from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta
import logging
from typing import List, Optional, Dict
from collections import defaultdict

from ..models import database_models as models
from ..services.ha_service import HomeAssistantService
from ..core.config import settings

logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(self, scheduler: BackgroundScheduler, ha_service: HomeAssistantService):
        self.scheduler = scheduler
        self.ha_service = ha_service
        self.running_jobs: Dict[str, List[str]] = defaultdict(list)  # solenoid_id -> [job_ids]

    def _get_job_id(self, schedule_id: int, slot_id: int, action: str) -> str:
        """Generate a unique job ID"""
        return f"schedule_{schedule_id}_slot_{slot_id}_{action}"

    def _parse_days_of_week(self, days_str: str) -> List[str]:
        """Convert days string to list of day numbers (0-6, where 0 is Monday)"""
        day_map = {
            'MON': '0', 'TUE': '1', 'WED': '2', 'THU': '3',
            'FRI': '4', 'SAT': '5', 'SUN': '6'
        }
        return [day_map[day] for day in days_str.split(',') if day in day_map]

    def _get_solenoid_entities(self, schedule: models.Schedule) -> List[str]:
        """Get list of entity_ids for a schedule (either single solenoid or group)"""
        if schedule.target_type == 'solenoid' and schedule.solenoid:
            return [schedule.solenoid.entity_id]
        elif schedule.target_type == 'group' and schedule.group:
            # If sequential watering is enabled for the group, maintain order
            if schedule.group.sequential_watering:
                return [s.entity_id for s in sorted(
                    schedule.group.solenoids,
                    key=lambda x: (x.sequence_order or float('inf'), x.id)
                ) if s.is_active]
            return [s.entity_id for s in schedule.group.solenoids if s.is_active]
        return []

    async def _check_conditions(self, conditions: List[models.ScheduleCondition]) -> bool:
        """Check if all conditions are met for a schedule"""
        for condition in conditions:
            try:
                state = await self.ha_service.get_entity_state(condition.entity_id)
                
                if condition.condition_type == 'state':
                    if not self._compare_values(state, condition.operator, condition.value):
                        return False
                elif condition.condition_type == 'numeric':
                    try:
                        num_state = float(state)
                        num_value = float(condition.value)
                        if not self._compare_values(num_state, condition.operator, num_value):
                            return False
                    except ValueError:
                        logger.error(f"Invalid numeric comparison: {state} {condition.operator} {condition.value}")
                        return False
                # Add template support if needed
            except Exception as e:
                logger.error(f"Error checking condition: {str(e)}")
                return False
        return True

    def _compare_values(self, val1, operator: str, val2):
        """Compare two values using the specified operator"""
        ops = {
            '==': lambda x, y: x == y,
            '!=': lambda x, y: x != y,
            '>': lambda x, y: x > y,
            '<': lambda x, y: x < y,
            '>=': lambda x, y: x >= y,
            '<=': lambda x, y: x <= y,
            'contains': lambda x, y: y in x
        }
        return ops.get(operator, lambda x, y: False)(val1, val2)

    async def execute_watering_action(
        self,
        action: str,
        entity_ids: List[str],
        schedule_id: int,
        is_sequential: bool = False
    ) -> None:
        """Execute watering action on specified entities"""
        if action not in ['turn_on', 'turn_off']:
            logger.error(f"Invalid action: {action}")
            return

        if is_sequential and action == 'turn_on':
            # For sequential watering, run one zone at a time
            for entity_id in entity_ids:
                try:
                    await self.ha_service.control_switch(entity_id, 'turn_on')
                    self.running_jobs[entity_id].append(str(schedule_id))
                    logger.info(f"Started {entity_id} for schedule {schedule_id}")
                    
                    # Wait for this zone to finish before starting the next
                    duration = self._get_zone_duration(schedule_id, entity_id)
                    if duration:
                        await asyncio.sleep(duration * 60)
                    
                    await self.ha_service.control_switch(entity_id, 'turn_off')
                    self.running_jobs[entity_id].remove(str(schedule_id))
                except Exception as e:
                    logger.error(f"Failed to control {entity_id}: {str(e)}")
        else:
            # For parallel watering or turn_off actions
            for entity_id in entity_ids:
                try:
                    await self.ha_service.control_switch(entity_id, action)
                    if action == 'turn_on':
                        self.running_jobs[entity_id].append(str(schedule_id))
                    else:
                        self.running_jobs[entity_id].remove(str(schedule_id))
                    logger.info(f"Successfully executed {action} for {entity_id}")
                except Exception as e:
                    logger.error(f"Failed to {action} {entity_id}: {str(e)}")

    def _get_zone_duration(self, schedule_id: int, entity_id: str) -> Optional[int]:
        """Get the duration for a specific zone in a schedule"""
        # Implement logic to get duration from schedule configuration
        # This is a placeholder - actual implementation would fetch from database
        return None

    def add_or_update_schedule(self, schedule: models.Schedule) -> bool:
        """Add or update jobs for a schedule"""
        try:
            # Remove existing jobs for this schedule
            self.remove_schedule(schedule.id)

            if not schedule.is_enabled:
                logger.info(f"Schedule {schedule.id} is disabled, skipping job creation")
                return True

            entity_ids = self._get_solenoid_entities(schedule)
            if not entity_ids:
                logger.error(f"No valid entities found for schedule {schedule.id}")
                return False

            is_sequential = (
                schedule.target_type == 'group' and 
                schedule.group and 
                schedule.group.sequential_watering
            )

            # Sort time slots by priority (P1 > P2 > MANUAL)
            for slot in sorted(schedule.time_slots, key=lambda x: schedule.priority):
                start_job_id = self._get_job_id(schedule.id, slot.id, "start")
                stop_job_id = self._get_job_id(schedule.id, slot.id, "stop")
                
                # Parse time and days
                hour, minute = slot.start_time.hour, slot.start_time.minute
                days_of_week = self._parse_days_of_week(slot.days_of_week)
                
                if not days_of_week:
                    logger.error(f"No valid days found for slot {slot.id}")
                    continue

                # Create start job
                self.scheduler.add_job(
                    func=self.execute_watering_action,
                    trigger=CronTrigger(
                        day_of_week=','.join(days_of_week),
                        hour=hour,
                        minute=minute
                    ),
                    id=start_job_id,
                    name=f"Start {schedule.name} - Slot {slot.id}",
                    args=[
                        'turn_on',
                        entity_ids,
                        schedule.id,
                        is_sequential
                    ],
                    replace_existing=True,
                    misfire_grace_time=300  # 5 minutes grace time
                )

                if not is_sequential:
                    # For non-sequential, schedule stop time
                    stop_time = (
                        datetime.combine(datetime.today(), slot.start_time) +
                        timedelta(minutes=slot.duration_minutes)
                    ).time()

                    self.scheduler.add_job(
                        func=self.execute_watering_action,
                        trigger=CronTrigger(
                            day_of_week=','.join(days_of_week),
                            hour=stop_time.hour,
                            minute=stop_time.minute
                        ),
                        id=stop_job_id,
                        name=f"Stop {schedule.name} - Slot {slot.id}",
                        args=['turn_off', entity_ids, schedule.id, False],
                        replace_existing=True,
                        misfire_grace_time=300
                    )

                logger.info(
                    f"Created jobs for schedule {schedule.id} slot {slot.id}: "
                    f"start at {slot.start_time}, duration {slot.duration_minutes}min"
                )

            return True

        except Exception as e:
            logger.error(f"Error creating schedule jobs: {str(e)}")
            return False

    def remove_schedule(self, schedule_id: int) -> None:
        """Remove all jobs for a schedule"""
        try:
            jobs = self.scheduler.get_jobs()
            for job in jobs:
                if job.id.startswith(f"schedule_{schedule_id}_"):
                    self.scheduler.remove_job(job.id)
            logger.info(f"Removed all jobs for schedule {schedule_id}")
        except Exception as e:
            logger.error(f"Error removing schedule jobs: {str(e)}")

    def run_schedule_now(self, schedule: models.Schedule) -> bool:
        """Manually run a schedule immediately"""
        try:
            entity_ids = self._get_solenoid_entities(schedule)
            if not entity_ids:
                logger.error(f"No valid entities found for schedule {schedule.id}")
                return False

            is_sequential = (
                schedule.target_type == 'group' and 
                schedule.group and 
                schedule.group.sequential_watering
            )

            # Execute for each time slot
            for slot in schedule.time_slots:
                # Start watering
                self.execute_watering_action('turn_on', entity_ids, schedule.id, is_sequential)
                
                if not is_sequential:
                    # Schedule stop after duration
                    self.scheduler.add_job(
                        func=self.execute_watering_action,
                        trigger='date',
                        run_date=datetime.now() + timedelta(minutes=slot.duration_minutes),
                        id=f"manual_stop_{schedule.id}_{slot.id}_{datetime.now().timestamp()}",
                        args=['turn_off', entity_ids, schedule.id, False]
                    )

            return True

        except Exception as e:
            logger.error(f"Error running schedule manually: {str(e)}")
            return False

    def get_active_jobs(self) -> dict:
        """Get currently active jobs"""
        return dict(self.running_jobs)
