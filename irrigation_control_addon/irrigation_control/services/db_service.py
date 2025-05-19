from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
import logging

from ..models import database_models as models
from ..models import schemas

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self, db: Session):
        self.db = db

    # Solenoid Operations
    def create_solenoid(self, solenoid: schemas.SolenoidCreate) -> Optional[models.SolenoidDevice]:
        try:
            db_solenoid = models.SolenoidDevice(**solenoid.model_dump())
            self.db.add(db_solenoid)
            self.db.commit()
            self.db.refresh(db_solenoid)
            return db_solenoid
        except SQLAlchemyError as e:
            logger.error(f"Error creating solenoid: {str(e)}")
            self.db.rollback()
            return None

    def get_solenoid(self, solenoid_id: int) -> Optional[models.SolenoidDevice]:
        return self.db.query(models.SolenoidDevice).filter(
            models.SolenoidDevice.id == solenoid_id
        ).first()

    def get_solenoid_by_entity_id(self, entity_id: str) -> Optional[models.SolenoidDevice]:
        return self.db.query(models.SolenoidDevice).filter(
            models.SolenoidDevice.entity_id == entity_id
        ).first()

    def get_solenoids(self) -> List[models.SolenoidDevice]:
        return self.db.query(models.SolenoidDevice).all()

    def delete_solenoid(self, solenoid_id: int) -> bool:
        try:
            solenoid = self.get_solenoid(solenoid_id)
            if solenoid:
                self.db.delete(solenoid)
                self.db.commit()
                return True
            return False
        except SQLAlchemyError as e:
            logger.error(f"Error deleting solenoid: {str(e)}")
            self.db.rollback()
            return False

    # Zone Group Operations
    def create_group(self, group: schemas.ZoneGroupCreate) -> Optional[models.ZoneGroup]:
        try:
            solenoid_ids = group.solenoid_ids
            group_data = group.model_dump(exclude={'solenoid_ids'})
            
            db_group = models.ZoneGroup(**group_data)
            self.db.add(db_group)
            self.db.flush()  # Get ID without committing

            # Add solenoids to group
            for solenoid_id in solenoid_ids:
                solenoid = self.get_solenoid(solenoid_id)
                if solenoid:
                    db_group.solenoids.append(solenoid)

            self.db.commit()
            self.db.refresh(db_group)
            return db_group
        except SQLAlchemyError as e:
            logger.error(f"Error creating group: {str(e)}")
            self.db.rollback()
            return None

    def get_group(self, group_id: int) -> Optional[models.ZoneGroup]:
        return self.db.query(models.ZoneGroup).filter(
            models.ZoneGroup.id == group_id
        ).first()

    def get_groups(self) -> List[models.ZoneGroup]:
        return self.db.query(models.ZoneGroup).all()

    def update_group(self, group_id: int, group: schemas.ZoneGroupCreate) -> Optional[models.ZoneGroup]:
        try:
            db_group = self.get_group(group_id)
            if not db_group:
                return None

            # Update basic fields
            for key, value in group.model_dump(exclude={'solenoid_ids'}).items():
                setattr(db_group, key, value)

            # Update solenoids
            db_group.solenoids.clear()
            for solenoid_id in group.solenoid_ids:
                solenoid = self.get_solenoid(solenoid_id)
                if solenoid:
                    db_group.solenoids.append(solenoid)

            self.db.commit()
            self.db.refresh(db_group)
            return db_group
        except SQLAlchemyError as e:
            logger.error(f"Error updating group: {str(e)}")
            self.db.rollback()
            return None

    def delete_group(self, group_id: int) -> bool:
        try:
            group = self.get_group(group_id)
            if group:
                self.db.delete(group)
                self.db.commit()
                return True
            return False
        except SQLAlchemyError as e:
            logger.error(f"Error deleting group: {str(e)}")
            self.db.rollback()
            return False

    # Schedule Operations
    def create_schedule(self, schedule: schemas.ScheduleCreate) -> Optional[models.Schedule]:
        try:
            schedule_data = schedule.model_dump(exclude={'time_slots'})
            target_id = schedule_data.pop('target_id')
            
            db_schedule = models.Schedule(**schedule_data)
            
            if schedule.target_type == 'solenoid':
                db_schedule.solenoid_id = target_id
            else:
                db_schedule.group_id = target_id

            self.db.add(db_schedule)
            self.db.flush()

            # Add time slots
            for slot in schedule.time_slots:
                db_slot = models.ScheduleTimeSlot(
                    schedule_id=db_schedule.id,
                    **slot.model_dump()
                )
                self.db.add(db_slot)

            self.db.commit()
            self.db.refresh(db_schedule)
            return db_schedule
        except SQLAlchemyError as e:
            logger.error(f"Error creating schedule: {str(e)}")
            self.db.rollback()
            return None

    def get_schedule(self, schedule_id: int) -> Optional[models.Schedule]:
        return self.db.query(models.Schedule).filter(
            models.Schedule.id == schedule_id
        ).first()

    def get_schedules(self) -> List[models.Schedule]:
        return self.db.query(models.Schedule).all()

    def update_schedule(self, schedule_id: int, schedule: schemas.ScheduleUpdate) -> Optional[models.Schedule]:
        try:
            db_schedule = self.get_schedule(schedule_id)
            if not db_schedule:
                return None

            # Update basic fields
            update_data = schedule.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                if key != 'time_slots' and value is not None:
                    setattr(db_schedule, key, value)

            # Update time slots if provided
            if schedule.time_slots is not None:
                # Remove existing slots
                self.db.query(models.ScheduleTimeSlot).filter(
                    models.ScheduleTimeSlot.schedule_id == schedule_id
                ).delete()
                
                # Add new slots
                for slot in schedule.time_slots:
                    db_slot = models.ScheduleTimeSlot(
                        schedule_id=schedule_id,
                        **slot.model_dump()
                    )
                    self.db.add(db_slot)

            self.db.commit()
            self.db.refresh(db_schedule)
            return db_schedule
        except SQLAlchemyError as e:
            logger.error(f"Error updating schedule: {str(e)}")
            self.db.rollback()
            return None

    def delete_schedule(self, schedule_id: int) -> bool:
        try:
            schedule = self.get_schedule(schedule_id)
            if schedule:
                self.db.delete(schedule)
                self.db.commit()
                return True
            return False
        except SQLAlchemyError as e:
            logger.error(f"Error deleting schedule: {str(e)}")
            self.db.rollback()
            return False
