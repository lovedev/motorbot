"""Pydantic schemas for TelemetryDataPoint model"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class TelemetryBase(BaseModel):
    """Base telemetry schema"""
    current_angle: Optional[float] = Field(None, description="Current position (degrees)")
    target_angle: Optional[float] = Field(None, description="Target position (degrees)")
    current_speed: Optional[float] = Field(None, description="Current speed (RPM or %)")
    current_torque: Optional[float] = Field(None, description="Current torque (Nm or %)")
    temperature: Optional[float] = Field(None, description="Motor temperature (Celsius)")
    voltage: Optional[float] = Field(None, description="Supply voltage (Volts)")
    current: Optional[float] = Field(None, description="Current consumption (Amperes)")
    error_code: Optional[int] = Field(None, description="Error code if any")


class TelemetryCreate(TelemetryBase):
    """Schema for creating telemetry data point"""
    motor_id: int


class TelemetryResponse(TelemetryBase):
    """Schema for telemetry response"""
    id: int
    motor_id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class TelemetryListResponse(BaseModel):
    """Response for list of telemetry data"""
    data_points: list[TelemetryResponse]
    motor_id: int
    total: int
    latest_timestamp: Optional[datetime]


class TelemetryStreamMessage(TelemetryBase):
    """Schema for WebSocket telemetry stream"""
    motor_id: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field("normal", description="Status: normal, warning, error")


class DashboardTelemetryMessage(BaseModel):
    """Schema for dashboard telemetry stream (all motors)"""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    motors: dict[int, TelemetryStreamMessage]
    overall_status: str = Field("normal", description="Overall system status")


class TelemetryStatistics(BaseModel):
    """Telemetry statistics for a motor"""
    motor_id: int
    motor_name: str
    data_points_count: int

    # Temperature stats
    avg_temperature: Optional[float] = None
    max_temperature: Optional[float] = None
    min_temperature: Optional[float] = None

    # Speed stats
    avg_speed: Optional[float] = None
    max_speed: Optional[float] = None
    min_speed: Optional[float] = None

    # Torque stats
    avg_torque: Optional[float] = None
    max_torque: Optional[float] = None

    # Time range
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    class Config:
        from_attributes = True
