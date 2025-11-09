"""Pydantic schemas for OperationLog model"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class OperationLogBase(BaseModel):
    """Base operation log schema"""
    operation_type: str = Field(..., description="Type of operation")
    status: str = Field(..., description="Operation status")
    description: Optional[str] = Field(None, description="Operation description")
    result: Optional[str] = Field(None, description="Operation result")
    duration: Optional[int] = Field(None, description="Duration (milliseconds)")


class OperationLogCreate(OperationLogBase):
    """Schema for creating operation log"""
    motor_id: int


class OperationLogResponse(OperationLogBase):
    """Schema for operation log response"""
    id: int
    motor_id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class OperationLogListResponse(BaseModel):
    """Response for list of operation logs"""
    logs: list[OperationLogResponse]
    motor_id: int
    total: int
    operation_type: Optional[str] = None


class OperationLogDetailResponse(OperationLogResponse):
    """Detailed operation log response"""
    motor_name: Optional[str] = None


class OperationSummary(BaseModel):
    """Summary of operations for a motor"""
    motor_id: int
    motor_name: str
    total_operations: int
    successful_operations: int
    failed_operations: int

    # Operation types breakdown
    calibration_count: int = 0
    test_count: int = 0
    control_count: int = 0
    configuration_count: int = 0

    # Timing
    first_operation: Optional[datetime] = None
    last_operation: Optional[datetime] = None
    avg_operation_duration: Optional[float] = None  # milliseconds

    class Config:
        from_attributes = True
