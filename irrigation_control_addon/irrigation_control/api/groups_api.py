from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..models import schemas
from ..services.db_service import DatabaseService

router = APIRouter()

def get_db_service(db: Session) -> DatabaseService:
    return DatabaseService(db)

@router.post("/groups", response_model=schemas.Response)
async def create_group(
    group: schemas.ZoneGroupCreate,
    db_service: DatabaseService = Depends(get_db_service)
) -> schemas.Response:
    """Create a new zone group"""
    # Verify all solenoids exist
    for solenoid_id in group.solenoid_ids:
        if not db_service.get_solenoid(solenoid_id):
            raise HTTPException(
                status_code=400,
                detail=f"Solenoid {solenoid_id} not found"
            )

    db_group = db_service.create_group(group)
    if not db_group:
        raise HTTPException(
            status_code=500,
            detail="Failed to create group"
        )

    return schemas.Response(
        success=True,
        message="Group created successfully",
        data=db_group
    )

@router.get("/groups", response_model=schemas.Response)
async def list_groups(
    db_service: DatabaseService = Depends(get_db_service)
) -> schemas.Response:
    """List all zone groups"""
    groups = db_service.get_groups()
    return schemas.Response(
        success=True,
        message="Groups retrieved successfully",
        data=groups
    )

@router.get("/groups/{group_id}", response_model=schemas.Response)
async def get_group(
    group_id: int,
    db_service: DatabaseService = Depends(get_db_service)
) -> schemas.Response:
    """Get a specific zone group by ID"""
    group = db_service.get_group(group_id)
    if not group:
        raise HTTPException(
            status_code=404,
            detail=f"Group {group_id} not found"
        )
    return schemas.Response(
        success=True,
        message="Group retrieved successfully",
        data=group
    )

@router.put("/groups/{group_id}", response_model=schemas.Response)
async def update_group(
    group_id: int,
    group: schemas.ZoneGroupCreate,
    db_service: DatabaseService = Depends(get_db_service)
) -> schemas.Response:
    """Update a zone group"""
    # Verify all solenoids exist
    for solenoid_id in group.solenoid_ids:
        if not db_service.get_solenoid(solenoid_id):
            raise HTTPException(
                status_code=400,
                detail=f"Solenoid {solenoid_id} not found"
            )

    # Verify group exists
    existing_group = db_service.get_group(group_id)
    if not existing_group:
        raise HTTPException(
            status_code=404,
            detail=f"Group {group_id} not found"
        )

    updated_group = db_service.update_group(group_id, group)
    if not updated_group:
        raise HTTPException(
            status_code=500,
            detail="Failed to update group"
        )

    return schemas.Response(
        success=True,
        message="Group updated successfully",
        data=updated_group
    )

@router.delete("/groups/{group_id}", response_model=schemas.Response)
async def delete_group(
    group_id: int,
    db_service: DatabaseService = Depends(get_db_service)
) -> schemas.Response:
    """Delete a zone group"""
    success = db_service.delete_group(group_id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Group {group_id} not found"
        )
    return schemas.Response(
        success=True,
        message="Group deleted successfully"
    )

@router.post("/groups/{group_id}/control", response_model=schemas.Response)
async def control_group(
    group_id: int,
    action: str,
    db_service: DatabaseService = Depends(get_db_service),
    ha_service = Depends(get_ha_service)
) -> schemas.Response:
    """Control all solenoids in a group (turn on/off)"""
    if action not in ["turn_on", "turn_off"]:
        raise HTTPException(
            status_code=400,
            detail="Action must be either 'turn_on' or 'turn_off'"
        )

    group = db_service.get_group(group_id)
    if not group:
        raise HTTPException(
            status_code=404,
            detail=f"Group {group_id} not found"
        )

    # Control each solenoid in the group
    success = True
    failed_solenoids = []
    for solenoid in group.solenoids:
        if not ha_service.control_switch(solenoid.entity_id, action):
            success = False
            failed_solenoids.append(solenoid.entity_id)

    if not success:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to {action} solenoids: {', '.join(failed_solenoids)}"
        )

    return schemas.Response(
        success=True,
        message=f"Group {action} successfully"
    )
