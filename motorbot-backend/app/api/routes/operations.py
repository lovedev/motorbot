"""Operation logging API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models.operation_log import OperationLog
from app.services.motor_service import MotorService
from app.schemas.operation_log import (
    OperationLogResponse,
    OperationLogListResponse,
    OperationLogDetailResponse,
    OperationLogCreate,
    OperationSummary,
)
from datetime import datetime
from typing import Optional

router = APIRouter(prefix="/api/motors", tags=["Operation Logging"])


@router.get("/{motor_id}/operations", response_model=OperationLogListResponse)
async def get_motor_operations(
    motor_id: int,
    operation_type: Optional[str] = Query(None, description="Filter by operation type"),
    limit: int = Query(50, ge=1, le=500, description="Max results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: Session = Depends(get_db)
):
    """
    Get operation history for a motor.

    Path Parameters:
        motor_id: Motor ID

    Query Parameters:
        operation_type: Filter by operation type (calibration, test, control, configuration)
        limit: Maximum results
        offset: Pagination offset

    Returns:
        List of operation logs with statistics
    """
    motor = MotorService.get_motor_by_id(db, motor_id)
    if not motor:
        raise HTTPException(status_code=404, detail=f"Motor {motor_id} not found")

    query = db.query(OperationLog).filter(OperationLog.motor_id == motor_id)

    if operation_type:
        query = query.filter(OperationLog.operation_type == operation_type)

    total = query.count()

    logs = query.order_by(OperationLog.timestamp.desc()).offset(offset).limit(limit).all()

    return OperationLogListResponse(
        logs=[
            OperationLogResponse(
                id=log.id,
                motor_id=log.motor_id,
                operation_type=log.operation_type,
                status=log.status,
                description=log.description,
                result=log.result,
                duration=log.duration,
                timestamp=log.timestamp,
            )
            for log in logs
        ],
        motor_id=motor_id,
        total=total,
        operation_type=operation_type,
    )


@router.get("/{motor_id}/operations/{operation_id}", response_model=OperationLogDetailResponse)
async def get_operation(
    motor_id: int,
    operation_id: int,
    db: Session = Depends(get_db)
):
    """
    Get details of a specific operation.

    Path Parameters:
        motor_id: Motor ID
        operation_id: Operation log ID

    Returns:
        Detailed operation log entry
    """
    motor = MotorService.get_motor_by_id(db, motor_id)
    if not motor:
        raise HTTPException(status_code=404, detail=f"Motor {motor_id} not found")

    log = db.query(OperationLog).filter(
        OperationLog.id == operation_id,
        OperationLog.motor_id == motor_id
    ).first()

    if not log:
        raise HTTPException(status_code=404, detail=f"Operation {operation_id} not found")

    return OperationLogDetailResponse(
        id=log.id,
        motor_id=log.motor_id,
        motor_name=motor.name,
        operation_type=log.operation_type,
        status=log.status,
        description=log.description,
        result=log.result,
        duration=log.duration,
        timestamp=log.timestamp,
    )


@router.post("/{motor_id}/operations", response_model=OperationLogResponse, status_code=201)
async def create_operation_log(
    motor_id: int,
    operation_data: OperationLogCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new operation log entry.

    Path Parameters:
        motor_id: Motor ID

    Request Body:
        operation_type: Type of operation (calibration, test, control, configuration)
        status: Status (started, completed, failed)
        description: Operation description
        result: Operation result
        duration: Duration in milliseconds

    Returns:
        Created operation log entry
    """
    motor = MotorService.get_motor_by_id(db, motor_id)
    if not motor:
        raise HTTPException(status_code=404, detail=f"Motor {motor_id} not found")

    try:
        log = OperationLog(
            motor_id=motor_id,
            operation_type=operation_data.operation_type,
            status=operation_data.status,
            description=operation_data.description,
            result=operation_data.result,
            duration=operation_data.duration,
        )
        db.add(log)
        db.commit()
        db.refresh(log)

        return OperationLogResponse(
            id=log.id,
            motor_id=log.motor_id,
            operation_type=log.operation_type,
            status=log.status,
            description=log.description,
            result=log.result,
            duration=log.duration,
            timestamp=log.timestamp,
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Failed to create operation log: {str(e)}")


@router.get("/{motor_id}/operations/summary")
async def get_operations_summary(motor_id: int, db: Session = Depends(get_db)):
    """
    Get operation summary for a motor.

    Path Parameters:
        motor_id: Motor ID

    Returns:
        Summary of operations with breakdown by type
    """
    motor = MotorService.get_motor_by_id(db, motor_id)
    if not motor:
        raise HTTPException(status_code=404, detail=f"Motor {motor_id} not found")

    all_logs = db.query(OperationLog).filter(OperationLog.motor_id == motor_id).all()

    if not all_logs:
        return OperationSummary(
            motor_id=motor_id,
            motor_name=motor.name,
            total_operations=0,
            successful_operations=0,
            failed_operations=0,
        )

    successful = sum(1 for log in all_logs if log.status == "completed")
    failed = sum(1 for log in all_logs if log.status == "failed")

    # Count by operation type
    type_counts = {}
    for log in all_logs:
        if log.operation_type not in type_counts:
            type_counts[log.operation_type] = 0
        type_counts[log.operation_type] += 1

    # Calculate average duration
    durations = [log.duration for log in all_logs if log.duration]
    avg_duration = sum(durations) / len(durations) if durations else None

    # Get first and last operation
    sorted_logs = sorted(all_logs, key=lambda x: x.timestamp)
    first_op = sorted_logs[0].timestamp if sorted_logs else None
    last_op = sorted_logs[-1].timestamp if sorted_logs else None

    return OperationSummary(
        motor_id=motor_id,
        motor_name=motor.name,
        total_operations=len(all_logs),
        successful_operations=successful,
        failed_operations=failed,
        calibration_count=type_counts.get('calibration', 0),
        test_count=type_counts.get('test', 0),
        control_count=type_counts.get('control', 0),
        configuration_count=type_counts.get('configuration', 0),
        first_operation=first_op,
        last_operation=last_op,
        avg_operation_duration=avg_duration,
    )


@router.get("/operations/by-type")
async def get_operations_by_type(
    motor_id: int = Query(..., description="Motor ID"),
    operation_type: str = Query(..., description="Operation type to filter"),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Get operations filtered by type.

    Query Parameters:
        motor_id: Motor ID
        operation_type: Type of operation to filter
        limit: Maximum results

    Returns:
        List of operations of specified type
    """
    motor = MotorService.get_motor_by_id(db, motor_id)
    if not motor:
        raise HTTPException(status_code=404, detail=f"Motor {motor_id} not found")

    logs = db.query(OperationLog).filter(
        OperationLog.motor_id == motor_id,
        OperationLog.operation_type == operation_type
    ).order_by(OperationLog.timestamp.desc()).limit(limit).all()

    return {
        "motor_id": motor_id,
        "motor_name": motor.name,
        "operation_type": operation_type,
        "count": len(logs),
        "operations": [
            {
                "id": log.id,
                "operation_type": log.operation_type,
                "status": log.status,
                "description": log.description,
                "result": log.result,
                "duration": log.duration,
                "timestamp": log.timestamp.isoformat(),
            }
            for log in logs
        ],
    }


@router.get("/operations/by-status")
async def get_operations_by_status(
    motor_id: int = Query(..., description="Motor ID"),
    status: str = Query(..., description="Status filter (started, completed, failed)"),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Get operations filtered by status.

    Query Parameters:
        motor_id: Motor ID
        status: Status to filter (started, completed, failed)
        limit: Maximum results

    Returns:
        List of operations with specified status
    """
    motor = MotorService.get_motor_by_id(db, motor_id)
    if not motor:
        raise HTTPException(status_code=404, detail=f"Motor {motor_id} not found")

    logs = db.query(OperationLog).filter(
        OperationLog.motor_id == motor_id,
        OperationLog.status == status
    ).order_by(OperationLog.timestamp.desc()).limit(limit).all()

    return {
        "motor_id": motor_id,
        "motor_name": motor.name,
        "status_filter": status,
        "count": len(logs),
        "operations": [
            {
                "id": log.id,
                "operation_type": log.operation_type,
                "status": log.status,
                "description": log.description,
                "result": log.result,
                "duration": log.duration,
                "timestamp": log.timestamp.isoformat(),
            }
            for log in logs
        ],
    }


@router.get("/operations/timeline")
async def get_operations_timeline(
    motor_id: int = Query(..., description="Motor ID"),
    hours: int = Query(24, ge=1, le=720, description="Hours to retrieve"),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get operations timeline for a motor.

    Query Parameters:
        motor_id: Motor ID
        hours: Hours to retrieve (default 24)
        limit: Maximum results

    Returns:
        Operations sorted by timestamp with timeline grouping
    """
    motor = MotorService.get_motor_by_id(db, motor_id)
    if not motor:
        raise HTTPException(status_code=404, detail=f"Motor {motor_id} not found")

    from datetime import timedelta
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours)

    logs = db.query(OperationLog).filter(
        OperationLog.motor_id == motor_id,
        OperationLog.timestamp >= start_time,
        OperationLog.timestamp <= end_time
    ).order_by(OperationLog.timestamp.desc()).limit(limit).all()

    # Group by hour
    timeline = {}
    for log in logs:
        hour_key = log.timestamp.replace(minute=0, second=0, microsecond=0).isoformat()
        if hour_key not in timeline:
            timeline[hour_key] = []
        timeline[hour_key].append({
            "id": log.id,
            "operation_type": log.operation_type,
            "status": log.status,
            "description": log.description,
            "result": log.result,
            "duration": log.duration,
            "timestamp": log.timestamp.isoformat(),
        })

    return {
        "motor_id": motor_id,
        "motor_name": motor.name,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "total_operations": len(logs),
        "timeline": timeline,
    }
