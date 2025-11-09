"""Telemetry data API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.services.telemetry_service import TelemetryService
from app.services.motor_service import MotorService
from app.schemas.telemetry import (
    TelemetryResponse,
    TelemetryCreate,
    TelemetryListResponse,
    TelemetryStreamMessage,
    DashboardTelemetryMessage,
    TelemetryStatistics,
)
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter(prefix="/api/motors", tags=["Telemetry"])


@router.post("/{motor_id}/telemetry", response_model=TelemetryResponse, status_code=201)
async def record_telemetry(
    motor_id: int,
    telemetry_data: TelemetryCreate,
    db: Session = Depends(get_db)
):
    """
    Record a telemetry data point for a motor.

    Path Parameters:
        motor_id: Motor ID

    Request Body:
        current_angle: Current position (degrees)
        target_angle: Target position (degrees)
        current_speed: Current speed (RPM or %)
        current_torque: Current torque (Nm or %)
        temperature: Motor temperature (Celsius)
        voltage: Supply voltage (Volts)
        current: Current consumption (Amperes)
        error_code: Error code if any

    Returns:
        Created telemetry data point
    """
    motor = MotorService.get_motor_by_id(db, motor_id)
    if not motor:
        raise HTTPException(status_code=404, detail=f"Motor {motor_id} not found")

    try:
        data_point = TelemetryService.record_telemetry(db, telemetry_data)
        return TelemetryResponse(
            id=data_point.id,
            motor_id=data_point.motor_id,
            current_angle=data_point.current_angle,
            target_angle=data_point.target_angle,
            current_speed=data_point.current_speed,
            current_torque=data_point.current_torque,
            temperature=data_point.temperature,
            voltage=data_point.voltage,
            current=data_point.current,
            error_code=data_point.error_code,
            timestamp=data_point.timestamp,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to record telemetry: {str(e)}")


@router.get("/{motor_id}/telemetry/latest", response_model=TelemetryResponse)
async def get_latest_telemetry(motor_id: int, db: Session = Depends(get_db)):
    """
    Get latest telemetry data point for a motor.

    Path Parameters:
        motor_id: Motor ID

    Returns:
        Latest telemetry data point
    """
    motor = MotorService.get_motor_by_id(db, motor_id)
    if not motor:
        raise HTTPException(status_code=404, detail=f"Motor {motor_id} not found")

    telemetry = TelemetryService.get_latest_telemetry(db, motor_id)
    if not telemetry:
        raise HTTPException(status_code=404, detail=f"No telemetry data for motor {motor_id}")

    return TelemetryResponse(
        id=telemetry.id,
        motor_id=telemetry.motor_id,
        current_angle=telemetry.current_angle,
        target_angle=telemetry.target_angle,
        current_speed=telemetry.current_speed,
        current_torque=telemetry.current_torque,
        temperature=telemetry.temperature,
        voltage=telemetry.voltage,
        current=telemetry.current,
        error_code=telemetry.error_code,
        timestamp=telemetry.timestamp,
    )


@router.get("/{motor_id}/telemetry", response_model=TelemetryListResponse)
async def get_telemetry_range(
    motor_id: int,
    hours: int = Query(24, ge=1, le=720, description="Hours to retrieve (default 24)"),
    limit: int = Query(100, ge=1, le=1000, description="Max results (default 100)"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: Session = Depends(get_db)
):
    """
    Get telemetry data points for a motor within a time range.

    Path Parameters:
        motor_id: Motor ID

    Query Parameters:
        hours: Number of hours to retrieve (1-720, default 24)
        limit: Maximum results per page (1-1000)
        offset: Pagination offset

    Returns:
        List of telemetry data points
    """
    motor = MotorService.get_motor_by_id(db, motor_id)
    if not motor:
        raise HTTPException(status_code=404, detail=f"Motor {motor_id} not found")

    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours)

    data_points = TelemetryService.get_telemetry_range(
        db, motor_id, start_time, end_time, limit, offset
    )

    latest_timestamp = data_points[0].timestamp if data_points else None

    return TelemetryListResponse(
        data_points=[
            TelemetryResponse(
                id=dp.id,
                motor_id=dp.motor_id,
                current_angle=dp.current_angle,
                target_angle=dp.target_angle,
                current_speed=dp.current_speed,
                current_torque=dp.current_torque,
                temperature=dp.temperature,
                voltage=dp.voltage,
                current=dp.current,
                error_code=dp.error_code,
                timestamp=dp.timestamp,
            )
            for dp in data_points
        ],
        motor_id=motor_id,
        total=TelemetryService.get_telemetry_count(db, motor_id),
        latest_timestamp=latest_timestamp,
    )


@router.get("/{motor_id}/telemetry/statistics", response_model=TelemetryStatistics)
async def get_telemetry_statistics(
    motor_id: int,
    hours: int = Query(24, ge=1, le=720, description="Hours to analyze"),
    db: Session = Depends(get_db)
):
    """
    Get telemetry statistics for a motor.

    Path Parameters:
        motor_id: Motor ID

    Query Parameters:
        hours: Number of hours to analyze (default 24)

    Returns:
        Statistics including avg, min, max for temperature, speed, torque
    """
    motor = MotorService.get_motor_by_id(db, motor_id)
    if not motor:
        raise HTTPException(status_code=404, detail=f"Motor {motor_id} not found")

    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours)

    stats = TelemetryService.get_telemetry_statistics(db, motor_id, start_time, end_time)

    return TelemetryStatistics(
        motor_id=motor_id,
        motor_name=motor.name,
        data_points_count=stats['data_points_count'],
        avg_temperature=stats['avg_temperature'],
        max_temperature=stats['max_temperature'],
        min_temperature=stats['min_temperature'],
        avg_speed=stats['avg_speed'],
        max_speed=stats['max_speed'],
        min_speed=stats['min_speed'],
        avg_torque=stats['avg_torque'],
        max_torque=stats['max_torque'],
        start_time=start_time,
        end_time=end_time,
    )


@router.get("/{motor_id}/telemetry/anomalies")
async def detect_anomalies(
    motor_id: int,
    limit: int = Query(100, ge=1, le=1000, description="Recent data points to analyze"),
    db: Session = Depends(get_db)
):
    """
    Detect anomalies in motor telemetry data.

    Detects:
    - High temperature (>60°C)
    - High current (>5A)
    - Error codes

    Path Parameters:
        motor_id: Motor ID

    Query Parameters:
        limit: Recent data points to analyze

    Returns:
        List of detected anomalies
    """
    motor = MotorService.get_motor_by_id(db, motor_id)
    if not motor:
        raise HTTPException(status_code=404, detail=f"Motor {motor_id} not found")

    anomalies = TelemetryService.detect_anomalies(db, motor_id, limit)

    return {
        "motor_id": motor_id,
        "motor_name": motor.name,
        "anomaly_count": len(anomalies),
        "anomalies": anomalies,
    }


@router.get("/telemetry/all/latest")
async def get_all_motors_latest_telemetry(db: Session = Depends(get_db)):
    """
    Get latest telemetry for all motors at once.

    Returns:
        Dictionary mapping motor IDs to their latest telemetry
    """
    telemetry_data = TelemetryService.get_all_latest_telemetry(db)

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "motors": telemetry_data,
        "motor_count": len(telemetry_data),
    }


@router.delete("/{motor_id}/telemetry/cleanup")
async def cleanup_old_telemetry(
    motor_id: int,
    days_to_keep: int = Query(30, ge=1, le=365, description="Days to keep"),
    db: Session = Depends(get_db)
):
    """
    Delete old telemetry data for a motor.

    Path Parameters:
        motor_id: Motor ID

    Query Parameters:
        days_to_keep: Days to keep (default 30)

    Returns:
        Number of deleted records
    """
    motor = MotorService.get_motor_by_id(db, motor_id)
    if not motor:
        raise HTTPException(status_code=404, detail=f"Motor {motor_id} not found")

    deleted_count = TelemetryService.cleanup_old_telemetry(db, days_to_keep)

    return {
        "motor_id": motor_id,
        "deleted_records": deleted_count,
        "message": f"Deleted {deleted_count} telemetry records older than {days_to_keep} days",
    }
