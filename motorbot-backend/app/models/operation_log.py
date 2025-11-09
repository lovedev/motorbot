"""
Operation log model for tracking motor operations and user actions
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.db import Base


class OperationLog(Base):
    """
    Records all operations and significant events related to motors.

    Attributes:
        id: Unique log entry identifier
        motor_id: Foreign key to Motor table
        motor: Relationship to Motor object
        operation_type: Type of operation (e.g., "calibration", "test", "control")
        status: Operation status (e.g., "started", "completed", "failed")
        description: Detailed description of the operation
        result: Result/outcome of the operation
        timestamp: When the operation occurred
        duration: Duration of operation (milliseconds)
    """

    __tablename__ = "operation_logs"

    id = Column(Integer, primary_key=True, index=True)
    motor_id = Column(Integer, ForeignKey("motors.id"), nullable=False, index=True)
    operation_type = Column(String(50), nullable=False, index=True)
    status = Column(String(20), nullable=False, index=True)
    description = Column(Text, nullable=True)
    result = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    duration = Column(Integer, nullable=True)  # milliseconds

    # Relationships
    motor = relationship("Motor", foreign_keys=[motor_id])

    def __repr__(self) -> str:
        return f"<OperationLog(id={self.id}, motor_id={self.motor_id}, operation_type='{self.operation_type}')>"
