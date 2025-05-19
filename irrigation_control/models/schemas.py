from pydantic import BaseModel, Field
from typing import List, Optional, Union
from datetime import time
from .database_models import EventType

class SolenoidBase(BaseModel):
    entity_id: str = Field(..., description="Home Assistant entity ID for the switch")
    name: str = Field(..., description="Display name for the solenoid")
    is_active: bool = Field(default=True, description="Whether the solenoid is active")
    sequence_order: Optional[int] = Field(None, description="Order in sequential operations")

class SolenoidCreate(SolenoidBase):
    pass

class Solenoid(SolenoidBase):
    id: int
    
    class Config:
        from_attributes = True

class ZoneGroupBase(BaseModel):
    name: str = Field(..., description="Name of the zone group")
    is_active: bool = Field(default=True, description="Whether the group is active")
    sequential_watering: bool = Field(default=False, description="Run zones sequentially")

class ZoneGroupCreate(ZoneGroupBase):
    solenoid_ids: List[int] = Field(default_factory=list, description="IDs of solenoids to include in the group")

class ZoneGroup(ZoneGroupBase):
    id: int
    solenoids: List[Solenoid] = []
    
    class Config:
        from_attributes = True

class ScheduleConditionBase(BaseModel):
    entity_id: str = Field(..., description="Home Assistant entity ID to monitor")
    condition_type: str = Field(..., description="Type of condition (state/numeric/template)")
    operator: str = Field(..., description="Comparison operator")
    value: str = Field(..., description="Expected value or template")

class ScheduleConditionCreate(ScheduleConditionBase):
    pass

class ScheduleCondition(ScheduleConditionBase):
    id: int
    schedule_id: int
    
    class Config:
        from_attributes = True

class TimeSlotBase(BaseModel):
    start_time: time = Field(..., description="Time to start watering (HH:MM)")
    duration_minutes: int = Field(..., ge=1, le=360, description="Duration in minutes")
    days_of_week: str = Field(..., description="Comma-separated list of days (MON,TUE,etc)")

class TimeSlotCreate(TimeSlotBase):
    pass

class TimeSlot(TimeSlotBase):
    id: int
    schedule_id: int
    
    class Config:
        from_attributes = True

class ScheduleBase(BaseModel):
    name: str = Field(..., description="Name of the schedule")
    target_type: str = Field(..., description="Type of target (solenoid or group)")
    is_enabled: bool = Field(default=True, description="Whether the schedule is active")
    event_type: EventType = Field(default=EventType.MANUAL, description="Type of event (P1/P2/MANUAL)")
    priority: int = Field(default=0, description="Schedule priority (higher = more important)")

class ScheduleCreate(ScheduleBase):
    target_id: int = Field(..., description="ID of the target (solenoid_id or group_id)")
    time_slots: List[TimeSlotCreate] = Field(default_factory=list, description="Time slots for this schedule")
    conditions: List[ScheduleConditionCreate] = Field(default_factory=list, description="Conditions for this schedule")

class Schedule(ScheduleBase):
    id: int
    solenoid_id: Optional[int]
    group_id: Optional[int]
    time_slots: List[TimeSlot] = []
    conditions: List[ScheduleCondition] = []
    
    class Config:
        from_attributes = True

class ScheduleUpdate(BaseModel):
    name: Optional[str] = None
    is_enabled: Optional[bool] = None
    event_type: Optional[EventType] = None
    priority: Optional[int] = None
    time_slots: Optional[List[TimeSlotCreate]] = None
    conditions: Optional[List[ScheduleConditionCreate]] = None

class ScheduleHistoryEntry(BaseModel):
    id: int
    schedule_id: int
    solenoid_id: int
    start_time: time
    end_time: Optional[time]
    duration_minutes: int
    status: str
    reason: Optional[str]
    event_type: EventType

    class Config:
        from_attributes = True

# Response Models
class Response(BaseModel):
    success: bool
    message: str
    data: Optional[Union[
        Solenoid,
        List[Solenoid],
        ZoneGroup,
        List[ZoneGroup],
        Schedule,
        List[Schedule],
        ScheduleHistoryEntry,
        List[ScheduleHistoryEntry],
        dict,
        None
    ]] = None

# Status/Health Models
class SystemStatus(BaseModel):
    active_schedules: int
    pending_jobs: int
    running_jobs: int
    p1_events_today: int
    p2_events_today: int
    last_run_status: Optional[str]
    database_size: str
    uptime: str

class EventStatus(BaseModel):
    event_type: EventType
    active_count: int
    total_slots: int
    next_runtime: Optional[str]
    last_runtime: Optional[str]
    success_rate: float  # Percentage of successful runs
