"""
Dashboard Data Transfer Objects

DTOs for role-based dashboard responses with widgets, stats, and trends.
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class StatCardDTO(BaseModel):
    """Single stat card widget."""
    title: str
    value: int | Decimal
    change: Optional[float] = Field(None, description="Percentage change from previous period")
    trend: Optional[str] = Field(None, description="UP, DOWN, or STABLE")
    icon: Optional[str] = None
    color: Optional[str] = None


class TrendPointDTO(BaseModel):
    """Single point in a trend series."""
    date: date
    value: int | Decimal
    label: Optional[str] = None


class TrendWidgetDTO(BaseModel):
    """Trend chart widget."""
    title: str
    metric: str
    period: str = Field(..., description="DAY, WEEK, MONTH, YEAR")
    data: List[TrendPointDTO]
    unit: Optional[str] = None


class SummaryCountDTO(BaseModel):
    """Summary count widget."""
    label: str
    count: int
    icon: Optional[str] = None
    color: Optional[str] = None


class DashboardWidgetDTO(BaseModel):
    """Generic dashboard widget."""
    id: str
    type: str = Field(..., description="STAT_CARD, TREND_CHART, SUMMARY_LIST, TABLE")
    title: str
    data: Dict[str, Any]
    position: Optional[int] = None
    size: Optional[str] = Field(None, description="SMALL, MEDIUM, LARGE, FULL")


class AdminDashboardDTO(BaseModel):
    """Admin dashboard response."""
    role: str = "ADMIN"
    generated_at: datetime
    widgets: List[DashboardWidgetDTO]
    stats: Dict[str, StatCardDTO]
    summary_counts: List[SummaryCountDTO]
    trends: List[TrendWidgetDTO]
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "role": "ADMIN",
                "generated_at": "2024-01-23T10:00:00Z",
                "widgets": [],
                "stats": {},
                "summary_counts": [],
                "trends": []
            }
        }
    )


class DoctorDashboardDTO(BaseModel):
    """Doctor dashboard response."""
    role: str = "DOCTOR"
    generated_at: datetime
    doctor_id: UUID
    widgets: List[DashboardWidgetDTO]
    stats: Dict[str, StatCardDTO]
    summary_counts: List[SummaryCountDTO]
    trends: List[TrendWidgetDTO]
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "role": "DOCTOR",
                "generated_at": "2024-01-23T10:00:00Z",
                "doctor_id": "123e4567-e89b-12d3-a456-426614174000",
                "widgets": [],
                "stats": {},
                "summary_counts": [],
                "trends": []
            }
        }
    )


class NurseDashboardDTO(BaseModel):
    """Nurse dashboard response."""
    role: str = "NURSE"
    generated_at: datetime
    widgets: List[DashboardWidgetDTO]
    stats: Dict[str, StatCardDTO]
    summary_counts: List[SummaryCountDTO]
    trends: List[TrendWidgetDTO]


class ReceptionistDashboardDTO(BaseModel):
    """Receptionist dashboard response."""
    role: str = "RECEPTIONIST"
    generated_at: datetime
    widgets: List[DashboardWidgetDTO]
    stats: Dict[str, StatCardDTO]
    summary_counts: List[SummaryCountDTO]
    trends: List[TrendWidgetDTO]


class AccountantDashboardDTO(BaseModel):
    """Accountant dashboard response."""
    role: str = "ACCOUNTANT"
    generated_at: datetime
    widgets: List[DashboardWidgetDTO]
    stats: Dict[str, StatCardDTO]
    summary_counts: List[SummaryCountDTO]
    trends: List[TrendWidgetDTO]


class HRDashboardDTO(BaseModel):
    """HR dashboard response."""
    role: str = "HR"
    generated_at: datetime
    widgets: List[DashboardWidgetDTO]
    stats: Dict[str, StatCardDTO]
    summary_counts: List[SummaryCountDTO]
    trends: List[TrendWidgetDTO]
