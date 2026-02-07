"""
My Tasks API – personal tasks per user (not visible to others).
All endpoints scoped by current user id from JWT.
"""

from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.core.database import db_manager
from app.infrastructure.database.models import UserTask
from app.api.v1.deps import get_current_user_context, CurrentUserContext

router = APIRouter(prefix="/my-tasks", tags=["My Tasks"])


class CreateMyTaskRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    priority: str = Field("NORMAL", description="LOW, NORMAL, HIGH")
    due_date: Optional[datetime] = None


class UpdateMyTaskRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    status: Optional[str] = None


def _task_to_dict(t: UserTask) -> dict:
    return {
        "id": str(t.id),
        "title": (t.title or "").strip(),
        "description": (t.description or "").strip() or None,
        "status": (t.status or "PENDING").strip(),
        "priority": (t.priority or "NORMAL").strip() if t.priority else "NORMAL",
        "due_date": t.due_date.isoformat() if t.due_date else None,
        "completed_at": t.completed_at.isoformat() if t.completed_at else None,
        "created_at": t.created_at.isoformat() if getattr(t, "created_at", None) else None,
        "updated_at": t.updated_at.isoformat() if getattr(t, "updated_at", None) else None,
    }


@router.get("")
async def list_my_tasks(
    ctx: CurrentUserContext = Depends(get_current_user_context),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = None,
) -> Any:
    """List current user's tasks only."""
    db = db_manager.get_session()
    try:
        base = (
            db.query(UserTask)
            .filter(UserTask.is_deleted == False, UserTask.user_id == ctx.user_id)
        )
        if status:
            base = base.filter(UserTask.status == status)
        total = base.count()
        rows = (
            base.order_by(UserTask.due_date.asc(), UserTask.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        items = [_task_to_dict(t) for t in rows]
        return {"items": items, "total": total, "skip": skip, "limit": limit}
    finally:
        db.close()


@router.get("/{task_id}")
async def get_my_task(
    task_id: str,
    ctx: CurrentUserContext = Depends(get_current_user_context),
) -> Any:
    """Get one task by id (must belong to current user)."""
    try:
        tid = UUID(task_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid task ID")
    db = db_manager.get_session()
    try:
        t = (
            db.query(UserTask)
            .filter(
                UserTask.id == tid,
                UserTask.is_deleted == False,
                UserTask.user_id == ctx.user_id,
            )
            .first()
        )
        if not t:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        return _task_to_dict(t)
    finally:
        db.close()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_my_task(
    body: CreateMyTaskRequest,
    ctx: CurrentUserContext = Depends(get_current_user_context),
) -> Any:
    """Create a personal task for the current user."""
    db = db_manager.get_session()
    try:
        t = UserTask(
            title=body.title,
            description=body.description,
            priority=body.priority or "NORMAL",
            status="PENDING",
            due_date=body.due_date,
            user_id=ctx.user_id,
        )
        db.add(t)
        db.commit()
        db.refresh(t)
        return _task_to_dict(t)
    finally:
        db.close()


@router.put("/{task_id}")
async def update_my_task(
    task_id: str,
    body: UpdateMyTaskRequest,
    ctx: CurrentUserContext = Depends(get_current_user_context),
) -> Any:
    """Update a task (must belong to current user)."""
    try:
        tid = UUID(task_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid task ID")
    db = db_manager.get_session()
    try:
        t = (
            db.query(UserTask)
            .filter(
                UserTask.id == tid,
                UserTask.is_deleted == False,
                UserTask.user_id == ctx.user_id,
            )
            .first()
        )
        if not t:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        if body.title is not None:
            t.title = body.title
        if body.description is not None:
            t.description = body.description
        if body.priority is not None:
            t.priority = body.priority
        if body.due_date is not None:
            t.due_date = body.due_date
        if body.status is not None:
            t.status = body.status
            if body.status == "COMPLETED":
                t.completed_at = datetime.now(timezone.utc)
            elif t.completed_at and body.status != "COMPLETED":
                t.completed_at = None
        db.commit()
        db.refresh(t)
        return _task_to_dict(t)
    finally:
        db.close()


@router.delete("/{task_id}")
async def delete_my_task(
    task_id: str,
    ctx: CurrentUserContext = Depends(get_current_user_context),
) -> Any:
    """Soft-delete a task (must belong to current user)."""
    try:
        tid = UUID(task_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid task ID")
    db = db_manager.get_session()
    try:
        t = (
            db.query(UserTask)
            .filter(
                UserTask.id == tid,
                UserTask.is_deleted == False,
                UserTask.user_id == ctx.user_id,
            )
            .first()
        )
        if not t:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        t.soft_delete()
        db.commit()
        return {"id": task_id, "deleted": True}
    finally:
        db.close()


@router.post("/{task_id}/complete")
async def complete_my_task(
    task_id: str,
    ctx: CurrentUserContext = Depends(get_current_user_context),
) -> Any:
    """Mark task as COMPLETED."""
    try:
        tid = UUID(task_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid task ID")
    db = db_manager.get_session()
    try:
        t = (
            db.query(UserTask)
            .filter(
                UserTask.id == tid,
                UserTask.is_deleted == False,
                UserTask.user_id == ctx.user_id,
            )
            .first()
        )
        if not t:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        t.status = "COMPLETED"
        t.completed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(t)
        return _task_to_dict(t)
    finally:
        db.close()
