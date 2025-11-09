"""
Motor model for tracking individual motors in the SO-ARM 101 robot
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.db import Base


class Motor(Base):
    """
    Represents a single motor in the SO-ARM 101 robot arm.

    Attributes:
        id: Unique motor identifier (1-12)
        name: Motor name (e.g., "Shoulder Motor", "Elbow Motor")
        motor_index: Position in robot arm (0-11)
        port_id: Foreign key to Port table
        port: Relationship to Port object
        model: Motor model name
        serial_number: Motor serial number
        max_speed: Maximum RPM
        max_torque: Maximum torque (Nm)
        is_calibrated: Calibration status
        is_functional: Operational status
        created_at: Creation timestamp
        last_updated: Last update timestamp
        configurations: Relationship to MotorConfiguration objects
        telemetry: Relationship to TelemetryDataPoint objects
        test_events: Relationship to MotorTestEvent objects
    """

    __tablename__ = "motors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    motor_index = Column(Integer, nullable=False, index=True)  # 0-11 for 12 motors
    port_id = Column(Integer, ForeignKey("ports.id"), nullable=True, index=True)
    model = Column(String(100), nullable=True)
    serial_number = Column(String(100), unique=True, nullable=True)
    max_speed = Column(Float, nullable=True)  # RPM
    max_torque = Column(Float, nullable=True)  # Nm
    is_calibrated = Column(Boolean, default=False, index=True)
    is_functional = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    port = relationship("Port", back_populates="motors")
    configurations = relationship("MotorConfiguration", back_populates="motor", cascade="all, delete-orphan")
    telemetry = relationship("TelemetryDataPoint", back_populates="motor", cascade="all, delete-orphan")
    test_events = relationship("MotorTestEvent", back_populates="motor", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Motor(id={self.id}, name='{self.name}', motor_index={self.motor_index})>"
