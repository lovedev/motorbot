"""
Motor configuration model for storing motor setup parameters
"""

from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.db import Base


class MotorConfiguration(Base):
    """
    Stores configuration parameters for each motor.

    Attributes:
        id: Unique configuration identifier
        motor_id: Foreign key to Motor table
        motor: Relationship to Motor object
        min_angle: Minimum allowed angle (degrees)
        max_angle: Maximum allowed angle (degrees)
        default_speed: Default motor speed (0-100%)
        default_torque: Default torque setting (0-100%)
        acceleration: Acceleration rate (degrees/sec²)
        deceleration: Deceleration rate (degrees/sec²)
        timeout: Motor timeout in milliseconds
        custom_params: Additional configuration parameters (JSON)
        created_at: Creation timestamp
        last_updated: Last update timestamp
    """

    __tablename__ = "motor_configurations"

    id = Column(Integer, primary_key=True, index=True)
    motor_id = Column(Integer, ForeignKey("motors.id"), nullable=False, index=True)
    min_angle = Column(Float, default=0.0)
    max_angle = Column(Float, default=360.0)
    default_speed = Column(Float, default=50.0)
    default_torque = Column(Float, default=50.0)
    acceleration = Column(Float, default=10.0)
    deceleration = Column(Float, default=10.0)
    timeout = Column(Integer, default=5000)  # milliseconds
    custom_params = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    motor = relationship("Motor", back_populates="configurations")

    def __repr__(self) -> str:
        return f"<MotorConfiguration(id={self.id}, motor_id={self.motor_id})>"
