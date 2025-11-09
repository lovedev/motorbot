"""
Telemetry data point model for real-time motor monitoring
"""

from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.db import Base


class TelemetryDataPoint(Base):
    """
    Stores real-time telemetry data from motors.

    Attributes:
        id: Unique data point identifier
        motor_id: Foreign key to Motor table
        motor: Relationship to Motor object
        current_angle: Current position (degrees)
        target_angle: Target position (degrees)
        current_speed: Current speed (RPM or %)
        current_torque: Current torque (Nm or %)
        temperature: Motor temperature (Celsius)
        voltage: Supply voltage (Volts)
        current: Current consumption (Amperes)
        error_code: Error status code if any
        timestamp: When telemetry was recorded
    """

    __tablename__ = "telemetry_data_points"

    id = Column(Integer, primary_key=True, index=True)
    motor_id = Column(Integer, ForeignKey("motors.id"), nullable=False, index=True)
    current_angle = Column(Float, nullable=True)
    target_angle = Column(Float, nullable=True)
    current_speed = Column(Float, nullable=True)
    current_torque = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)
    voltage = Column(Float, nullable=True)
    current = Column(Float, nullable=True)
    error_code = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    motor = relationship("Motor", back_populates="telemetry")

    def __repr__(self) -> str:
        return f"<TelemetryDataPoint(id={self.id}, motor_id={self.motor_id}, timestamp={self.timestamp})>"
