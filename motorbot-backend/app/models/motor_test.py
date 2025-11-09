"""
Motor test event model for tracking test results
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.db import Base


class MotorTestEvent(Base):
    """
    Records test events and their results for motors.

    Attributes:
        id: Unique test event identifier
        motor_id: Foreign key to Motor table
        motor: Relationship to Motor object
        test_type: Type of test (e.g., "communication", "speed", "torque", "temperature")
        test_name: Human-readable test name
        status: Test result status (e.g., "passed", "failed", "warning")
        success: Whether the test passed
        error_message: Error message if test failed
        max_value: Maximum measured value during test
        min_value: Minimum measured value during test
        avg_value: Average measured value during test
        test_started_at: When test started
        test_completed_at: When test completed
        duration: Test duration (milliseconds)
    """

    __tablename__ = "motor_test_events"

    id = Column(Integer, primary_key=True, index=True)
    motor_id = Column(Integer, ForeignKey("motors.id"), nullable=False, index=True)
    test_type = Column(String(50), nullable=False, index=True)
    test_name = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False, index=True)
    success = Column(Boolean, nullable=False)
    error_message = Column(Text, nullable=True)
    max_value = Column(Float, nullable=True)
    min_value = Column(Float, nullable=True)
    avg_value = Column(Float, nullable=True)
    test_started_at = Column(DateTime, nullable=False)
    test_completed_at = Column(DateTime, nullable=False)
    duration = Column(Integer, nullable=True)  # milliseconds
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    motor = relationship("Motor", back_populates="test_events")

    def __repr__(self) -> str:
        return f"<MotorTestEvent(id={self.id}, motor_id={self.motor_id}, test_type='{self.test_type}', success={self.success})>"
