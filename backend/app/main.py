"""
FastAPI Application Entry Point

This is the main application file that initializes FastAPI, sets up middleware,
configures routes, and manages the application lifecycle.

Key Features:
- FastAPI application initialization
- Database connection management
- CORS configuration
- Route registration
- Application lifecycle events
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import db_manager
from app.api.v1.endpoints import health  # Import endpoints as you create them


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    
    Handles startup and shutdown events:
    - Startup: Initialize database connections
    - Shutdown: Close database connections and cleanup
    
    Args:
        app: FastAPI application instance
        
    Yields:
        None
    """
    # Startup
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Debug mode: {settings.DEBUG}")
    
    # Initialize database
    db_manager.initialize()
    print("Database initialized")
    
    yield
    
    # Shutdown
    print("Shutting down application...")
    await db_manager.close()
    print("Database connections closed")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Hospital/Clinic Management System API",
    debug=settings.DEBUG,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled exceptions.
    
    In production, you might want to log these exceptions
    to a monitoring service.
    """
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An unexpected error occurred"
        }
    )


# Include routers
# Register your API routers here
app.include_router(
    health.router,
    prefix="/api/v1",
    tags=["Health"]
)

# Authentication routes
from app.api.v1.endpoints import auth
app.include_router(
    auth.router,
    prefix="/api/v1",
)

# Appointment management routes
from app.api.v1.endpoints import appointments
app.include_router(
    appointments.router,
    prefix="/api/v1",
)

# Patients (add before setting up appointments)
from app.api.v1.endpoints import patients
app.include_router(
    patients.router,
    prefix="/api/v1",
)

# Doctors by clinic (use primary_clinic_id from login/cookies for appointment dropdown etc.)
from app.api.v1.endpoints import doctors
app.include_router(
    doctors.router,
    prefix="/api/v1",
)

# Work queue routes
from app.api.v1.endpoints import work_queue
app.include_router(
    work_queue.router,
    prefix="/api/v1",
)

# Finance & Billing routes
from app.api.v1.endpoints import finance
app.include_router(
    finance.router,
    prefix="/api/v1",
)

# Payroll & HR routes
from app.api.v1.endpoints import payroll
app.include_router(
    payroll.router,
    prefix="/api/v1",
)

# KPI & Targets routes
from app.api.v1.endpoints import kpi
app.include_router(
    kpi.router,
    prefix="/api/v1",
)

# Super Admin routes (clinics count, clinic users, onboard clinic with user)
from app.api.v1.endpoints import super_admin
app.include_router(
    super_admin.router,
    prefix="/api/v1",
)

# Clinic Admin routes (add employees with NURSE/HR_OPERATIONS/RECEPTIONIST)
from app.api.v1.endpoints import clinic_admin
app.include_router(
    clinic_admin.router,
    prefix="/api/v1",
)


@app.get("/")
async def root():
    """
    Root endpoint.
    
    Returns:
        dict: Application information
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        dict: Health status
    """
    return {
        "status": "healthy",
        "database": "connected"  # You can add actual DB health check
    }
