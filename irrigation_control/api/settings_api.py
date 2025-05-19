from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..models import schemas
from ..core.config import settings

router = APIRouter()

@router.get("/settings", response_model=schemas.Response)
async def get_settings() -> schemas.Response:
    """Get current addon settings"""
    config = {
        "version": settings.VERSION,
        "max_zones": settings.MAX_ZONES,
        "min_duration": settings.MIN_DURATION,
        "max_duration": settings.MAX_DURATION,
        "timezone": settings.TIMEZONE,
        "max_instances": settings.MAX_INSTANCES
    }
    
    return schemas.Response(
        success=True,
        message="Settings retrieved successfully",
        data=config
    )

@router.get("/settings/limits", response_model=schemas.Response)
async def get_limits() -> schemas.Response:
    """Get system limits and constraints"""
    limits = {
        "max_zones": settings.MAX_ZONES,
        "min_duration": settings.MIN_DURATION,
        "max_duration": settings.MAX_DURATION,
        "max_instances": settings.MAX_INSTANCES
    }
    
    return schemas.Response(
        success=True,
        message="System limits retrieved successfully",
        data=limits
    )

@router.get("/settings/version", response_model=schemas.Response)
async def get_version() -> schemas.Response:
    """Get addon version information"""
    version_info = {
        "version": settings.VERSION,
        "app_name": settings.APP_NAME
    }
    
    return schemas.Response(
        success=True,
        message="Version information retrieved successfully",
        data=version_info
    )

@router.get("/settings/status", response_model=schemas.Response)
async def get_status() -> schemas.Response:
    """Get addon status and health information"""
    # This could be expanded to include more detailed health checks
    status = {
        "status": "healthy",
        "supervisor_token": bool(settings.SUPERVISOR_TOKEN),
        "database_url": settings.DATABASE_URL != "",
        "scheduler_url": settings.SCHEDULER_DB_URL != ""
    }
    
    return schemas.Response(
        success=True,
        message="System status retrieved successfully",
        data=status
    )
