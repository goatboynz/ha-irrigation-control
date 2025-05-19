import os
import logging
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import SQLAlchemyError

from models.database_models import Base
from core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """Initialize the database schema"""
    try:
        # Ensure the database directory exists
        db_dir = "/data/db"
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
            logger.info(f"Created database directory: {db_dir}")

        # Create database engine
        engine = create_engine(
            settings.DATABASE_URL,
            connect_args={"check_same_thread": False}
        )

        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Successfully created database tables")

        # Also create APScheduler jobs database
        scheduler_engine = create_engine(
            settings.SCHEDULER_DB_URL,
            connect_args={"check_same_thread": False}
        )
        # APScheduler will create its tables automatically when needed
        logger.info("Initialized APScheduler database")

        # Log table information
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        logger.info(f"Available tables: {', '.join(tables)}")

        return True

    except SQLAlchemyError as e:
        logger.error(f"Database initialization error: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during database initialization: {str(e)}")
        return False

if __name__ == "__main__":
    success = init_db()
    if not success:
        logger.error("Failed to initialize database")
        exit(1)
    logger.info("Database initialization completed successfully")
