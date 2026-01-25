"""
Work Queue API Endpoints

This module provides endpoints for priority queue management.
"""

import uuid
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.core.database import db_manager
from app.infrastructure.database.models import WorkQueue, User

router = APIRouter(prefix="/work-queue", tags=["Work Queue"])


class CreateWorkQueueRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    priority: str = Field("NORMAL", description="LOW, NORMAL, HIGH, URGENT")
    status: str = Field("PENDING", description="PENDING, IN_PROGRESS, COMPLETED, CANCELLED")
    entity_type: Optional[str] = None
    entity_id: Optional[UUID] = None
    appointment_id: Optional[UUID] = None
    assigned_to_id: Optional[UUID] = None
    due_date: Optional[datetime] = None


class UpdateWorkQueueRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    assigned_to_id: Optional[UUID] = None
    due_date: Optional[datetime] = None
    notes: Optional[str] = None


class AssignWorkQueueRequest(BaseModel):
    assigned_to_id: UUID


class UpdateStatusRequest(BaseModel):
    status: str


def _str(v: Any) -> str:
    if v is None:
        return ""
    return str(v).strip() or ""


def _item_from(w: WorkQueue, u: Optional[User] = None) -> dict:
    assigned_name = "N/A"
    if u:
        fn = getattr(u, "first_name", None) or ""
        ln = getattr(u, "last_name", None) or ""
        assigned_name = f"{_str(fn)} {_str(ln)}".strip() or _str(getattr(u, "username", None)) or "N/A"
    return {
        "id": str(w.id),
        "title": _str(w.title),
        "description": _str(w.description) or "",
        "priority": _str(w.priority) or "NORMAL",
        "status": _str(w.status) or "PENDING",
        "entity_type": _str(w.entity_type) or None,
        "entity_id": str(w.entity_id) if w.entity_id else None,
        "assigned_to_user_id": str(w.assigned_to_id) if w.assigned_to_id else None,
        "assigned_to_user_name": assigned_name,
        "due_date": w.due_date.isoformat() if w.due_date else None,
        "completed_at": w.completed_at.isoformat() if w.completed_at else None,
        "metadata": None,
        "created_at": w.created_at.isoformat() if getattr(w, "created_at", None) else None,
        "updated_at": w.updated_at.isoformat() if getattr(w, "updated_at", None) else None,
    }


@router.get("")
async def list_queue_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    priority: Optional[str] = None,
    status: Optional[str] = None,
) -> Any:
    """List work queue items with filtering. Returns items with assigned_to_user_name; null-safe."""
    db = db_manager.get_session()
    try:
        base = db.query(WorkQueue).filter(WorkQueue.is_deleted == False)
        if priority:
            base = base.filter(WorkQueue.priority == priority)
        if status:
            base = base.filter(WorkQueue.status == status)
        total = base.count()

        rows = (
            db.query(WorkQueue, User)
            .select_from(WorkQueue)
            .outerjoin(User, WorkQueue.assigned_to_id == User.id)
            .filter(WorkQueue.is_deleted == False)
        )
        if priority:
            rows = rows.filter(WorkQueue.priority == priority)
        if status:
            rows = rows.filter(WorkQueue.status == status)
        rows = rows.order_by(WorkQueue.created_at.desc()).offset(skip).limit(limit).all()

        items = [_item_from(w, u) for w, u in rows]
        return {
            "items": items or [],
            "total": total,
            "skip": skip,
            "limit": limit,
        }
    finally:
        db.close()


@router.get("/{item_id}")
async def get_queue_item(item_id: str) -> Any:
    """Get queue item by ID."""
    try:
        iid = UUID(item_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid item ID")
    db = db_manager.get_session()
    try:
        row = (
            db.query(WorkQueue, User)
            .select_from(WorkQueue)
            .outerjoin(User, WorkQueue.assigned_to_id == User.id)
            .filter(WorkQueue.id == iid, WorkQueue.is_deleted == False)
            .first()
        )
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work queue item not found")
        w, u = row
        return _item_from(w, u)
    finally:
        db.close()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_queue_item(body: CreateWorkQueueRequest) -> Any:
    """Create a new queue item."""
    db = db_manager.get_session()
    try:
        qn = f"WQ-{uuid.uuid4().hex[:8].upper()}"
        w = WorkQueue(
            queue_number=qn,
            title=body.title,
            description=body.description,
            priority=body.priority or "NORMAL",
            status=body.status or "PENDING",
            entity_type=body.entity_type,
            entity_id=body.entity_id,
            appointment_id=body.appointment_id,
            assigned_to_id=body.assigned_to_id,
            due_date=body.due_date,
        )
        db.add(w)
        db.commit()
        db.refresh(w)
        u = db.query(User).filter(User.id == w.assigned_to_id).first() if w.assigned_to_id else None
        return _item_from(w, u)
    finally:
        db.close()


@router.put("/{item_id}")
async def update_queue_item(item_id: str, body: UpdateWorkQueueRequest) -> Any:
    """Update a work queue item."""
    try:
        iid = UUID(item_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid item ID")
    db = db_manager.get_session()
    try:
        w = db.query(WorkQueue).filter(WorkQueue.id == iid, WorkQueue.is_deleted == False).first()
        if not w:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work queue item not found")
        if body.title is not None:
            w.title = body.title
        if body.description is not None:
            w.description = body.description
        if body.priority is not None:
            w.priority = body.priority
        if body.status is not None:
            w.status = body.status
            if body.status == "COMPLETED":
                from datetime import timezone
                w.completed_at = datetime.now(timezone.utc)
        if body.assigned_to_id is not None:
            w.assigned_to_id = body.assigned_to_id
        if body.due_date is not None:
            w.due_date = body.due_date
        if body.notes is not None:
            w.notes = body.notes
        db.commit()
        db.refresh(w)
        u = db.query(User).filter(User.id == w.assigned_to_id).first() if w.assigned_to_id else None
        return _item_from(w, u)
    finally:
        db.close()


@router.delete("/{item_id}")
async def delete_queue_item(item_id: str) -> Any:
    """Soft-delete a work queue item."""
    try:
        iid = UUID(item_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid item ID")
    db = db_manager.get_session()
    try:
        w = db.query(WorkQueue).filter(WorkQueue.id == iid, WorkQueue.is_deleted == False).first()
        if not w:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work queue item not found")
        w.soft_delete()
        db.commit()
        return {"id": item_id, "deleted": True}
    finally:
        db.close()


@router.put("/{item_id}/status")
async def update_queue_item_status(item_id: str, body: UpdateStatusRequest) -> Any:
    """Update queue item status (convenience)."""
    try:
        iid = UUID(item_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid item ID")
    db = db_manager.get_session()
    try:
        w = db.query(WorkQueue).filter(WorkQueue.id == iid, WorkQueue.is_deleted == False).first()
        if not w:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work queue item not found")
        w.status = body.status
        if body.status == "COMPLETED":
            from datetime import timezone
            w.completed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(w)
        u = db.query(User).filter(User.id == w.assigned_to_id).first() if w.assigned_to_id else None
        return _item_from(w, u)
    finally:
        db.close()


@router.put("/{item_id}/assign")
async def assign_queue_item(item_id: str, body: AssignWorkQueueRequest) -> Any:
    """Assign queue item to a user."""
    try:
        iid = UUID(item_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid item ID")
    db = db_manager.get_session()
    try:
        w = db.query(WorkQueue).filter(WorkQueue.id == iid, WorkQueue.is_deleted == False).first()
        if not w:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work queue item not found")
        w.assigned_to_id = body.assigned_to_id
        db.commit()
        db.refresh(w)
        u = db.query(User).filter(User.id == body.assigned_to_id).first()
        return _item_from(w, u)
    finally:
        db.close()


@router.get("/stats/summary")
async def get_queue_stats() -> Any:
    """Get work queue statistics summary."""
    return {
        "pending": 0,
        "in_progress": 0,
        "completed": 0,
        "high_priority": 0
    }
