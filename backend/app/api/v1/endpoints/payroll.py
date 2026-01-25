"""
Payroll & HR API Endpoints

This module provides endpoints for payroll management.
"""

import uuid
from datetime import date
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.core.database import db_manager
from app.infrastructure.database.models import Payroll

router = APIRouter(prefix="/payroll", tags=["Payroll"])


class CreatePayrollRequest(BaseModel):
    period_start: date
    period_end: date
    pay_date: Optional[date] = None
    status: str = Field("DRAFT", description="DRAFT, PROCESSING, COMPLETED, CANCELLED")
    clinic_id: Optional[UUID] = None
    notes: Optional[str] = None


class UpdatePayrollRequest(BaseModel):
    pay_date: Optional[date] = None
    status: Optional[str] = None
    total_gross: Optional[Decimal] = None
    total_deductions: Optional[Decimal] = None
    total_net: Optional[Decimal] = None
    employee_count: Optional[int] = None
    notes: Optional[str] = None


def _payroll_item(p: Payroll) -> dict:
    return {
        "id": str(p.id),
        "payroll_number": (p.payroll_number or ""),
        "period_start": p.period_start.isoformat() if p.period_start else None,
        "period_end": p.period_end.isoformat() if p.period_end else None,
        "pay_date": p.pay_date.isoformat() if p.pay_date else None,
        "status": p.status or "DRAFT",
        "total_gross": float(p.total_gross) if p.total_gross is not None else 0,
        "total_deductions": float(p.total_deductions) if p.total_deductions is not None else 0,
        "total_net": float(p.total_net) if p.total_net is not None else 0,
        "employee_count": int(p.employee_count) if p.employee_count is not None else 0,
        "clinic_id": str(p.clinic_id) if p.clinic_id else None,
        "notes": p.notes,
        "created_at": p.created_at.isoformat() if getattr(p, "created_at", None) else None,
        "updated_at": p.updated_at.isoformat() if getattr(p, "updated_at", None) else None,
    }


@router.get("/runs")
async def list_payrolls(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    clinic_id: Optional[str] = None,
) -> Any:
    """List payroll runs with pagination."""
    db = db_manager.get_session()
    try:
        q = db.query(Payroll).filter(Payroll.is_deleted == False)
        if status:
            q = q.filter(Payroll.status == status)
        if clinic_id:
            try:
                q = q.filter(Payroll.clinic_id == UUID(clinic_id))
            except ValueError:
                pass
        total = q.count()
        rows = q.order_by(Payroll.period_end.desc()).offset(skip).limit(limit).all()
        return {"items": [_payroll_item(p) for p in rows], "total": total, "skip": skip, "limit": limit}
    finally:
        db.close()


@router.post("/runs", status_code=status.HTTP_201_CREATED)
async def create_payroll(body: CreatePayrollRequest) -> Any:
    """Create a new payroll run."""
    db = db_manager.get_session()
    try:
        pn = f"PAY-{uuid.uuid4().hex[:8].upper()}"
        p = Payroll(
            payroll_number=pn,
            period_start=body.period_start,
            period_end=body.period_end,
            pay_date=body.pay_date,
            status=body.status or "DRAFT",
            clinic_id=body.clinic_id,
            notes=body.notes,
            total_gross=Decimal("0"),
            total_deductions=Decimal("0"),
            total_net=Decimal("0"),
            employee_count=0,
        )
        db.add(p)
        db.commit()
        db.refresh(p)
        return _payroll_item(p)
    finally:
        db.close()


@router.get("/runs/{payroll_id}")
async def get_payroll(payroll_id: str) -> Any:
    """Get payroll run by ID."""
    try:
        pid = UUID(payroll_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payroll ID")
    db = db_manager.get_session()
    try:
        p = db.query(Payroll).filter(Payroll.id == pid, Payroll.is_deleted == False).first()
        if not p:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payroll not found")
        return _payroll_item(p)
    finally:
        db.close()


@router.put("/runs/{payroll_id}")
async def update_payroll(payroll_id: str, body: UpdatePayrollRequest) -> Any:
    """Update a payroll run."""
    try:
        pid = UUID(payroll_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payroll ID")
    db = db_manager.get_session()
    try:
        p = db.query(Payroll).filter(Payroll.id == pid, Payroll.is_deleted == False).first()
        if not p:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payroll not found")
        if body.pay_date is not None:
            p.pay_date = body.pay_date
        if body.status is not None:
            p.status = body.status
        if body.total_gross is not None:
            p.total_gross = body.total_gross
        if body.total_deductions is not None:
            p.total_deductions = body.total_deductions
        if body.total_net is not None:
            p.total_net = body.total_net
        if body.employee_count is not None:
            p.employee_count = body.employee_count
        if body.notes is not None:
            p.notes = body.notes
        db.commit()
        db.refresh(p)
        return _payroll_item(p)
    finally:
        db.close()


@router.get("/employees")
async def list_employees(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    department: Optional[str] = None,
) -> Any:
    """List employees with filtering."""
    return {
        "items": [],
        "total": 0,
        "skip": skip,
        "limit": limit
    }


@router.get("/employees/{employee_id}")
async def get_employee(employee_id: str) -> Any:
    """Get employee by ID."""
    return {"id": employee_id, "name": "Employee"}


@router.get("/attendance")
async def list_attendance(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    employee_id: Optional[str] = None,
) -> Any:
    """List attendance records."""
    return {
        "items": [],
        "total": 0
    }


@router.post("/attendance")
async def record_attendance() -> Any:
    """Record employee attendance."""
    return {"message": "Attendance recording - to be implemented"}


@router.get("/payslips")
async def list_payslips(
    period: Optional[str] = None,
    employee_id: Optional[str] = None,
) -> Any:
    """List payslips."""
    return {
        "items": [],
        "total": 0
    }


@router.post("/payslips/generate")
async def generate_payslips() -> Any:
    """Generate payslips for a period."""
    return {"message": "Payslip generation - to be implemented"}


@router.get("/stats/summary")
async def get_payroll_summary() -> Any:
    """Get payroll summary statistics."""
    return {
        "total_employees": 0,
        "total_payroll": 0,
        "pending_payslips": 0,
        "average_salary": 0
    }
