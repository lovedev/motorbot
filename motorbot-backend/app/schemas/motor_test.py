"""Pydantic schemas for MotorTestEvent model"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class MotorTestBase(BaseModel):
    """Base motor test schema"""
    test_type: str = Field(..., description="Type of test (communication, speed, torque, temperature)")
    test_name: str = Field(..., description="Test name")
    status: str = Field(..., description="Test status (passed, failed, warning)")
    success: bool = Field(..., description="Whether test passed")
    error_message: Optional[str] = Field(None, description="Error message if failed")


class MotorTestCreate(MotorTestBase):
    """Schema for creating motor test"""
    motor_id: int
    max_value: Optional[float] = None
    min_value: Optional[float] = None
    avg_value: Optional[float] = None
    test_started_at: datetime
    test_completed_at: datetime
    duration: Optional[int] = None


class MotorTestResponse(MotorTestBase):
    """Schema for motor test response"""
    id: int
    motor_id: int
    max_value: Optional[float]
    min_value: Optional[float]
    avg_value: Optional[float]
    test_started_at: datetime
    test_completed_at: datetime
    duration: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class MotorTestListResponse(BaseModel):
    """Response for list of motor tests"""
    tests: list[MotorTestResponse]
    motor_id: int
    total: int
    passed_count: int
    failed_count: int


class MotorTestDetailResponse(MotorTestResponse):
    """Detailed motor test response"""
    motor_name: Optional[str] = None
    test_duration_seconds: Optional[float] = None


class TestExecutionRequest(BaseModel):
    """Request to execute a test"""
    test_type: str = Field(..., description="Type of test to execute")
    test_name: Optional[str] = Field(None, description="Custom test name")
    timeout: int = Field(30000, description="Test timeout (milliseconds)")


class TestExecutionResponse(BaseModel):
    """Response from test execution start"""
    test_id: int
    motor_id: int
    test_type: str
    status: str = "running"
    started_at: datetime
    message: str = "Test execution started"


class TestResult(BaseModel):
    """Individual test result"""
    test_name: str
    status: str
    passed: bool
    value: Optional[float] = None
    expected: Optional[float] = None
    tolerance: Optional[float] = None
    message: Optional[str] = None


class TestResultsResponse(BaseModel):
    """Complete test results"""
    motor_id: int
    motor_name: str
    test_type: str
    overall_status: str = "completed"
    results: list[TestResult]
    total_tests: int
    passed_tests: int
    failed_tests: int
    duration_seconds: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TestHistoryResponse(BaseModel):
    """Test history summary"""
    motor_id: int
    motor_name: str
    total_tests_run: int
    total_passed: int
    total_failed: int
    success_rate: float

    # Tests by type
    communication_tests: int = 0
    communication_passed: int = 0

    speed_tests: int = 0
    speed_passed: int = 0

    torque_tests: int = 0
    torque_passed: int = 0

    temperature_tests: int = 0
    temperature_passed: int = 0

    # Last test info
    last_test_type: Optional[str] = None
    last_test_status: Optional[str] = None
    last_test_time: Optional[datetime] = None
