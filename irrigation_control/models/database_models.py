from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table, Time, Enum
from sqlalchemy.orm import relationship, DeclarativeBase
from datetime import time
from typing import List
import enum

class Base(DeclarativeBase):
    pass

class EventType(str, enum.Enum):
    P1 = "p1"
    P2 = "p2"
    MANUAL = "manual"

# Association table for many-to-many relationship between solenoids and groups
solenoid_group_association = Table(
    'solenoid_group_association',
    Base.metadata,
    Column('solenoid_id', Integer, ForeignKey('solenoids.id')),
    Column('group_id', Integer, ForeignKey('zone_groups.id'))
)

class SolenoidDevice(Base):
    __tablename__ = "solenoids"

    id = Column(Integer, primary_key=True, index=True)
    entity_id = Column(String, unique=True, index=True)  # Home Assistant entity_id
    name = Column(String)
    is_active = Column(Boolean, default=True)
    sequence_order = Column(Integer, nullable=True)  # For sequential operation
    
    # Relationships
    groups = relationship(
        "ZoneGroup",
        secondary=solenoid_group_association,
        back_populates="solenoids"
    )
    schedules = relationship("Schedule", back_populates="solenoid")

class ZoneGroup(Base):
    __tablename__ = "zone_groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    sequential_watering = Column(Boolean, default=False)  # Run zones sequentially
    
    # Relationships
    solenoids = relationship(
        "SolenoidDevice",
        secondary=solenoid_group_association,
        back_populates="groups"
    )
    schedules = relationship("Schedule", back_populates="group")

class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    target_type = Column(String)  # 'solenoid' or 'group'
    solenoid_id = Column(Integer, ForeignKey("solenoids.id"), nullable=True)
    group_id = Column(Integer, ForeignKey("zone_groups.id"), nullable=True)
    is_enabled = Column(Boolean, default=True)
    event_type = Column(Enum(EventType), default=EventType.MANUAL)
    priority = Column(Integer, default=0)  # Higher number = higher priority
    
    # Relationships
    solenoid = relationship("SolenoidDevice", back_populates="schedules")
    group = relationship("ZoneGroup", back_populates="schedules")
    time_slots = relationship("ScheduleTimeSlot", back_populates="schedule", cascade="all, delete-orphan")
    conditions = relationship("ScheduleCondition", back_populates="schedule", cascade="all, delete-orphan")

class ScheduleTimeSlot(Base):
    __tablename__ = "schedule_time_slots"

    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("schedules.id"))
    start_time = Column(Time, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    days_of_week = Column(String, nullable=False)  # Comma-separated days: "MON,TUE,WED"
    
    # Relationship
    schedule = relationship("Schedule", back_populates="time_slots")

class ScheduleCondition(Base):
    __tablename__ = "schedule_conditions"

    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("schedules.id"))
    entity_id = Column(String, nullable=False)  # Home Assistant entity ID to monitor
    condition_type = Column(String, nullable=False)  # 'state', 'numeric', 'template'
    operator = Column(String, nullable=False)  # '==', '!=', '>', '<', '>=', '<=', 'contains'
    value = Column(String, nullable=False)  # Expected value or template
    
    # Relationship
    schedule = relationship("Schedule", back_populates="conditions")

class ScheduleHistory(Base):
    __tablename__ = "schedule_history"

    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("schedules.id"))
    solenoid_id = Column(Integer, ForeignKey("solenoids.id"))
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=True)
    duration_minutes = Column(Integer)
    status = Column(String)  # 'completed', 'interrupted', 'skipped', 'error'
    reason = Column(String, nullable=True)  # Why was it skipped or interrupted?
    event_type = Column(Enum(EventType))
