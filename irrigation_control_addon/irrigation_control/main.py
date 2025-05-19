from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
import os

from .core.config import settings
from .api import entities_api, groups_api, schedules_api, settings_api
from .models.database_models import Base

app = FastAPI(
    title="Irrigation Control",
    description="Home Assistant addon for advanced irrigation control",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:////data/db/irrigation_addon.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Initialize scheduler with SQLite job store
jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:////data/db/apscheduler_jobs.sqlite')
}
scheduler = BackgroundScheduler(jobstores=jobstores)

def init_db():
    Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(entities_api.router, prefix="/api", tags=["entities"])
app.include_router(groups_api.router, prefix="/api", tags=["groups"])
app.include_router(schedules_api.router, prefix="/api", tags=["schedules"])
app.include_router(settings_api.router, prefix="/api", tags=["settings"])

# Root route
@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    # Ensure we have the supervisor token
    if not os.getenv("SUPERVISOR_TOKEN"):
        raise ValueError("SUPERVISOR_TOKEN environment variable is not set")
    
    # Initialize database
    init_db()
    
    # Start the scheduler
    scheduler.start()

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()
