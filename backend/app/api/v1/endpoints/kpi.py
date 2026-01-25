"""
KPI & Targets API Endpoints

This module provides endpoints for key performance indicators.
"""

from calendar import monthrange
from datetime import date, datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field
from uuid import UUID
from sqlalchemy import func
from typing import Any, Optional

from app.core.database import db_manager
from app.infrastructure.database.models import (
    Patient,
    Appointment,
    Payment,
    Doctor,
    WorkQueue,
    Target,
)

router = APIRouter(prefix="/kpi", tags=["KPI & Analytics"])


def _utc_today_start() -> datetime:
    n = datetime.now(timezone.utc)
    return n.replace(hour=0, minute=0, second=0, microsecond=0)


def _zero(value: Any) -> float:
    if value is None:
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _int(value: Any) -> int:
    if value is None:
        return 0
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


class CreateTargetRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    target_type: str = Field(..., description="REVENUE, PATIENTS, APPOINTMENTS, etc.")
    target_value: float = Field(..., ge=0)
    current_value: float = Field(0, ge=0)
    unit: Optional[str] = Field("COUNT", description="COUNT, CURRENCY, PERCENTAGE")
    period_start: date
    period_end: date
    status: str = Field("IN_PROGRESS", description="IN_PROGRESS, ACHIEVED, MISSED")
    department_id: Optional[UUID] = None
    assigned_to_id: Optional[UUID] = None


class UpdateTargetRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    target_value: Optional[float] = Field(None, ge=0)
    current_value: Optional[float] = Field(None, ge=0)
    unit: Optional[str] = None
    status: Optional[str] = None
    assigned_to_id: Optional[UUID] = None


def _target_item(t: Target) -> dict:
    return {
        "id": str(t.id),
        "name": t.name or "",
        "description": t.description,
        "target_type": t.target_type or "",
        "target_value": float(t.target_value) if t.target_value is not None else 0,
        "current_value": float(t.current_value) if t.current_value is not None else 0,
        "unit": t.unit,
        "period_start": t.period_start.isoformat() if getattr(t, "period_start", None) else None,
        "period_end": t.period_end.isoformat() if getattr(t, "period_end", None) else None,
        "status": t.status or "IN_PROGRESS",
        "department_id": str(t.department_id) if getattr(t, "department_id", None) else None,
        "assigned_to_id": str(t.assigned_to_id) if getattr(t, "assigned_to_id", None) else None,
        "progress": (float(t.current_value) / float(t.target_value) * 100) if t.target_value and float(t.target_value) != 0 else 0,
    }


@router.get("/targets")
async def list_targets(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
) -> Any:
    """List KPI targets with filtering."""
    db = db_manager.get_session()
    try:
        q = db.query(Target).filter(Target.is_deleted == False)
        if status:
            q = q.filter(Target.status == status)
        total = q.count()
        rows = q.order_by(Target.period_end.desc()).offset(skip).limit(limit).all()
        return {"items": [_target_item(r) for r in rows], "total": total, "skip": skip, "limit": limit}
    finally:
        db.close()


@router.get("/targets/{target_id}")
async def get_target(target_id: str) -> Any:
    """Get target by ID."""
    try:
        tid = UUID(target_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid target ID")
    db = db_manager.get_session()
    try:
        t = db.query(Target).filter(Target.id == tid, Target.is_deleted == False).first()
        if not t:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target not found")
        return _target_item(t)
    finally:
        db.close()


@router.post("/targets", status_code=status.HTTP_201_CREATED)
async def create_target(body: CreateTargetRequest) -> Any:
    """Create a new KPI target."""
    db = db_manager.get_session()
    try:
        t = Target(
            name=body.name,
            description=body.description,
            target_type=body.target_type,
            target_value=body.target_value,
            current_value=body.current_value or 0,
            unit=body.unit or "COUNT",
            period_start=body.period_start,
            period_end=body.period_end,
            status=body.status or "IN_PROGRESS",
            department_id=body.department_id,
            assigned_to_id=body.assigned_to_id,
        )
        db.add(t)
        db.commit()
        db.refresh(t)
        return _target_item(t)
    finally:
        db.close()


@router.put("/targets/{target_id}")
async def update_target(target_id: str, body: UpdateTargetRequest) -> Any:
    """Update a KPI target."""
    try:
        tid = UUID(target_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid target ID")
    db = db_manager.get_session()
    try:
        t = db.query(Target).filter(Target.id == tid, Target.is_deleted == False).first()
        if not t:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target not found")
        if body.name is not None:
            t.name = body.name
        if body.description is not None:
            t.description = body.description
        if body.target_value is not None:
            t.target_value = body.target_value
        if body.current_value is not None:
            t.current_value = body.current_value
        if body.unit is not None:
            t.unit = body.unit
        if body.status is not None:
            t.status = body.status
        if body.assigned_to_id is not None:
            t.assigned_to_id = body.assigned_to_id
        db.commit()
        db.refresh(t)
        return _target_item(t)
    finally:
        db.close()


@router.delete("/targets/{target_id}")
async def delete_target(target_id: str) -> Any:
    """Soft-delete a KPI target."""
    try:
        tid = UUID(target_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid target ID")
    db = db_manager.get_session()
    try:
        t = db.query(Target).filter(Target.id == tid, Target.is_deleted == False).first()
        if not t:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target not found")
        t.soft_delete()
        db.commit()
        return {"id": target_id, "deleted": True}
    finally:
        db.close()


@router.get("/dashboard")
async def get_dashboard_data() -> Any:
    """Get dashboard KPI data from database. All numbers and arrays are non-null."""
    db = db_manager.get_session()
    try:
        today_start = _utc_today_start()
        today_end = today_start + timedelta(days=1)
        month_start = today_start.replace(day=1)

        # KPIs: always int/float, never null
        total_patients = _int(
            db.query(func.count(Patient.id))
            .filter(Patient.is_deleted == False)
            .scalar()
        )
        appointments_today = _int(
            db.query(func.count(Appointment.id))
            .filter(
                Appointment.is_deleted == False,
                Appointment.appointment_date >= today_start,
                Appointment.appointment_date < today_end,
            )
            .scalar()
        )
        revenue_today_val = db.query(func.coalesce(func.sum(Payment.amount), 0)).filter(
            Payment.is_deleted == False,
            Payment.status == "COMPLETED",
            Payment.payment_date >= today_start,
            Payment.payment_date < today_end,
        ).scalar()
        revenue_today = _zero(revenue_today_val)
        active_doctors = _int(
            db.query(func.count(Doctor.id))
            .filter(Doctor.is_deleted == False, Doctor.is_available == True)
            .scalar()
        )

        # Last 7 days for revenueData
        revenue_data = []
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i in range(7):
            d = today_start - timedelta(days=6 - i)
            day_end = d + timedelta(days=1)
            rev = db.query(func.coalesce(func.sum(Payment.amount), 0)).filter(
                Payment.is_deleted == False,
                Payment.status == "COMPLETED",
                Payment.payment_date >= d,
                Payment.payment_date < day_end,
            ).scalar()
            cnt = _int(
                db.query(func.count(Appointment.id))
                .filter(
                    Appointment.is_deleted == False,
                    Appointment.appointment_date >= d,
                    Appointment.appointment_date < day_end,
                )
                .scalar()
            )
            revenue_data.append({
                "date": day_names[d.weekday()],
                "revenue": _zero(rev),
                "patients": cnt,
            })

        # Last 7 days for appointmentsData (scheduled vs completed)
        appointments_data = []
        for i in range(7):
            d = today_start - timedelta(days=6 - i)
            day_end = d + timedelta(days=1)
            scheduled = _int(
                db.query(func.count(Appointment.id))
                .filter(
                    Appointment.is_deleted == False,
                    Appointment.appointment_date >= d,
                    Appointment.appointment_date < day_end,
                )
                .scalar()
            )
            completed = _int(
                db.query(func.count(Appointment.id))
                .filter(
                    Appointment.is_deleted == False,
                    Appointment.status == "COMPLETED",
                    Appointment.appointment_date >= d,
                    Appointment.appointment_date < day_end,
                )
                .scalar()
            )
            appointments_data.append({
                "day": day_names[d.weekday()],
                "scheduled": scheduled,
                "completed": completed,
            })

        # Last 6 months for patientTrendData (new patients in month, returning = appointments in month)
        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        patient_trend_data = []
        for i in range(6):
            target_month = today_start.month - (5 - i)
            target_year = today_start.year
            while target_month < 1:
                target_month += 12
                target_year -= 1
            m_start = today_start.replace(year=target_year, month=target_month, day=1)
            _, last_day = monthrange(target_year, target_month)
            m_end = m_start.replace(day=last_day) + timedelta(days=1)
            new_p = _int(
                db.query(func.count(Patient.id))
                .filter(
                    Patient.is_deleted == False,
                    Patient.created_at >= m_start,
                    Patient.created_at < m_end,
                )
                .scalar()
            )
            ret = _int(
                db.query(func.count(Appointment.id))
                .filter(
                    Appointment.is_deleted == False,
                    Appointment.appointment_date >= m_start,
                    Appointment.appointment_date < m_end,
                )
                .scalar()
            )
            patient_trend_data.append({
                "month": month_names[target_month - 1],
                "new": new_p,
                "returning": ret,
            })

        return {
            "kpis": {
                "totalPatients": total_patients,
                "appointmentsToday": appointments_today,
                "revenueToday": revenue_today,
                "activeDoctors": active_doctors,
            },
            "revenueData": revenue_data or [],
            "appointmentsData": appointments_data or [],
            "patientTrendData": patient_trend_data or [],
        }
    finally:
        db.close()


@router.get("/analytics/trends")
async def get_analytics_trends(
    metric: str = Query(..., description="Metric to analyze"),
    period: str = Query("month", pattern="^(week|month|quarter|year)$"),
) -> Any:
    """Get trend analytics for a specific metric."""
    return {
        "metric": metric,
        "period": period,
        "data": [],
        "trend": "stable",
    }


@router.get("/stats/summary")
async def get_kpi_summary() -> Any:
    """Get KPI summary statistics."""
    return {
        "total_targets": 0,
        "achieved": 0,
        "in_progress": 0,
        "missed": 0,
        "achievement_rate": 0,
    }
