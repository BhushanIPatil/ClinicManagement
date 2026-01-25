"""
Health Check Endpoint

This module provides health check endpoints for monitoring and load balancers.
"""

from fastapi import APIRouter
from sqlalchemy import text
from app.core.database import db_manager

router = APIRouter()


@router.get("/debug-db", tags=["Health"])
async def health_check():
    """
    Basic health check endpoint.
    
    Returns:
        dict: Health status
    """
    print("DB TYPE:", type(db_manager.get_session()))
    print("DB:", db_manager.get_session())
    return {
        "status": "healthy",
        "service": "clinic-management-api"
    }


@router.get("/health/db", tags=["Health"])
async def database_health_check():
    """
    Database health check endpoint.
    
    Returns:
        dict: Database connection status
    """
    try:
        db = db_manager.get_session()
        try:
            db.execute(text("SELECT 1"))
            return {
                "status": "healthy",
                "database": "connected"
            }
        finally:
            db.close()
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }
