"""Pydantic schemas for Port model"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class PortBase(BaseModel):
    """Base port schema"""
    port_name: str = Field(..., description="System port name (e.g., COM3, /dev/ttyUSB0)")
    vendor_id: Optional[str] = Field(None, description="USB vendor ID")
    product_id: Optional[str] = Field(None, description="USB product ID")
    description: Optional[str] = Field(None, description="Port description")


class PortCreate(PortBase):
    """Schema for creating a port"""
    is_active: bool = Field(True, description="Whether port is active")
    is_assigned: bool = Field(False, description="Whether port is assigned to a motor")


class PortUpdate(BaseModel):
    """Schema for updating a port"""
    is_active: Optional[bool] = None
    is_assigned: Optional[bool] = None
    description: Optional[str] = None


class PortResponse(PortBase):
    """Schema for port response"""
    id: int
    device_id: Optional[str]
    is_active: bool
    is_assigned: bool
    detected_at: datetime
    last_updated: datetime

    class Config:
        from_attributes = True


class PortListResponse(BaseModel):
    """Response for list of ports"""
    ports: list[PortResponse]
    total: int = Field(..., description="Total number of ports")


class PortDiscoveryResponse(BaseModel):
    """Response for port discovery"""
    ports: list[PortResponse]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    available_count: int
    assigned_count: int
