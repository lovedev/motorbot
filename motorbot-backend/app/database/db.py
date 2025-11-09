"""
Database configuration and session management for Motor Setup and Monitoring Dashboard
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator
import os
from pathlib import Path

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./motorbot.db")

# Ensure database file is created in the correct location
if DATABASE_URL.startswith("sqlite:///"):
    db_path = DATABASE_URL.replace("sqlite:///", "")
    # Create parent directories if they don't exist
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

# Create engine with appropriate settings for SQLite
if "sqlite" in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Enable foreign keys for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
else:
    # For other databases (PostgreSQL, MySQL, etc.)
    engine = create_engine(
        DATABASE_URL,
        echo=os.getenv("SQL_ECHO", "false").lower() == "true",
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.

    Usage in FastAPI routes:
        @app.get("/items")
        async def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database by creating all tables.

    This should be called once at application startup.
    """
    # Import all models here to ensure they are registered with Base
    from app.models import port, motor, motor_config, telemetry, operation_log, motor_test

    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables initialized successfully")


def drop_db() -> None:
    """
    Drop all tables from the database.

    WARNING: This will delete all data. Only use for testing.
    """
    Base.metadata.drop_all(bind=engine)
    print("✓ All database tables dropped")
