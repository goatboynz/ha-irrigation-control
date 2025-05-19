from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Base configuration
    APP_NAME: str = "Irrigation Control"
    VERSION: str = "0.1.0"
    
    # Home Assistant integration
    SUPERVISOR_URL: str = "http://supervisor"
    CORE_URL: str = "http://supervisor/core"
    SUPERVISOR_TOKEN: Optional[str] = os.getenv("SUPERVISOR_TOKEN")
    
    # Database
    DATABASE_URL: str = "sqlite:////data/db/irrigation_addon.db"
    SCHEDULER_DB_URL: str = "sqlite:////data/db/apscheduler_jobs.sqlite"
    
    # API Settings
    API_V1_STR: str = "/api"
    
    # Scheduler Settings
    MAX_INSTANCES: int = 3
    TIMEZONE: str = "UTC"
    
    # Irrigation Settings
    MIN_DURATION: int = 1  # minutes
    MAX_DURATION: int = 360  # minutes (6 hours)
    MAX_SLOTS_PER_EVENT: int = 50  # Maximum number of time slots for P1/P2 events
    
    # P1/P2 Event Settings
    P1_ENABLED: bool = True
    P2_ENABLED: bool = True
    P1_MAX_SLOTS: int = 50
    P2_MAX_SLOTS: int = 50
    P1_DEFAULT_PRIORITY: int = 1
    P2_DEFAULT_PRIORITY: int = 2
    
    class Config:
        case_sensitive = True

settings = Settings()
