"""Pydantic schemas for MotorConfiguration model"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class MotorConfigBase(BaseModel):
    """Base motor configuration schema"""
    min_angle: float = Field(0.0, description="Minimum allowed angle (degrees)")
    max_angle: float = Field(360.0, description="Maximum allowed angle (degrees)")
    default_speed: float = Field(50.0, ge=0, le=100, description="Default speed (0-100%)")
    default_torque: float = Field(50.0, ge=0, le=100, description="Default torque (0-100%)")
    acceleration: float = Field(10.0, description="Acceleration rate (degrees/sec²)")
    deceleration: float = Field(10.0, description="Deceleration rate (degrees/sec²)")
    timeout: int = Field(5000, description="Motor timeout (milliseconds)")


class MotorConfigCreate(MotorConfigBase):
    """Schema for creating motor configuration"""
    custom_params: Optional[dict] = Field(None, description="Custom parameters")


class MotorConfigUpdate(BaseModel):
    """Schema for updating motor configuration"""
    min_angle: Optional[float] = None
    max_angle: Optional[float] = None
    default_speed: Optional[float] = None
    default_torque: Optional[float] = None
    acceleration: Optional[float] = None
    deceleration: Optional[float] = None
    timeout: Optional[int] = None
    custom_params: Optional[dict] = None


class MotorConfigResponse(MotorConfigBase):
    """Schema for motor configuration response"""
    id: int
    motor_id: int
    custom_params: Optional[dict]
    created_at: datetime
    last_updated: datetime

    class Config:
        from_attributes = True


class MotorConfigDetailResponse(MotorConfigResponse):
    """Detailed configuration response"""
    motor_name: Optional[str] = None
    presets: Optional[list[str]] = Field(default_factory=list, description="Available preset names")


class ConfigPreset(BaseModel):
    """Configuration preset"""
    name: str = Field(..., description="Preset name")
    min_angle: float
    max_angle: float
    default_speed: float
    default_torque: float
    acceleration: float
    deceleration: float
    timeout: int
