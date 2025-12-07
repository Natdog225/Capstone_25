"""Database connection and session management"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
import os
from typing import Generator
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    logger.warning("No DATABASE_URL - database disabled")
    engine = None
    SessionLocal = None
else:
    engine = create_engine(DATABASE_URL, poolclass=NullPool, echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("✓ Database connection initialized")


def get_db() -> Generator[Session, None, None]:
    if SessionLocal is None:
        raise Exception("Database not configured")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    if engine is None:
        return
    from app.models.database_models import Base

    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✓ Database tables created")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


def check_db_connection() -> bool:
    if engine is None:
        return False
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Connection failed: {e}")
        return False
