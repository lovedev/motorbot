"""Motor testing API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.services.test_service import TestService
from app.services.motor_service import MotorService
from app.schemas.motor_test import (
    MotorTestResponse,
    MotorTestListResponse,
    MotorTestDetailResponse,
    TestExecutionRequest,
    TestExecutionResponse,
    TestHistoryResponse,
)
from datetime import datetime
from typing import Optional

router = APIRouter(prefix="/api/motors", tags=["Motor Testing"])


@router.get("/{motor_id}/tests/available")
async def get_available_tests(motor_id: int, db: Session = Depends(get_db)):
    """
    Get available test types for a motor.

    Path Parameters:
        motor_id: Motor ID

    Returns:
        Dictionary of available test types and specifications
    """
    motor = MotorService.get_motor_by_id(db, motor_id)
    if not motor:
        raise HTTPException(status_code=404, detail=f"Motor {motor_id} not found")

    tests = TestService.get_available_tests()

    return {
        "motor_id": motor_id,
        "motor_name": motor.name,
        "available_tests": tests,
        "test_count": len(tests),
    }


@router.post("/{motor_id}/tests/execute")
async def execute_test(
    motor_id: int,
    test_request: TestExecutionRequest,
    db: Session = Depends(get_db)
):
    """
    Start a test execution on a motor.

    Path Parameters:
        motor_id: Motor ID

    Request Body:
        test_type: Type of test (communication, speed, torque, temperature)
        test_name: Custom test name (optional)
        timeout: Test timeout in milliseconds

    Returns:
        Test execution response with status
    """
    motor = MotorService.get_motor_by_id(db, motor_id)
    if not motor:
        raise HTTPException(status_code=404, detail=f"Motor {motor_id} not found")

    # Get test specification
    test_spec = TestService.get_test_spec(test_request.test_type)
    if not test_spec:
        raise HTTPException(status_code=400, detail=f"Unknown test type: {test_request.test_type}")

    # Get simulator for this test type
    simulator = TestService.get_simulator_for_test(test_request.test_type)
    if not simulator:
        raise HTTPException(status_code=500, detail=f"No simulator for test type: {test_request.test_type}")

    # Run simulation and get results
    test_result = simulator(motor_id)

    # Create test event
    test_name = test_request.test_name or test_spec['name']
    start_time = datetime.utcnow()
    end_time = datetime.utcnow()

    test_event = TestService.create_test_event(
        db,
        motor_id,
        test_request.test_type,
        test_name,
        test_result['status'],
        test_result['success'],
        error_message=test_result.get('error_message'),
        max_value=test_result.get('max_value'),
        min_value=test_result.get('min_value'),
        avg_value=test_result.get('avg_value'),
        start_time=start_time,
        end_time=end_time,
    )

    return TestExecutionResponse(
        test_id=test_event.id,
        motor_id=motor_id,
        test_type=test_request.test_type,
        status="completed",
        started_at=start_time,
        message=f"Test execution completed: {test_result['status']}",
    )


@router.get("/{motor_id}/tests/{test_id}", response_model=MotorTestDetailResponse)
async def get_test_result(
    motor_id: int,
    test_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific test result.

    Path Parameters:
        motor_id: Motor ID
        test_id: Test event ID

    Returns:
        Detailed test result information
    """
    motor = MotorService.get_motor_by_id(db, motor_id)
    if not motor:
        raise HTTPException(status_code=404, detail=f"Motor {motor_id} not found")

    test_event = TestService.get_test_by_id(db, test_id)
    if not test_event or test_event.motor_id != motor_id:
        raise HTTPException(status_code=404, detail=f"Test {test_id} not found")

    duration_seconds = (
        test_event.duration / 1000 if test_event.duration else 0
    )

    return MotorTestDetailResponse(
        id=test_event.id,
        motor_id=test_event.motor_id,
        motor_name=motor.name,
        test_type=test_event.test_type,
        test_name=test_event.test_name,
        status=test_event.status,
        success=test_event.success,
        error_message=test_event.error_message,
        max_value=test_event.max_value,
        min_value=test_event.min_value,
        avg_value=test_event.avg_value,
        test_started_at=test_event.test_started_at,
        test_completed_at=test_event.test_completed_at,
        duration=test_event.duration,
        test_duration_seconds=duration_seconds,
        created_at=test_event.created_at,
    )


@router.get("/{motor_id}/tests", response_model=MotorTestListResponse)
async def get_motor_tests(
    motor_id: int,
    test_type: Optional[str] = Query(None, description="Filter by test type"),
    limit: int = Query(50, ge=1, le=500, description="Max results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: Session = Depends(get_db)
):
    """
    Get test history for a motor.

    Path Parameters:
        motor_id: Motor ID

    Query Parameters:
        test_type: Filter by test type (optional)
        limit: Maximum results
        offset: Pagination offset

    Returns:
        List of test events with statistics
    """
    motor = MotorService.get_motor_by_id(db, motor_id)
    if not motor:
        raise HTTPException(status_code=404, detail=f"Motor {motor_id} not found")

    tests = TestService.get_motor_tests(db, motor_id, test_type, limit, offset)
    all_tests = TestService.get_motor_tests(db, motor_id, test_type, limit=10000)

    passed = sum(1 for t in all_tests if t.success)
    failed = sum(1 for t in all_tests if not t.success)

    return MotorTestListResponse(
        tests=[
            MotorTestResponse(
                id=t.id,
                motor_id=t.motor_id,
                test_type=t.test_type,
                test_name=t.test_name,
                status=t.status,
                success=t.success,
                error_message=t.error_message,
                max_value=t.max_value,
                min_value=t.min_value,
                avg_value=t.avg_value,
                test_started_at=t.test_started_at,
                test_completed_at=t.test_completed_at,
                duration=t.duration,
                created_at=t.created_at,
            )
            for t in tests
        ],
        motor_id=motor_id,
        total=len(all_tests),
        passed_count=passed,
        failed_count=failed,
    )


@router.get("/{motor_id}/tests/history")
async def get_test_history(
    motor_id: int,
    db: Session = Depends(get_db)
):
    """
    Get test history summary for a motor.

    Path Parameters:
        motor_id: Motor ID

    Returns:
        Test history with success rates and breakdown by type
    """
    motor = MotorService.get_motor_by_id(db, motor_id)
    if not motor:
        raise HTTPException(status_code=404, detail=f"Motor {motor_id} not found")

    history = TestService.get_test_history(db, motor_id)

    return TestHistoryResponse(
        motor_id=motor_id,
        motor_name=motor.name,
        total_tests_run=history['total_tests'],
        total_passed=history['passed_tests'],
        total_failed=history['failed_tests'],
        success_rate=history['success_rate'],
        communication_tests=history['test_type_breakdown'].get('communication', {}).get('total', 0),
        communication_passed=history['test_type_breakdown'].get('communication', {}).get('passed', 0),
        speed_tests=history['test_type_breakdown'].get('speed', {}).get('total', 0),
        speed_passed=history['test_type_breakdown'].get('speed', {}).get('passed', 0),
        torque_tests=history['test_type_breakdown'].get('torque', {}).get('total', 0),
        torque_passed=history['test_type_breakdown'].get('torque', {}).get('passed', 0),
        temperature_tests=history['test_type_breakdown'].get('temperature', {}).get('total', 0),
        temperature_passed=history['test_type_breakdown'].get('temperature', {}).get('passed', 0),
        last_test_type=history.get('last_test_type'),
        last_test_status=history.get('last_test_status'),
        last_test_time=history.get('last_test'),
    )


@router.delete("/{motor_id}/tests/{test_id}", status_code=204)
async def delete_test(
    motor_id: int,
    test_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a test record.

    Path Parameters:
        motor_id: Motor ID
        test_id: Test ID to delete

    Returns:
        No content
    """
    motor = MotorService.get_motor_by_id(db, motor_id)
    if not motor:
        raise HTTPException(status_code=404, detail=f"Motor {motor_id} not found")

    success = TestService.delete_test(db, test_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Test {test_id} not found")

    return None


@router.post("/{motor_id}/tests/run-all")
async def run_all_tests(
    motor_id: int,
    db: Session = Depends(get_db)
):
    """
    Run all available tests on a motor sequentially.

    Path Parameters:
        motor_id: Motor ID

    Returns:
        Results of all tests run
    """
    motor = MotorService.get_motor_by_id(db, motor_id)
    if not motor:
        raise HTTPException(status_code=404, detail=f"Motor {motor_id} not found")

    available_tests = TestService.get_available_tests()
    results = []

    for test_type in available_tests.keys():
        simulator = TestService.get_simulator_for_test(test_type)
        if simulator:
            test_result = simulator(motor_id)
            test_spec = TestService.get_test_spec(test_type)

            test_event = TestService.create_test_event(
                db,
                motor_id,
                test_type,
                test_spec['name'],
                test_result['status'],
                test_result['success'],
                error_message=test_result.get('error_message'),
                max_value=test_result.get('max_value'),
                min_value=test_result.get('min_value'),
                avg_value=test_result.get('avg_value'),
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow(),
            )

            results.append({
                'test_id': test_event.id,
                'test_type': test_type,
                'test_name': test_spec['name'],
                'status': test_result['status'],
                'success': test_result['success'],
            })

    return {
        "motor_id": motor_id,
        "motor_name": motor.name,
        "tests_executed": len(results),
        "timestamp": datetime.utcnow().isoformat(),
        "results": results,
    }
