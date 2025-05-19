from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..models import schemas
from ..services.db_service import DatabaseService
from ..services.scheduler_service import SchedulerService
from ..core.config import settings

router = APIRouter()

def get_db_service(db: Session) -> DatabaseService:
    return DatabaseService(db)

def get_scheduler_service(scheduler, ha_service) -> SchedulerService:
    return SchedulerService(scheduler, ha_service)

@router.post("/schedules", response_model=schemas.Response)
async def create_schedule(
    schedule: schemas.ScheduleCreate,
    db_service: DatabaseService = Depends(get_db_service),
    scheduler_service: SchedulerService = Depends(get_scheduler_service)
) -> schemas.Response:
    """Create a new irrigation schedule"""
    # Validate target exists
    if schedule.target_type == "solenoid":
        if not db_service.get_solenoid(schedule.target_id):
            raise HTTPException(
                status_code=400,
                detail=f"Solenoid {schedule.target_id} not found"
            )
    else:  # target_type == "group"
        if not db_service.get_group(schedule.target_id):
            raise HTTPException(
                status_code=400,
                detail=f"Group {schedule.target_id} not found"
            )

    # Create schedule in database
    db_schedule = db_service.create_schedule(schedule)
    if not db_schedule:
        raise HTTPException(
            status_code=500,
            detail="Failed to create schedule"
        )

    # Create scheduler jobs if schedule is enabled
    if db_schedule.is_enabled:
        success = scheduler_service.add_or_update_schedule(db_schedule)
        if not success:
            # Schedule was created in DB but jobs failed
            # We'll keep the schedule but warn the user
            return schemas.Response(
                success=True,
                message="Schedule created but job creation failed. Please check configuration.",
                data=db_schedule
            )

    return schemas.Response(
        success=True,
        message="Schedule created successfully",
        data=db_schedule
    )

@router.get("/schedules", response_model=schemas.Response)
async def list_schedules(
    db_service: DatabaseService = Depends(get_db_service)
) -> schemas.Response:
    """List all irrigation schedules"""
    schedules = db_service.get_schedules()
    return schemas.Response(
        success=True,
        message="Schedules retrieved successfully",
        data=schedules
    )

@router.get("/schedules/{schedule_id}", response_model=schemas.Response)
async def get_schedule(
    schedule_id: int,
    db_service: DatabaseService = Depends(get_db_service)
) -> schemas.Response:
    """Get a specific schedule by ID"""
    schedule = db_service.get_schedule(schedule_id)
    if not schedule:
        raise HTTPException(
            status_code=404,
            detail=f"Schedule {schedule_id} not found"
        )
    return schemas.Response(
        success=True,
        message="Schedule retrieved successfully",
        data=schedule
    )

@router.put("/schedules/{schedule_id}", response_model=schemas.Response)
async def update_schedule(
    schedule_id: int,
    schedule: schemas.ScheduleUpdate,
    db_service: DatabaseService = Depends(get_db_service),
    scheduler_service: SchedulerService = Depends(get_scheduler_service)
) -> schemas.Response:
    """Update a schedule"""
    # Update schedule in database
    updated_schedule = db_service.update_schedule(schedule_id, schedule)
    if not updated_schedule:
        raise HTTPException(
            status_code=404,
            detail=f"Schedule {schedule_id} not found"
        )

    # Update scheduler jobs
    if updated_schedule.is_enabled:
        success = scheduler_service.add_or_update_schedule(updated_schedule)
        if not success:
            return schemas.Response(
                success=True,
                message="Schedule updated but job update failed. Please check configuration.",
                data=updated_schedule
            )
    else:
        # Remove jobs if schedule is disabled
        scheduler_service.remove_schedule(schedule_id)

    return schemas.Response(
        success=True,
        message="Schedule updated successfully",
        data=updated_schedule
    )

@router.delete("/schedules/{schedule_id}", response_model=schemas.Response)
async def delete_schedule(
    schedule_id: int,
    db_service: DatabaseService = Depends(get_db_service),
    scheduler_service: SchedulerService = Depends(get_scheduler_service)
) -> schemas.Response:
    """Delete a schedule"""
    # Remove scheduler jobs first
    scheduler_service.remove_schedule(schedule_id)
    
    # Delete from database
    success = db_service.delete_schedule(schedule_id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Schedule {schedule_id} not found"
        )

    return schemas.Response(
        success=True,
        message="Schedule deleted successfully"
    )

@router.post("/schedules/{schedule_id}/run", response_model=schemas.Response)
async def run_schedule(
    schedule_id: int,
    db_service: DatabaseService = Depends(get_db_service),
    scheduler_service: SchedulerService = Depends(get_scheduler_service)
) -> schemas.Response:
    """Run a schedule immediately"""
    schedule = db_service.get_schedule(schedule_id)
    if not schedule:
        raise HTTPException(
            status_code=404,
            detail=f"Schedule {schedule_id} not found"
        )

    success = scheduler_service.run_schedule_now(schedule)
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to run schedule"
        )

    return schemas.Response(
        success=True,
        message="Schedule started successfully"
    )
