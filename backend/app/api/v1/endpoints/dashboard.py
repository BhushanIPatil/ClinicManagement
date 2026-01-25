"""
Dashboard API Endpoints

Role-based dashboard endpoints with optimized single-endpoint-per-role design.
Cache-friendly and fast response.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Response, Header
from fastapi.responses import JSONResponse

from app.core.security.dependencies import get_current_user, require_roles
from app.domain.entities.user import User
from app.application.services.dashboard_service import DashboardService, get_dashboard_service
from app.application.dto.dashboard_dto import (
    AdminDashboardDTO,
    DoctorDashboardDTO,
    NurseDashboardDTO,
    ReceptionistDashboardDTO,
    AccountantDashboardDTO,
    HRDashboardDTO,
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/admin",
    response_model=AdminDashboardDTO,
    summary="Admin Dashboard",
    description="Get comprehensive admin dashboard with all stats, widgets, and trends."
)
async def get_admin_dashboard(
    service: DashboardService = Depends(get_dashboard_service),
    current_user: User = Depends(require_roles("ADMIN")),
    cache_control: Optional[str] = Header(None, alias="Cache-Control"),
) -> AdminDashboardDTO:
    """
    Admin Dashboard Endpoint
    
    Returns:
    - Real-time stats (patients, appointments, revenue, etc.)
    - Summary counts for current period
    - Trend data for visualizations
    - Widgets for dashboard display
    
    Cache: Recommended 60 seconds for optimal performance
    """
    dashboard = await service.get_admin_dashboard()
    
    # Set cache headers for fast response
    response = JSONResponse(content=dashboard.model_dump())
    response.headers["Cache-Control"] = "public, max-age=60"
    response.headers["ETag"] = f'"{dashboard.generated_at.timestamp()}"'
    
    return dashboard


@router.get(
    "/doctor",
    response_model=DoctorDashboardDTO,
    summary="Doctor Dashboard",
    description="Get doctor-specific dashboard with appointments, patients, and performance metrics."
)
async def get_doctor_dashboard(
    service: DashboardService = Depends(get_dashboard_service),
    current_user: User = Depends(require_roles("DOCTOR")),
) -> DoctorDashboardDTO:
    """
    Doctor Dashboard Endpoint
    
    Returns:
    - Today's appointments and patients
    - Upcoming appointments
    - Weekly/monthly appointment trends
    - Performance metrics
    
    Note: Uses current user's doctor profile ID
    """
    # TODO: Get doctor_id from current_user's employee/doctor relationship
    # For now, we'll need to extract it from user context
    # This assumes user has a doctor_id field or relationship
    doctor_id = getattr(current_user, 'doctor_id', None)
    if not doctor_id:
        # Fallback: try to get from employee relationship
        # This would need to be implemented based on your user model
        raise ValueError("Doctor ID not found for current user")
    
    dashboard = await service.get_doctor_dashboard(doctor_id)
    
    response = JSONResponse(content=dashboard.model_dump())
    response.headers["Cache-Control"] = "public, max-age=60"
    
    return dashboard


@router.get(
    "/doctor/{doctor_id}",
    response_model=DoctorDashboardDTO,
    summary="Doctor Dashboard by ID",
    description="Get dashboard for a specific doctor (admin/HR only)."
)
async def get_doctor_dashboard_by_id(
    doctor_id: UUID,
    service: DashboardService = Depends(get_dashboard_service),
    current_user: User = Depends(require_roles("ADMIN", "HR")),
) -> DoctorDashboardDTO:
    """Get dashboard for a specific doctor (admin/HR access)."""
    dashboard = await service.get_doctor_dashboard(doctor_id)
    
    response = JSONResponse(content=dashboard.model_dump())
    response.headers["Cache-Control"] = "public, max-age=60"
    
    return dashboard


@router.get(
    "/nurse",
    response_model=NurseDashboardDTO,
    summary="Nurse Dashboard",
    description="Get nurse dashboard with patient care metrics and tasks."
)
async def get_nurse_dashboard(
    service: DashboardService = Depends(get_dashboard_service),
    current_user: User = Depends(require_roles("NURSE")),
) -> NurseDashboardDTO:
    """
    Nurse Dashboard Endpoint
    
    Returns:
    - Patients today
    - Pending tasks
    - Today's appointments
    """
    dashboard = await service.get_nurse_dashboard()
    
    response = JSONResponse(content=dashboard.model_dump())
    response.headers["Cache-Control"] = "public, max-age=60"
    
    return dashboard


@router.get(
    "/receptionist",
    response_model=ReceptionistDashboardDTO,
    summary="Receptionist Dashboard",
    description="Get receptionist dashboard with appointments and patient registration metrics."
)
async def get_receptionist_dashboard(
    service: DashboardService = Depends(get_dashboard_service),
    current_user: User = Depends(require_roles("RECEPTIONIST")),
) -> ReceptionistDashboardDTO:
    """
    Receptionist Dashboard Endpoint
    
    Returns:
    - Appointments today
    - New patients today
    - Pending tasks
    - Today's appointments list
    """
    dashboard = await service.get_receptionist_dashboard()
    
    response = JSONResponse(content=dashboard.model_dump())
    response.headers["Cache-Control"] = "public, max-age=30"  # More frequent updates for reception
    
    return dashboard


@router.get(
    "/accountant",
    response_model=AccountantDashboardDTO,
    summary="Accountant Dashboard",
    description="Get accountant dashboard with financial metrics, invoices, and payments."
)
async def get_accountant_dashboard(
    service: DashboardService = Depends(get_dashboard_service),
    current_user: User = Depends(require_roles("ACCOUNTANT")),
) -> AccountantDashboardDTO:
    """
    Accountant Dashboard Endpoint
    
    Returns:
    - Revenue today and monthly
    - Pending invoices
    - Payment status
    - Revenue trends
    - Recent payments
    """
    dashboard = await service.get_accountant_dashboard()
    
    response = JSONResponse(content=dashboard.model_dump())
    response.headers["Cache-Control"] = "public, max-age=60"
    
    return dashboard


@router.get(
    "/hr",
    response_model=HRDashboardDTO,
    summary="HR Dashboard",
    description="Get HR dashboard with employee and staff metrics."
)
async def get_hr_dashboard(
    service: DashboardService = Depends(get_dashboard_service),
    current_user: User = Depends(require_roles("HR")),
) -> HRDashboardDTO:
    """
    HR Dashboard Endpoint
    
    Returns:
    - Total employees
    - Active doctors
    - Staff statistics
    """
    dashboard = await service.get_hr_dashboard()
    
    response = JSONResponse(content=dashboard.model_dump())
    response.headers["Cache-Control"] = "public, max-age=300"  # HR data changes less frequently
    
    return dashboard
