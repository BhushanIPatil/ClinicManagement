"""
Payroll & HR API Endpoints

This module provides endpoints for payroll management. Employee payments
are stored in payments table with payment_type=EMPLOYEE_PAYROLL and payslip_id.
"""

import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import joinedload

from app.api.v1.deps import CurrentUserContext, get_current_user_context
from app.application.services.clinic_service import ClinicService
from app.core.database import db_manager
from app.infrastructure.database.models import Payroll, PayrollAssignment, Payslip, Payment, SalaryStructure, User

router = APIRouter(prefix="/payroll", tags=["Payroll"])


class RecordPayslipPaymentRequest(BaseModel):
    """Record an employee payroll payment for a payslip."""
    amount: Decimal = Field(..., gt=0)
    payment_method: str = Field("CASH", description="CASH, CARD, BANK_TRANSFER, etc.")
    payment_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    reference_number: Optional[str] = None
    notes: Optional[str] = None


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


class AddToRosterRequest(BaseModel):
    """Add an existing clinic user to payroll roster."""
    user_id: UUID
    joining_date: date
    role: str = Field(..., min_length=1, max_length=50)
    salary_structure_id: Optional[UUID] = None


class UpdateRosterRequest(BaseModel):
    """Update a payroll roster entry."""
    joining_date: Optional[date] = None
    role: Optional[str] = Field(None, min_length=1, max_length=50)
    salary_structure_id: Optional[UUID] = None
    payment_status: Optional[str] = Field(None, description="PENDING, PAID, PARTIAL")
    last_payment_date: Optional[date] = None


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


# --- Payroll roster (users on payroll for current user's clinic) ---


def _roster_item(a: PayrollAssignment, user: Optional[User] = None, salary: Optional[SalaryStructure] = None, updated_by_user: Optional[User] = None, created_by_user: Optional[User] = None) -> dict:
    fn = getattr(user, "first_name", None) or ""
    ln = getattr(user, "last_name", None) or ""
    name = f"{fn} {ln}".strip() or getattr(user, "username", None) or ""
    return {
        "id": str(a.id),
        "user_id": str(a.user_id),
        "user_name": name,
        "clinic_id": str(a.clinic_id),
        "joining_date": a.joining_date.isoformat() if a.joining_date else None,
        "role": a.role or "",
        "salary_structure_id": str(a.salary_structure_id) if a.salary_structure_id else None,
        "payment_status": a.payment_status or "PENDING",
        "last_payment_date": a.last_payment_date.isoformat() if a.last_payment_date else None,
        "base_salary": float(salary.base_salary) if salary else None,
        "gross_salary": float(salary.gross_salary) if salary else None,
        "net_salary": float(salary.net_salary) if salary else None,
        "created_at": a.created_at.isoformat() if getattr(a, "created_at", None) else None,
        "updated_at": a.updated_at.isoformat() if getattr(a, "updated_at", None) else None,
        "updated_by_id": str(a.updated_by_id) if a.updated_by_id else None,
        "updated_by_name": f"{getattr(updated_by_user, 'first_name', '') or ''} {getattr(updated_by_user, 'last_name', '') or ''}".strip() or getattr(updated_by_user, "username", None) if updated_by_user else None,
        "created_by_id": str(a.created_by_id) if a.created_by_id else None,
        "created_by_name": f"{getattr(created_by_user, 'first_name', '') or ''} {getattr(created_by_user, 'last_name', '') or ''}".strip() or getattr(created_by_user, "username", None) if created_by_user else None,
    }


@router.get("/clinic-users")
async def list_clinic_users_for_payroll(
    ctx: CurrentUserContext = Depends(get_current_user_context),
) -> Any:
    """List clinic users that can be added to payroll (existing users not already on roster)."""
    if not ctx.primary_clinic_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No clinic assigned")
    cid = UUID(ctx.primary_clinic_id)
    db = db_manager.get_session()
    try:
        clinic_svc = ClinicService(db)
        users = clinic_svc.list_users_for_clinic(cid)
        # Exclude users already in payroll roster for this clinic
        existing = (
            db.query(PayrollAssignment.user_id)
            .filter(
                PayrollAssignment.clinic_id == cid,
                PayrollAssignment.is_deleted == False,
            )
            .all()
        )
        existing_ids = {str(r[0]) for r in existing}
        out = [u for u in users if u.get("id") not in existing_ids]
        return {"items": out, "total": len(out)}
    finally:
        db.close()


@router.get("/roster")
async def list_roster(
    ctx: CurrentUserContext = Depends(get_current_user_context),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> Any:
    """List payroll roster (users on payroll) for current user's clinic. Includes updated_by and updated_at."""
    if not ctx.primary_clinic_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No clinic assigned")
    cid = UUID(ctx.primary_clinic_id)
    db = db_manager.get_session()
    try:
        q = (
            db.query(PayrollAssignment)
            .filter(
                PayrollAssignment.clinic_id == cid,
                PayrollAssignment.is_deleted == False,
            )
        )
        total = q.count()
        rows = (
            q.options(
                joinedload(PayrollAssignment.user),
                joinedload(PayrollAssignment.salary_structure),
                joinedload(PayrollAssignment.updated_by),
                joinedload(PayrollAssignment.created_by),
            )
            .order_by(PayrollAssignment.joining_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        items = [
            _roster_item(
                a,
                user=getattr(a, "user", None),
                salary=getattr(a, "salary_structure", None),
                updated_by_user=getattr(a, "updated_by", None),
                created_by_user=getattr(a, "created_by", None),
            )
            for a in rows
        ]
        return {"items": items, "total": total, "skip": skip, "limit": limit}
    finally:
        db.close()


@router.post("/roster", status_code=status.HTTP_201_CREATED)
async def add_to_roster(
    body: AddToRosterRequest,
    ctx: CurrentUserContext = Depends(get_current_user_context),
) -> Any:
    """Add an existing clinic user to the payroll roster. Sets created_by and updated_by to current user."""
    if not ctx.primary_clinic_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No clinic assigned")
    cid = UUID(ctx.primary_clinic_id)
    db = db_manager.get_session()
    try:
        # Ensure user is in clinic (e.g. via linked_clinics)
        clinic_svc = ClinicService(db)
        users = clinic_svc.list_users_for_clinic(cid)
        user_ids = {u.get("id") for u in users}
        if str(body.user_id) not in user_ids:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not in clinic")
        existing = (
            db.query(PayrollAssignment)
            .filter(
                PayrollAssignment.user_id == body.user_id,
                PayrollAssignment.clinic_id == cid,
                PayrollAssignment.is_deleted == False,
            )
            .first()
        )
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already on payroll roster")
        a = PayrollAssignment(
            user_id=body.user_id,
            clinic_id=cid,
            joining_date=body.joining_date,
            role=body.role,
            salary_structure_id=body.salary_structure_id,
            payment_status="PENDING",
            created_by_id=ctx.user_id,
            updated_by_id=ctx.user_id,
        )
        db.add(a)
        db.commit()
        db.refresh(a)
        # Reload with relationships for response
        a = (
            db.query(PayrollAssignment)
            .options(
                joinedload(PayrollAssignment.user),
                joinedload(PayrollAssignment.salary_structure),
                joinedload(PayrollAssignment.updated_by),
                joinedload(PayrollAssignment.created_by),
            )
            .filter(PayrollAssignment.id == a.id)
            .first()
        )
        return _roster_item(
            a,
            user=getattr(a, "user", None),
            salary=getattr(a, "salary_structure", None),
            updated_by_user=getattr(a, "updated_by", None),
            created_by_user=getattr(a, "created_by", None),
        )
    finally:
        db.close()


@router.put("/roster/{assignment_id}")
async def update_roster(
    assignment_id: str,
    body: UpdateRosterRequest,
    ctx: CurrentUserContext = Depends(get_current_user_context),
) -> Any:
    """Update a roster entry. Sets updated_by and updated_at to current user and now."""
    if not ctx.primary_clinic_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No clinic assigned")
    try:
        aid = UUID(assignment_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid assignment ID")
    cid = UUID(ctx.primary_clinic_id)
    db = db_manager.get_session()
    try:
        a = (
            db.query(PayrollAssignment)
            .options(
                joinedload(PayrollAssignment.user),
                joinedload(PayrollAssignment.salary_structure),
                joinedload(PayrollAssignment.updated_by),
                joinedload(PayrollAssignment.created_by),
            )
            .filter(
                PayrollAssignment.id == aid,
                PayrollAssignment.clinic_id == cid,
                PayrollAssignment.is_deleted == False,
            )
            .first()
        )
        if not a:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Roster entry not found")
        if body.joining_date is not None:
            a.joining_date = body.joining_date
        if body.role is not None:
            a.role = body.role
        if body.salary_structure_id is not None:
            a.salary_structure_id = body.salary_structure_id
        if body.payment_status is not None:
            a.payment_status = body.payment_status
        if body.last_payment_date is not None:
            a.last_payment_date = body.last_payment_date
        a.updated_by_id = ctx.user_id
        db.commit()
        db.refresh(a)
        a = (
            db.query(PayrollAssignment)
            .options(
                joinedload(PayrollAssignment.user),
                joinedload(PayrollAssignment.salary_structure),
                joinedload(PayrollAssignment.updated_by),
                joinedload(PayrollAssignment.created_by),
            )
            .filter(PayrollAssignment.id == a.id)
            .first()
        )
        return _roster_item(
            a,
            user=getattr(a, "user", None),
            salary=getattr(a, "salary_structure", None),
            updated_by_user=getattr(a, "updated_by", None),
            created_by_user=getattr(a, "created_by", None),
        )
    finally:
        db.close()


@router.delete("/roster/{assignment_id}")
async def remove_from_roster(
    assignment_id: str,
    ctx: CurrentUserContext = Depends(get_current_user_context),
) -> Any:
    """Remove user from payroll roster (soft delete)."""
    if not ctx.primary_clinic_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No clinic assigned")
    try:
        aid = UUID(assignment_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid assignment ID")
    cid = UUID(ctx.primary_clinic_id)
    db = db_manager.get_session()
    try:
        a = (
            db.query(PayrollAssignment)
            .filter(
                PayrollAssignment.id == aid,
                PayrollAssignment.clinic_id == cid,
                PayrollAssignment.is_deleted == False,
            )
            .first()
        )
        if not a:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Roster entry not found")
        a.is_deleted = True
        a.deleted_at = datetime.now(timezone.utc)
        db.commit()
        return {"message": "Removed from roster"}
    finally:
        db.close()


# --- Salary structures (by user, for roster) ---


class CreateSalaryStructureRequest(BaseModel):
    """Create a salary structure for a user (for payroll)."""
    user_id: UUID
    base_salary: Decimal = Field(..., ge=0)
    housing_allowance: Decimal = Field(0, ge=0)
    transport_allowance: Decimal = Field(0, ge=0)
    medical_allowance: Decimal = Field(0, ge=0)
    other_allowances: Decimal = Field(0, ge=0)
    tax_deduction: Decimal = Field(0, ge=0)
    insurance_deduction: Decimal = Field(0, ge=0)
    other_deductions: Decimal = Field(0, ge=0)
    notes: Optional[str] = None


def _salary_structure_item(s: SalaryStructure, user: Optional[User] = None) -> dict:
    fn = getattr(user, "first_name", None) or ""
    ln = getattr(user, "last_name", None) or ""
    name = f"{fn} {ln}".strip() or getattr(user, "username", None) if user else None
    return {
        "id": str(s.id),
        "user_id": str(s.user_id) if s.user_id else None,
        "user_name": name,
        "base_salary": float(s.base_salary or 0),
        "housing_allowance": float(s.housing_allowance or 0),
        "transport_allowance": float(s.transport_allowance or 0),
        "medical_allowance": float(s.medical_allowance or 0),
        "other_allowances": float(s.other_allowances or 0),
        "tax_deduction": float(s.tax_deduction or 0),
        "insurance_deduction": float(s.insurance_deduction or 0),
        "other_deductions": float(s.other_deductions or 0),
        "gross_salary": float(s.gross_salary or 0),
        "net_salary": float(s.net_salary or 0),
        "is_active": bool(s.is_active) if s.is_active is not None else True,
        "notes": s.notes,
    }


@router.get("/salary-structures")
async def list_salary_structures(
    ctx: CurrentUserContext = Depends(get_current_user_context),
    user_id: Optional[str] = Query(None, description="Filter by user"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> Any:
    """List salary structures, optionally for a user. For current user's clinic roster users."""
    db = db_manager.get_session()
    try:
        q = db.query(SalaryStructure).filter(SalaryStructure.is_deleted == False)
        if user_id:
            try:
                q = q.filter(SalaryStructure.user_id == UUID(user_id))
            except ValueError:
                pass
        total = q.count()
        rows = (
            q.options(joinedload(SalaryStructure.user))
            .order_by(SalaryStructure.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return {"items": [_salary_structure_item(r, getattr(r, "user", None)) for r in rows], "total": total, "skip": skip, "limit": limit}
    finally:
        db.close()


@router.post("/salary-structures", status_code=status.HTTP_201_CREATED)
async def create_salary_structure(
    body: CreateSalaryStructureRequest,
    ctx: CurrentUserContext = Depends(get_current_user_context),
) -> Any:
    """Create a salary structure for a user. Gross = base + allowances; net = gross - deductions."""
    db = db_manager.get_session()
    try:
        gross = (
            body.base_salary + body.housing_allowance + body.transport_allowance
            + body.medical_allowance + body.other_allowances
        )
        deductions = body.tax_deduction + body.insurance_deduction + body.other_deductions
        net = gross - deductions
        s = SalaryStructure(
            user_id=body.user_id,
            base_salary=body.base_salary,
            housing_allowance=body.housing_allowance,
            transport_allowance=body.transport_allowance,
            medical_allowance=body.medical_allowance,
            other_allowances=body.other_allowances,
            tax_deduction=body.tax_deduction,
            insurance_deduction=body.insurance_deduction,
            other_deductions=body.other_deductions,
            gross_salary=gross,
            net_salary=net,
            is_active=True,
            notes=body.notes,
        )
        db.add(s)
        db.commit()
        db.refresh(s)
        db.refresh(s)
        s = db.query(SalaryStructure).options(joinedload(SalaryStructure.user)).filter(SalaryStructure.id == s.id).first()
        return _salary_structure_item(s, getattr(s, "user", None))
    finally:
        db.close()


@router.get("/salary-structures/{structure_id}")
async def get_salary_structure(
    structure_id: str,
    ctx: CurrentUserContext = Depends(get_current_user_context),
) -> Any:
    """Get a salary structure by ID."""
    try:
        sid = UUID(structure_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID")
    db = db_manager.get_session()
    try:
        s = (
            db.query(SalaryStructure)
            .options(joinedload(SalaryStructure.user))
            .filter(SalaryStructure.id == sid, SalaryStructure.is_deleted == False)
            .first()
        )
        if not s:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Salary structure not found")
        return _salary_structure_item(s, getattr(s, "user", None))
    finally:
        db.close()


class GeneratePayslipsRequest(BaseModel):
    """Generate payslips for a payroll run from roster."""
    payroll_id: UUID


@router.post("/payslips/generate", status_code=status.HTTP_201_CREATED)
async def generate_payslips_from_roster(
    body: GeneratePayslipsRequest,
    ctx: CurrentUserContext = Depends(get_current_user_context),
) -> Any:
    """Generate one payslip per roster user for the given payroll run. Uses each assignment's salary structure."""
    if not ctx.primary_clinic_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No clinic assigned")
    cid = UUID(ctx.primary_clinic_id)
    db = db_manager.get_session()
    try:
        payroll = (
            db.query(Payroll)
            .filter(Payroll.id == body.payroll_id, Payroll.is_deleted == False)
            .first()
        )
        if not payroll:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payroll not found")
        if str(payroll.clinic_id) != ctx.primary_clinic_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Payroll not for your clinic")
        roster = (
            db.query(PayrollAssignment)
            .options(joinedload(PayrollAssignment.user), joinedload(PayrollAssignment.salary_structure))
            .filter(
                PayrollAssignment.clinic_id == cid,
                PayrollAssignment.is_deleted == False,
            )
            .all()
        )
        created = []
        for a in roster:
            salary = getattr(a, "salary_structure", None)
            base = float(salary.base_salary) if salary else 0
            gross = float(salary.gross_salary) if salary else base
            net = float(salary.net_salary) if salary else base
            total_allowances = (float(salary.housing_allowance or 0) + float(salary.transport_allowance or 0) + float(salary.medical_allowance or 0) + float(salary.other_allowances or 0)) if salary else 0
            total_deductions = (float(salary.tax_deduction or 0) + float(salary.insurance_deduction or 0) + float(salary.other_deductions or 0)) if salary else 0
            ps_num = f"PS-{uuid.uuid4().hex[:8].upper()}"
            ps = Payslip(
                payslip_number=ps_num,
                payroll_id=payroll.id,
                user_id=a.user_id,
                base_salary=Decimal(str(base)),
                total_allowances=Decimal(str(total_allowances)),
                total_deductions=Decimal(str(total_deductions)),
                gross_salary=Decimal(str(gross)),
                net_salary=Decimal(str(net)),
                status="GENERATED",
            )
            db.add(ps)
            created.append(ps_num)
        db.commit()
        return {"message": "Payslips generated", "count": len(created), "payslip_numbers": created}
    finally:
        db.close()


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


def _payslip_item(ps: Payslip, payroll: Optional[Payroll] = None, user: Optional[User] = None) -> dict:
    p = payroll or getattr(ps, "payroll", None)
    fn = getattr(user, "first_name", None) or ""
    ln = getattr(user, "last_name", None) or ""
    user_name = f"{fn} {ln}".strip() or getattr(user, "username", None) if user else None
    return {
        "id": str(ps.id),
        "payslip_number": ps.payslip_number or "",
        "payroll_id": str(ps.payroll_id) if ps.payroll_id else None,
        "payroll_number": p.payroll_number if p else None,
        "period_start": p.period_start.isoformat() if p and p.period_start else None,
        "period_end": p.period_end.isoformat() if p and p.period_end else None,
        "employee_id": str(ps.employee_id) if ps.employee_id else None,
        "user_id": str(ps.user_id) if ps.user_id else None,
        "user_name": user_name,
        "base_salary": float(ps.base_salary or 0),
        "gross_salary": float(ps.gross_salary or 0),
        "net_salary": float(ps.net_salary or 0),
        "status": ps.status or "GENERATED",
        "notes": ps.notes,
    }


@router.get("/payslips")
async def list_payslips(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    payroll_id: Optional[str] = None,
    clinic_id: Optional[str] = None,
    status: Optional[str] = None,
) -> Any:
    """List payslips with optional filters."""
    db = db_manager.get_session()
    try:
        q = (
            db.query(Payslip)
            .join(Payroll, Payslip.payroll_id == Payroll.id)
            .filter(Payslip.is_deleted == False, Payroll.is_deleted == False)
        )
        if payroll_id:
            try:
                q = q.filter(Payslip.payroll_id == UUID(payroll_id))
            except ValueError:
                pass
        if clinic_id:
            try:
                q = q.filter(Payroll.clinic_id == UUID(clinic_id))
            except ValueError:
                pass
        if status:
            q = q.filter(Payslip.status == status)
        total = q.count()
        rows = (
            q.options(joinedload(Payslip.payroll), joinedload(Payslip.user))
            .order_by(Payroll.period_end.desc(), Payslip.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return {"items": [_payslip_item(r, user=getattr(r, "user", None)) for r in rows], "total": total, "skip": skip, "limit": limit}
    finally:
        db.close()


@router.post("/payslips/{payslip_id}/payments", status_code=status.HTTP_201_CREATED)
async def record_payslip_payment(payslip_id: str, body: RecordPayslipPaymentRequest) -> Any:
    """Record an employee payroll payment for a payslip. Stored in payments table with payment_type=EMPLOYEE_PAYROLL."""
    try:
        psid = UUID(payslip_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payslip ID")
    db = db_manager.get_session()
    try:
        ps = (
            db.query(Payslip)
            .options(joinedload(Payslip.payroll))
            .filter(Payslip.id == psid, Payslip.is_deleted == False)
            .first()
        )
        if not ps:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payslip not found")
        clinic_id = ps.payroll.clinic_id if ps.payroll else None
        pm_num = f"PAY-{uuid.uuid4().hex[:8].upper()}"
        pm = Payment(
            payment_number=pm_num,
            payment_type="EMPLOYEE_PAYROLL",
            payment_date=body.payment_date,
            amount=body.amount,
            payment_method=body.payment_method or "CASH",
            status="COMPLETED",
            reference_number=body.reference_number,
            notes=body.notes,
            payslip_id=ps.id,
            clinic_id=clinic_id,
        )
        db.add(pm)
        ps.status = "PAID"
        db.commit()
        db.refresh(pm)
        return {
            "id": str(pm.id),
            "payment_number": pm_num,
            "amount": float(pm.amount or 0),
            "payment_method": body.payment_method or "CASH",
            "payment_date": pm.payment_date.isoformat() if pm.payment_date else None,
        }
    finally:
        db.close()


@router.get("/stats/summary")
async def get_payroll_summary() -> Any:
    """Get payroll summary statistics."""
    return {
        "total_employees": 0,
        "total_payroll": 0,
        "pending_payslips": 0,
        "average_salary": 0
    }
