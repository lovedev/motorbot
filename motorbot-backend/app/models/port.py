"""
Port model for USB port discovery and tracking
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.db import Base


class Port(Base):
    """
    Represents a USB port connection for motor communication.

    Attributes:
        id: Unique identifier
        port_name: System port name (e.g., "COM3", "/dev/ttyUSB0")
        device_id: USB device identifier
        vendor_id: USB vendor ID
        product_id: USB product ID
        description: Human-readable port description
        is_active: Whether the port is currently connected
        is_assigned: Whether the port is assigned to a motor
        detected_at: Timestamp when port was first detected
        last_updated: Last update timestamp
        motors: Relationship to Motor objects using this port
    """

    __tablename__ = "ports"

    id = Column(Integer, primary_key=True, index=True)
    port_name = Column(String(50), unique=True, index=True, nullable=False)
    device_id = Column(String(100), nullable=True)
    vendor_id = Column(String(10), nullable=True)
    product_id = Column(String(10), nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    is_assigned = Column(Boolean, default=False, index=True)
    detected_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    motors = relationship("Motor", back_populates="port", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Port(id={self.id}, port_name='{self.port_name}', is_active={self.is_active})>"
