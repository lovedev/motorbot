"""Pydantic schemas for Motor model"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class MotorBase(BaseModel):
    """Base motor schema"""
    name: str = Field(..., description="Motor name")
    motor_index: int = Field(..., ge=0, le=11, description="Motor index (0-11)")
    model: Optional[str] = Field(None, description="Motor model name")
    serial_number: Optional[str] = Field(None, description="Motor serial number")
    max_speed: Optional[float] = Field(None, description="Maximum RPM")
    max_torque: Optional[float] = Field(None, description="Maximum torque (Nm)")


class MotorCreate(MotorBase):
    """Schema for creating a motor"""
    port_id: Optional[int] = Field(None, description="Port ID")


class MotorUpdate(BaseModel):
    """Schema for updating a motor"""
    name: Optional[str] = None
    port_id: Optional[int] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    max_speed: Optional[float] = None
    max_torque: Optional[float] = None
    is_calibrated: Optional[bool] = None
    is_functional: Optional[bool] = None


class MotorResponse(MotorBase):
    """Schema for motor response"""
    id: int
    port_id: Optional[int]
    is_calibrated: bool
    is_functional: bool
    created_at: datetime
    last_updated: datetime

    class Config:
        from_attributes = True


class MotorListResponse(BaseModel):
    """Response for list of motors"""
    motors: list[MotorResponse]
    total: int
    calibrated_count: int
    functional_count: int


class MotorDetailResponse(MotorResponse):
    """Detailed motor response with related data"""
    port_name: Optional[str] = None
    configuration: Optional[dict] = None
    latest_telemetry: Optional[dict] = None
    test_count: int = 0
    operation_count: int = 0


class MotorStatusResponse(BaseModel):
    """Motor status response"""
    motor_id: int
    name: str
    is_calibrated: bool
    is_functional: bool
    last_updated: datetime
    current_angle: Optional[float] = None
    current_speed: Optional[float] = None
    temperature: Optional[float] = None


class AllMotorsStatusResponse(BaseModel):
    """Response for all motors status"""
    motors: list[MotorStatusResponse]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    total_motors: int
    calibrated_motors: int
    functional_motors: int
