"""
Dashboard Service

Optimized service for role-based dashboard data with real-time stats,
summary counts, and trend data. Cache-friendly and fast response.
"""

import asyncio
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select, func, and_, or_, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db

from app.infrastructure.database.models.appointment import Appointment
from app.infrastructure.database.models.patient import Patient
from app.infrastructure.database.models.payment import Payment
from app.infrastructure.database.models.work_queue import WorkQueue
from app.infrastructure.database.models.doctor import Doctor
from app.infrastructure.database.models.financial_transaction import FinancialTransaction

from app.application.dto.dashboard_dto import (
    AdminDashboardDTO,
    DoctorDashboardDTO,
    NurseDashboardDTO,
    ReceptionistDashboardDTO,
    AccountantDashboardDTO,
    HRDashboardDTO,
    StatCardDTO,
    TrendPointDTO,
    TrendWidgetDTO,
    SummaryCountDTO,
    DashboardWidgetDTO,
)


def _date_start(d: date) -> datetime:
    """Convert date to start of day datetime."""
    return datetime.combine(d, datetime.min.time())


def _date_end(d: date) -> datetime:
    """Convert date to end of day datetime."""
    return datetime.combine(d, datetime.max.time())


def _calculate_change(current: int | Decimal, previous: int | Decimal) -> Optional[float]:
    """Calculate percentage change."""
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    return float(((current - previous) / previous) * 100)


def _get_trend(change: Optional[float]) -> Optional[str]:
    """Get trend direction from change percentage."""
    if change is None:
        return None
    if change > 0:
        return "UP"
    elif change < 0:
        return "DOWN"
    return "STABLE"


class DashboardService:
    """Dashboard service for role-based dashboard data."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_admin_dashboard(self) -> AdminDashboardDTO:
        """Get admin dashboard with comprehensive stats."""
        now = datetime.utcnow()
        today = now.date()
        yesterday = today - timedelta(days=1)
        last_week = today - timedelta(days=7)
        last_month = today - timedelta(days=30)
        this_month_start = date(today.year, today.month, 1)
        last_month_start = date(today.year, today.month - 1, 1) if today.month > 1 else date(today.year - 1, 12, 1)

        # Execute queries (can be parallelized in future)
        total_patients = await self._get_total_patients()
        appointments_today = await self._get_total_appointments_today()
        revenue_today = await self._get_total_revenue_today()
        pending_payments = await self._get_pending_payments_count()
        active_doctors = await self._get_active_doctors()
        pending_queue = await self._get_pending_work_queue()
        
        # Get previous period stats for comparison
        prev_appointments = await self._get_total_appointments_date(yesterday)
        prev_revenue = await self._get_total_revenue_date(yesterday)

        # Build stats
        stats = {
            "total_patients": StatCardDTO(
                title="Total Patients",
                value=total_patients,
                icon="users",
                color="blue"
            ),
            "appointments_today": StatCardDTO(
                title="Appointments Today",
                value=appointments_today,
                change=_calculate_change(appointments_today, prev_appointments),
                trend=_get_trend(_calculate_change(appointments_today, prev_appointments)),
                icon="calendar",
                color="green"
            ),
            "revenue_today": StatCardDTO(
                title="Revenue Today",
                value=revenue_today,
                change=_calculate_change(revenue_today, prev_revenue),
                trend=_get_trend(_calculate_change(revenue_today, prev_revenue)),
                icon="dollar-sign",
                color="green"
            ),
            "pending_payments": StatCardDTO(
                title="Pending Payments",
                value=pending_payments,
                icon="file-text",
                color="orange"
            ),
            "active_doctors": StatCardDTO(
                title="Active Doctors",
                value=active_doctors,
                icon="user-md",
                color="blue"
            ),
            "pending_queue": StatCardDTO(
                title="Pending Tasks",
                value=pending_queue,
                icon="list",
                color="red"
            ),
        }

        # Summary counts
        summary_counts = [
            SummaryCountDTO(label="Total Appointments", count=await self._get_total_appointments_month(this_month_start), icon="calendar"),
            SummaryCountDTO(label="Total Revenue", count=await self._get_total_revenue_month(this_month_start), icon="dollar-sign"),
            SummaryCountDTO(label="New Patients", count=await self._get_new_patients_month(this_month_start), icon="user-plus"),
            SummaryCountDTO(label="Completed Appointments", count=await self._get_completed_appointments_month(this_month_start), icon="check-circle"),
        ]

        # Trends (last 7 days)
        trends = [
            await self._get_appointments_trend(last_week, today),
            await self._get_revenue_trend(last_week, today),
        ]

        # Widgets
        widgets = [
            DashboardWidgetDTO(
                id="recent_appointments",
                type="TABLE",
                title="Recent Appointments",
                data={"items": await self._get_recent_appointments(10)},
                position=1,
                size="LARGE"
            ),
            DashboardWidgetDTO(
                id="revenue_chart",
                type="TREND_CHART",
                title="Revenue Trend",
                data={"trend": trends[1].dict()},
                position=2,
                size="MEDIUM"
            ),
        ]

        return AdminDashboardDTO(
            role="ADMIN",
            generated_at=now,
            widgets=widgets,
            stats=stats,
            summary_counts=summary_counts,
            trends=trends
        )

    async def get_doctor_dashboard(self, doctor_id: UUID) -> DoctorDashboardDTO:
        """Get doctor-specific dashboard."""
        now = datetime.utcnow()
        today = now.date()
        yesterday = today - timedelta(days=1)
        this_week_start = today - timedelta(days=today.weekday())

        # Doctor-specific stats
        appointments_today = await self._get_doctor_appointments_today(doctor_id)
        appointments_yesterday = await self._get_doctor_appointments_date(doctor_id, yesterday)
        patients_today = await self._get_doctor_patients_today(doctor_id)
        upcoming_appointments = await self._get_doctor_upcoming_appointments(doctor_id, 5)

        stats = {
            "appointments_today": StatCardDTO(
                title="Appointments Today",
                value=appointments_today,
                change=_calculate_change(appointments_today, appointments_yesterday),
                trend=_get_trend(_calculate_change(appointments_today, appointments_yesterday)),
                icon="calendar",
                color="blue"
            ),
            "patients_today": StatCardDTO(
                title="Patients Today",
                value=patients_today,
                icon="users",
                color="green"
            ),
        }

        summary_counts = [
            SummaryCountDTO(label="This Week", count=await self._get_doctor_appointments_week(doctor_id, this_week_start), icon="calendar"),
            SummaryCountDTO(label="This Month", count=await self._get_doctor_appointments_month(doctor_id, date(today.year, today.month, 1)), icon="calendar"),
        ]

        trends = [
            await self._get_doctor_appointments_trend(doctor_id, this_week_start, today),
        ]

        widgets = [
            DashboardWidgetDTO(
                id="upcoming_appointments",
                type="TABLE",
                title="Upcoming Appointments",
                data={"items": upcoming_appointments},
                position=1,
                size="LARGE"
            ),
        ]

        return DoctorDashboardDTO(
            role="DOCTOR",
            generated_at=now,
            doctor_id=doctor_id,
            widgets=widgets,
            stats=stats,
            summary_counts=summary_counts,
            trends=trends
        )

    async def get_nurse_dashboard(self) -> NurseDashboardDTO:
        """Get nurse dashboard."""
        now = datetime.utcnow()
        today = now.date()

        stats = {
            "patients_today": StatCardDTO(
                title="Patients Today",
                value=await self._get_total_patients_today(),
                icon="users",
                color="blue"
            ),
            "pending_tasks": StatCardDTO(
                title="Pending Tasks",
                value=await self._get_pending_work_queue(),
                icon="list",
                color="orange"
            ),
        }

        summary_counts = [
            SummaryCountDTO(label="Today's Appointments", count=await self._get_total_appointments_today(), icon="calendar"),
        ]

        trends = []

        widgets = []

        return NurseDashboardDTO(
            role="NURSE",
            generated_at=now,
            widgets=widgets,
            stats=stats,
            summary_counts=summary_counts,
            trends=trends
        )

    async def get_receptionist_dashboard(self) -> ReceptionistDashboardDTO:
        """Get receptionist dashboard."""
        now = datetime.utcnow()
        today = now.date()

        stats = {
            "appointments_today": StatCardDTO(
                title="Appointments Today",
                value=await self._get_total_appointments_today(),
                icon="calendar",
                color="blue"
            ),
            "new_patients_today": StatCardDTO(
                title="New Patients Today",
                value=await self._get_new_patients_today(),
                icon="user-plus",
                color="green"
            ),
            "pending_queue": StatCardDTO(
                title="Pending Tasks",
                value=await self._get_pending_work_queue(),
                icon="list",
                color="orange"
            ),
        }

        summary_counts = [
            SummaryCountDTO(label="Upcoming Appointments", count=await self._get_upcoming_appointments(10), icon="calendar"),
        ]

        trends = []

        widgets = [
            DashboardWidgetDTO(
                id="today_appointments",
                type="TABLE",
                title="Today's Appointments",
                data={"items": await self._get_today_appointments()},
                position=1,
                size="LARGE"
            ),
        ]

        return ReceptionistDashboardDTO(
            role="RECEPTIONIST",
            generated_at=now,
            widgets=widgets,
            stats=stats,
            summary_counts=summary_counts,
            trends=trends
        )

    async def get_accountant_dashboard(self) -> AccountantDashboardDTO:
        """Get accountant dashboard."""
        now = datetime.utcnow()
        today = now.date()
        this_month_start = date(today.year, today.month, 1)

        stats = {
            "revenue_today": StatCardDTO(
                title="Revenue Today",
                value=await self._get_total_revenue_today(),
                icon="dollar-sign",
                color="green"
            ),
            "pending_payments": StatCardDTO(
                title="Pending Payments",
                value=await self._get_pending_payments_count(),
                icon="file-text",
                color="orange"
            ),
            "total_revenue_month": StatCardDTO(
                title="Monthly Revenue",
                value=await self._get_total_revenue_month(this_month_start),
                icon="dollar-sign",
                color="blue"
            ),
        }

        summary_counts = [
            SummaryCountDTO(label="Paid Payments (month)", count=await self._get_paid_payments_month(this_month_start), icon="check"),
            SummaryCountDTO(label="Pending Payments", count=await self._get_pending_payments_count(), icon="clock"),
        ]

        trends = [
            await self._get_revenue_trend(today - timedelta(days=30), today),
        ]

        widgets = [
            DashboardWidgetDTO(
                id="recent_payments",
                type="TABLE",
                title="Recent Payments",
                data={"items": await self._get_recent_payments(10)},
                position=1,
                size="LARGE"
            ),
        ]

        return AccountantDashboardDTO(
            role="ACCOUNTANT",
            generated_at=now,
            widgets=widgets,
            stats=stats,
            summary_counts=summary_counts,
            trends=trends
        )

    async def get_hr_dashboard(self) -> HRDashboardDTO:
        """Get HR dashboard."""
        now = datetime.utcnow()
        today = now.date()

        stats = {
            "total_employees": StatCardDTO(
                title="Total Employees",
                value=await self._get_total_employees(),
                icon="users",
                color="blue"
            ),
            "active_doctors": StatCardDTO(
                title="Active Doctors",
                value=await self._get_active_doctors(),
                icon="user-md",
                color="green"
            ),
        }

        summary_counts = [
            SummaryCountDTO(label="Total Staff", count=await self._get_total_employees(), icon="users"),
        ]

        trends = []

        widgets = []

        return HRDashboardDTO(
            role="HR",
            generated_at=now,
            widgets=widgets,
            stats=stats,
            summary_counts=summary_counts,
            trends=trends
        )

    # Helper methods for database queries

    async def _get_total_patients(self) -> int:
        """Get total patients count."""
        result = await self.db.execute(
            select(func.count(Patient.id)).where(Patient.is_deleted == False)
        )
        return result.scalar() or 0

    async def _get_total_appointments_today(self) -> int:
        """Get total appointments today."""
        today = datetime.utcnow().date()
        result = await self.db.execute(
            select(func.count(Appointment.id)).where(
                and_(
                    func.cast(Appointment.appointment_date, text).like(f"{today}%"),
                    Appointment.is_deleted == False
                )
            )
        )
        return result.scalar() or 0

    async def _get_total_appointments_date(self, d: date) -> int:
        """Get appointments for a specific date."""
        result = await self.db.execute(
            select(func.count(Appointment.id)).where(
                and_(
                    func.cast(Appointment.appointment_date, text).like(f"{d}%"),
                    Appointment.is_deleted == False
                )
            )
        )
        return result.scalar() or 0

    async def _get_total_revenue_today(self) -> Decimal:
        """Get total revenue today."""
        today = datetime.utcnow().date()
        result = await self.db.execute(
            select(func.sum(Payment.amount)).where(
                and_(
                    func.cast(Payment.payment_date, text).like(f"{today}%"),
                    Payment.is_deleted == False,
                    Payment.status == "COMPLETED"
                )
            )
        )
        return Decimal(str(result.scalar() or 0))

    async def _get_total_revenue_date(self, d: date) -> Decimal:
        """Get revenue for a specific date."""
        result = await self.db.execute(
            select(func.sum(Payment.amount)).where(
                and_(
                    func.cast(Payment.payment_date, text).like(f"{d}%"),
                    Payment.is_deleted == False,
                    Payment.status == "COMPLETED"
                )
            )
        )
        return Decimal(str(result.scalar() or 0))

    async def _get_pending_payments_count(self) -> int:
        """Get pending payments count."""
        result = await self.db.execute(
            select(func.count(Payment.id)).where(
                and_(
                    Payment.status.in_(["PENDING", "PROCESSING"]),
                    Payment.is_deleted == False
                )
            )
        )
        return result.scalar() or 0

    async def _get_active_doctors(self) -> int:
        """Get active doctors count (employees table removed; count doctors only)."""
        result = await self.db.execute(
            select(func.count(Doctor.id)).where(Doctor.is_deleted == False)
        )
        return result.scalar() or 0

    async def _get_pending_work_queue(self) -> int:
        """Get pending work queue items."""
        result = await self.db.execute(
            select(func.count(WorkQueue.id)).where(
                and_(
                    WorkQueue.status.in_(["PENDING", "IN_PROGRESS"]),
                    WorkQueue.is_deleted == False
                )
            )
        )
        return result.scalar() or 0

    async def _get_total_appointments_month(self, month_start: date) -> int:
        """Get total appointments for month."""
        month_end = date(month_start.year, month_start.month + 1, 1) - timedelta(days=1) if month_start.month < 12 else date(month_start.year + 1, 1, 1) - timedelta(days=1)
        result = await self.db.execute(
            select(func.count(Appointment.id)).where(
                and_(
                    func.cast(Appointment.appointment_date, text) >= str(month_start),
                    func.cast(Appointment.appointment_date, text) <= str(month_end),
                    Appointment.is_deleted == False
                )
            )
        )
        return result.scalar() or 0

    async def _get_total_revenue_month(self, month_start: date) -> Decimal:
        """Get total revenue for month."""
        month_end = date(month_start.year, month_start.month + 1, 1) - timedelta(days=1) if month_start.month < 12 else date(month_start.year + 1, 1, 1) - timedelta(days=1)
        result = await self.db.execute(
            select(func.sum(Payment.amount)).where(
                and_(
                    func.cast(Payment.payment_date, text) >= str(month_start),
                    func.cast(Payment.payment_date, text) <= str(month_end),
                    Payment.is_deleted == False,
                    Payment.status == "COMPLETED"
                )
            )
        )
        return Decimal(str(result.scalar() or 0))

    async def _get_new_patients_month(self, month_start: date) -> int:
        """Get new patients for month."""
        month_end = date(month_start.year, month_start.month + 1, 1) - timedelta(days=1) if month_start.month < 12 else date(month_start.year + 1, 1, 1) - timedelta(days=1)
        result = await self.db.execute(
            select(func.count(Patient.id)).where(
                and_(
                    func.cast(Patient.created_at, text) >= str(month_start),
                    func.cast(Patient.created_at, text) <= str(month_end),
                    Patient.is_deleted == False
                )
            )
        )
        return result.scalar() or 0

    async def _get_completed_appointments_month(self, month_start: date) -> int:
        """Get completed appointments for month."""
        month_end = date(month_start.year, month_start.month + 1, 1) - timedelta(days=1) if month_start.month < 12 else date(month_start.year + 1, 1, 1) - timedelta(days=1)
        result = await self.db.execute(
            select(func.count(Appointment.id)).where(
                and_(
                    func.cast(Appointment.appointment_date, text) >= str(month_start),
                    func.cast(Appointment.appointment_date, text) <= str(month_end),
                    Appointment.status == "COMPLETED",
                    Appointment.is_deleted == False
                )
            )
        )
        return result.scalar() or 0

    async def _get_appointments_trend(self, start_date: date, end_date: date) -> TrendWidgetDTO:
        """Get appointments trend data."""
        result = await self.db.execute(
            select(
                func.cast(func.cast(Appointment.appointment_date, text), text).label("date"),
                func.count(Appointment.id).label("count")
            ).where(
                and_(
                    func.cast(Appointment.appointment_date, text) >= str(start_date),
                    func.cast(Appointment.appointment_date, text) <= str(end_date),
                    Appointment.is_deleted == False
                )
            ).group_by(func.cast(func.cast(Appointment.appointment_date, text), text))
        )
        rows = result.all()
        data = [
            TrendPointDTO(date=date.fromisoformat(str(row.date)[:10]), value=row.count)
            for row in rows
        ]
        return TrendWidgetDTO(
            title="Appointments Trend",
            metric="APPOINTMENTS",
            period="DAY",
            data=data
        )

    async def _get_revenue_trend(self, start_date: date, end_date: date) -> TrendWidgetDTO:
        """Get revenue trend data."""
        result = await self.db.execute(
            select(
                func.cast(func.cast(Payment.payment_date, text), text).label("date"),
                func.sum(Payment.amount).label("total")
            ).where(
                and_(
                    func.cast(Payment.payment_date, text) >= str(start_date),
                    func.cast(Payment.payment_date, text) <= str(end_date),
                    Payment.is_deleted == False,
                    Payment.status == "COMPLETED"
                )
            ).group_by(func.cast(func.cast(Payment.payment_date, text), text))
        )
        rows = result.all()
        data = [
            TrendPointDTO(date=date.fromisoformat(str(row.date)[:10]), value=Decimal(str(row.total or 0)))
            for row in rows
        ]
        return TrendWidgetDTO(
            title="Revenue Trend",
            metric="REVENUE",
            period="DAY",
            data=data,
            unit="USD"
        )

    async def _get_recent_appointments(self, limit: int = 10) -> List[Dict]:
        """Get recent appointments."""
        result = await self.db.execute(
            select(Appointment).where(
                Appointment.is_deleted == False
            ).order_by(Appointment.appointment_date.desc()).limit(limit)
        )
        appointments = result.scalars().all()
        return [
            {
                "id": str(apt.id),
                "appointment_number": apt.appointment_number,
                "appointment_date": apt.appointment_date.isoformat() if apt.appointment_date else None,
                "status": apt.status,
            }
            for apt in appointments
        ]

    async def _get_doctor_appointments_today(self, doctor_id: UUID) -> int:
        """Get doctor appointments today."""
        today = datetime.utcnow().date()
        result = await self.db.execute(
            select(func.count(Appointment.id)).where(
                and_(
                    Appointment.doctor_id == doctor_id,
                    func.cast(Appointment.appointment_date, text).like(f"{today}%"),
                    Appointment.is_deleted == False
                )
            )
        )
        return result.scalar() or 0

    async def _get_doctor_appointments_date(self, doctor_id: UUID, d: date) -> int:
        """Get doctor appointments for date."""
        result = await self.db.execute(
            select(func.count(Appointment.id)).where(
                and_(
                    Appointment.doctor_id == doctor_id,
                    func.cast(Appointment.appointment_date, text).like(f"{d}%"),
                    Appointment.is_deleted == False
                )
            )
        )
        return result.scalar() or 0

    async def _get_doctor_patients_today(self, doctor_id: UUID) -> int:
        """Get unique patients for doctor today."""
        today = datetime.utcnow().date()
        result = await self.db.execute(
            select(func.count(func.distinct(Appointment.patient_id))).where(
                and_(
                    Appointment.doctor_id == doctor_id,
                    func.cast(Appointment.appointment_date, text).like(f"{today}%"),
                    Appointment.is_deleted == False
                )
            )
        )
        return result.scalar() or 0

    async def _get_doctor_upcoming_appointments(self, doctor_id: UUID, limit: int) -> List[Dict]:
        """Get doctor upcoming appointments."""
        now = datetime.utcnow()
        result = await self.db.execute(
            select(Appointment).where(
                and_(
                    Appointment.doctor_id == doctor_id,
                    Appointment.appointment_date >= now,
                    Appointment.is_deleted == False
                )
            ).order_by(Appointment.appointment_date.asc()).limit(limit)
        )
        appointments = result.scalars().all()
        return [
            {
                "id": str(apt.id),
                "appointment_number": apt.appointment_number,
                "appointment_date": apt.appointment_date.isoformat() if apt.appointment_date else None,
                "status": apt.status,
            }
            for apt in appointments
        ]

    async def _get_doctor_appointments_week(self, doctor_id: UUID, week_start: date) -> int:
        """Get doctor appointments for week."""
        week_end = week_start + timedelta(days=6)
        result = await self.db.execute(
            select(func.count(Appointment.id)).where(
                and_(
                    Appointment.doctor_id == doctor_id,
                    func.cast(Appointment.appointment_date, text) >= str(week_start),
                    func.cast(Appointment.appointment_date, text) <= str(week_end),
                    Appointment.is_deleted == False
                )
            )
        )
        return result.scalar() or 0

    async def _get_doctor_appointments_month(self, doctor_id: UUID, month_start: date) -> int:
        """Get doctor appointments for month."""
        month_end = date(month_start.year, month_start.month + 1, 1) - timedelta(days=1) if month_start.month < 12 else date(month_start.year + 1, 1, 1) - timedelta(days=1)
        result = await self.db.execute(
            select(func.count(Appointment.id)).where(
                and_(
                    Appointment.doctor_id == doctor_id,
                    func.cast(Appointment.appointment_date, text) >= str(month_start),
                    func.cast(Appointment.appointment_date, text) <= str(month_end),
                    Appointment.is_deleted == False
                )
            )
        )
        return result.scalar() or 0

    async def _get_doctor_appointments_trend(self, doctor_id: UUID, start_date: date, end_date: date) -> TrendWidgetDTO:
        """Get doctor appointments trend."""
        result = await self.db.execute(
            select(
                func.cast(func.cast(Appointment.appointment_date, text), text).label("date"),
                func.count(Appointment.id).label("count")
            ).where(
                and_(
                    Appointment.doctor_id == doctor_id,
                    func.cast(Appointment.appointment_date, text) >= str(start_date),
                    func.cast(Appointment.appointment_date, text) <= str(end_date),
                    Appointment.is_deleted == False
                )
            ).group_by(func.cast(func.cast(Appointment.appointment_date, text), text))
        )
        rows = result.all()
        data = [
            TrendPointDTO(date=date.fromisoformat(str(row.date)[:10]), value=row.count)
            for row in rows
        ]
        return TrendWidgetDTO(
            title="My Appointments Trend",
            metric="APPOINTMENTS",
            period="DAY",
            data=data
        )

    async def _get_total_patients_today(self) -> int:
        """Get total patients seen today."""
        today = datetime.utcnow().date()
        result = await self.db.execute(
            select(func.count(func.distinct(Appointment.patient_id))).where(
                and_(
                    func.cast(Appointment.appointment_date, text).like(f"{today}%"),
                    Appointment.is_deleted == False
                )
            )
        )
        return result.scalar() or 0

    async def _get_new_patients_today(self) -> int:
        """Get new patients registered today."""
        today = datetime.utcnow().date()
        result = await self.db.execute(
            select(func.count(Patient.id)).where(
                and_(
                    func.cast(Patient.created_at, text).like(f"{today}%"),
                    Patient.is_deleted == False
                )
            )
        )
        return result.scalar() or 0

    async def _get_upcoming_appointments(self, limit: int) -> int:
        """Get count of upcoming appointments."""
        now = datetime.utcnow()
        result = await self.db.execute(
            select(func.count(Appointment.id)).where(
                and_(
                    Appointment.appointment_date >= now,
                    Appointment.is_deleted == False
                )
            )
        )
        return result.scalar() or 0

    async def _get_today_appointments(self) -> List[Dict]:
        """Get today's appointments."""
        today = datetime.utcnow().date()
        result = await self.db.execute(
            select(Appointment).where(
                and_(
                    func.cast(Appointment.appointment_date, text).like(f"{today}%"),
                    Appointment.is_deleted == False
                )
            ).order_by(Appointment.appointment_date.asc())
        )
        appointments = result.scalars().all()
        return [
            {
                "id": str(apt.id),
                "appointment_number": apt.appointment_number,
                "appointment_date": apt.appointment_date.isoformat() if apt.appointment_date else None,
                "status": apt.status,
            }
            for apt in appointments
        ]

    async def _get_paid_payments_month(self, month_start: date) -> int:
        """Get completed payments count for month."""
        month_end = date(month_start.year, month_start.month + 1, 1) - timedelta(days=1) if month_start.month < 12 else date(month_start.year + 1, 1, 1) - timedelta(days=1)
        result = await self.db.execute(
            select(func.count(Payment.id)).where(
                and_(
                    func.cast(Payment.payment_date, text) >= str(month_start),
                    func.cast(Payment.payment_date, text) <= str(month_end),
                    Payment.status == "COMPLETED",
                    Payment.is_deleted == False
                )
            )
        )
        return result.scalar() or 0

    async def _get_pending_payments(self) -> int:
        """Get pending payments count."""
        result = await self.db.execute(
            select(func.count(Payment.id)).where(
                and_(
                    Payment.status.in_(["PENDING", "PROCESSING"]),
                    Payment.is_deleted == False
                )
            )
        )
        return result.scalar() or 0

    async def _get_recent_payments(self, limit: int) -> List[Dict]:
        """Get recent payments."""
        result = await self.db.execute(
            select(Payment).where(
                Payment.is_deleted == False
            ).order_by(Payment.payment_date.desc()).limit(limit)
        )
        payments = result.scalars().all()
        return [
            {
                "id": str(pay.id),
                "payment_number": pay.payment_number,
                "amount": float(pay.amount) if pay.amount else 0,
                "payment_date": pay.payment_date.isoformat() if pay.payment_date else None,
                "status": pay.status,
            }
            for pay in payments
        ]

    async def _get_total_employees(self) -> int:
        """Get total employees count (employees table removed; return 0 or count from linked_clinics later)."""
        return 0


def get_dashboard_service(db: AsyncSession = Depends(get_async_db)) -> DashboardService:
    """Dependency injection factory for DashboardService."""
    return DashboardService(db)
