"""Pydantic schemas for API request/response validation"""

from app.schemas.port import PortResponse, PortCreate, PortUpdate
from app.schemas.motor import MotorResponse, MotorCreate, MotorUpdate
from app.schemas.motor_config import MotorConfigResponse, MotorConfigCreate, MotorConfigUpdate
from app.schemas.telemetry import TelemetryResponse, TelemetryCreate
from app.schemas.operation_log import OperationLogResponse, OperationLogCreate
from app.schemas.motor_test import MotorTestResponse, MotorTestCreate

__all__ = [
    "PortResponse",
    "PortCreate",
    "PortUpdate",
    "MotorResponse",
    "MotorCreate",
    "MotorUpdate",
    "MotorConfigResponse",
    "MotorConfigCreate",
    "MotorConfigUpdate",
    "TelemetryResponse",
    "TelemetryCreate",
    "OperationLogResponse",
    "OperationLogCreate",
    "MotorTestResponse",
    "MotorTestCreate",
]
