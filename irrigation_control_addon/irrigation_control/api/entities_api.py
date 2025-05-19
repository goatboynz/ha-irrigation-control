from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import os

from ..models import schemas
from ..services.db_service import DatabaseService
from ..services.ha_service import HomeAssistantService
from ..core.config import settings

router = APIRouter()

def get_ha_service() -> HomeAssistantService:
    token = os.getenv("SUPERVISOR_TOKEN")
    if not token:
        raise HTTPException(status_code=500, message="Supervisor token not available")
    return HomeAssistantService(token)

def get_db_service(db: Session) -> DatabaseService:
    return DatabaseService(db)

@router.get("/ha-switches", response_model=List[dict])
async def get_available_switches(
    ha_service: HomeAssistantService = Depends(get_ha_service)
) -> List[dict]:
    """Get all available switch entities from Home Assistant"""
    try:
        switches = ha_service.get_switches()
        return switches
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch switches from Home Assistant: {str(e)}"
        )

@router.post("/solenoids", response_model=schemas.Response)
async def create_solenoid(
    solenoid: schemas.SolenoidCreate,
    db_service: DatabaseService = Depends(get_db_service),
    ha_service: HomeAssistantService = Depends(get_ha_service)
) -> schemas.Response:
    """Create a new solenoid mapping"""
    # Verify the switch exists in Home Assistant
    switches = ha_service.get_switches()
    if not any(s["entity_id"] == solenoid.entity_id for s in switches):
        raise HTTPException(
            status_code=400,
            detail=f"Switch {solenoid.entity_id} not found in Home Assistant"
        )

    # Check if already mapped
    existing = db_service.get_solenoid_by_entity_id(solenoid.entity_id)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Entity {solenoid.entity_id} is already mapped"
        )

    # Create solenoid
    db_solenoid = db_service.create_solenoid(solenoid)
    if not db_solenoid:
        raise HTTPException(
            status_code=500,
            detail="Failed to create solenoid"
        )

    return schemas.Response(
        success=True,
        message="Solenoid created successfully",
        data=db_solenoid
    )

@router.get("/solenoids", response_model=schemas.Response)
async def list_solenoids(
    db_service: DatabaseService = Depends(get_db_service)
) -> schemas.Response:
    """List all mapped solenoids"""
    solenoids = db_service.get_solenoids()
    return schemas.Response(
        success=True,
        message="Solenoids retrieved successfully",
        data=solenoids
    )

@router.get("/solenoids/{solenoid_id}", response_model=schemas.Response)
async def get_solenoid(
    solenoid_id: int,
    db_service: DatabaseService = Depends(get_db_service)
) -> schemas.Response:
    """Get a specific solenoid by ID"""
    solenoid = db_service.get_solenoid(solenoid_id)
    if not solenoid:
        raise HTTPException(
            status_code=404,
            detail=f"Solenoid {solenoid_id} not found"
        )
    return schemas.Response(
        success=True,
        message="Solenoid retrieved successfully",
        data=solenoid
    )

@router.delete("/solenoids/{solenoid_id}", response_model=schemas.Response)
async def delete_solenoid(
    solenoid_id: int,
    db_service: DatabaseService = Depends(get_db_service)
) -> schemas.Response:
    """Delete a solenoid mapping"""
    success = db_service.delete_solenoid(solenoid_id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Solenoid {solenoid_id} not found"
        )
    return schemas.Response(
        success=True,
        message="Solenoid deleted successfully"
    )

@router.post("/solenoids/{solenoid_id}/control", response_model=schemas.Response)
async def control_solenoid(
    solenoid_id: int,
    action: str,
    db_service: DatabaseService = Depends(get_db_service),
    ha_service: HomeAssistantService = Depends(get_ha_service)
) -> schemas.Response:
    """Control a solenoid (turn on/off)"""
    if action not in ["turn_on", "turn_off"]:
        raise HTTPException(
            status_code=400,
            detail="Action must be either 'turn_on' or 'turn_off'"
        )

    solenoid = db_service.get_solenoid(solenoid_id)
    if not solenoid:
        raise HTTPException(
            status_code=404,
            detail=f"Solenoid {solenoid_id} not found"
        )

    success = ha_service.control_switch(solenoid.entity_id, action)
    if not success:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to {action} solenoid"
        )

    return schemas.Response(
        success=True,
        message=f"Solenoid {action} successfully"
    )
