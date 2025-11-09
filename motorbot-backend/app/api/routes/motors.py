"""Motor management API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.services.motor_service import MotorService
from app.services.port_service import PortService
from app.schemas.motor import (
    MotorResponse,
    MotorCreate,
    MotorUpdate,
    MotorListResponse,
    MotorDetailResponse,
    MotorStatusResponse,
    AllMotorsStatusResponse,
)
from datetime import datetime
from typing import List

router = APIRouter(prefix="/api/motors", tags=["Motors"])


@router.get("", response_model=MotorListResponse)
async def get_motors(
    calibrated_only: bool = Query(False, description="Filter only calibrated motors"),
    functional_only: bool = Query(False, description="Filter only functional motors"),
    db: Session = Depends(get_db)
):
    """
    Get all motors with optional filtering.

    Query Parameters:
        calibrated_only: If true, return only calibrated motors
        functional_only: If true, return only functional motors

    Returns:
        List of motors and statistics
    """
    motors = MotorService.get_all_motors(db, calibrated_only, functional_only)
    all_motors = MotorService.get_all_motors(db)

    calibrated_count = sum(1 for m in all_motors if m.is_calibrated)
    functional_count = sum(1 for m in all_motors if m.is_functional)

    return MotorListResponse(
        motors=[
            MotorResponse(
                id=motor.id,
                name=motor.name,
                motor_index=motor.motor_index,
                port_id=motor.port_id,
                model=motor.model,
                serial_number=motor.serial_number,
                max_speed=motor.max_speed,
                max_torque=motor.max_torque,
                is_calibrated=motor.is_calibrated,
                is_functional=motor.is_functional,
                created_at=motor.created_at,
                last_updated=motor.last_updated,
            )
            for motor in motors
        ],
        total=len(all_motors),
        calibrated_count=calibrated_count,
        functional_count=functional_count,
    )


@router.get("/status/all", response_model=AllMotorsStatusResponse)
async def get_all_motors_status(db: Session = Depends(get_db)):
    """
    Get status of all motors.

    Returns:
        Status of all motors with telemetry
    """
    statuses = MotorService.get_all_motors_status(db)
    motors = MotorService.get_all_motors(db)
    calibrated = sum(1 for m in motors if m.is_calibrated)
    functional = sum(1 for m in motors if m.is_functional)

    return AllMotorsStatusResponse(
        motors=[MotorStatusResponse(**status) for status in statuses],
        timestamp=datetime.utcnow(),
        total_motors=len(motors),
        calibrated_motors=calibrated,
        functional_motors=functional,
    )


@router.get("/{motor_id}", response_model=MotorDetailResponse)
async def get_motor(motor_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific motor.

    Path Parameters:
        motor_id: Motor ID (1-12)

    Returns:
        Detailed motor information
    """
    motor = MotorService.get_motor_by_id(db, motor_id)
    if not motor:
        raise HTTPException(status_code=404, detail=f"Motor {motor_id} not found")

    operation_count = MotorService.get_motor_operation_count(db, motor_id)
    latest_telemetry = MotorService.get_latest_telemetry(db, motor_id)

    return MotorDetailResponse(
        id=motor.id,
        name=motor.name,
        motor_index=motor.motor_index,
        port_id=motor.port_id,
        port_name=motor.port.port_name if motor.port else None,
        model=motor.model,
        serial_number=motor.serial_number,
        max_speed=motor.max_speed,
        max_torque=motor.max_torque,
        is_calibrated=motor.is_calibrated,
        is_functional=motor.is_functional,
        created_at=motor.created_at,
        last_updated=motor.last_updated,
        latest_telemetry={
            'current_angle': latest_telemetry.current_angle,
            'current_speed': latest_telemetry.current_speed,
            'temperature': latest_telemetry.temperature,
            'timestamp': latest_telemetry.timestamp.isoformat(),
        } if latest_telemetry else None,
        operation_count=operation_count,
    )


@router.post("", response_model=MotorResponse, status_code=201)
async def create_motor(motor_data: MotorCreate, db: Session = Depends(get_db)):
    """
    Create a new motor.

    Request Body:
        name: Motor name
        motor_index: Motor index (0-11)
        port_id: Port ID (optional)
        model: Motor model
        serial_number: Motor serial number

    Returns:
        Created motor details
    """
    try:
        motor = MotorService.create_motor(db, motor_data)
        return MotorResponse(
            id=motor.id,
            name=motor.name,
            motor_index=motor.motor_index,
            port_id=motor.port_id,
            model=motor.model,
            serial_number=motor.serial_number,
            max_speed=motor.max_speed,
            max_torque=motor.max_torque,
            is_calibrated=motor.is_calibrated,
            is_functional=motor.is_functional,
            created_at=motor.created_at,
            last_updated=motor.last_updated,
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.put("/{motor_id}", response_model=MotorResponse)
async def update_motor(
    motor_id: int,
    motor_data: MotorUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a motor.

    Path Parameters:
        motor_id: Motor ID

    Request Body:
        name: Motor name
        port_id: Port ID
        model: Motor model
        serial_number: Serial number
        is_calibrated: Calibration status
        is_functional: Functional status

    Returns:
        Updated motor details
    """
    try:
        motor = MotorService.update_motor(db, motor_id, motor_data)
        if not motor:
            raise HTTPException(status_code=404, detail=f"Motor {motor_id} not found")

        return MotorResponse(
            id=motor.id,
            name=motor.name,
            motor_index=motor.motor_index,
            port_id=motor.port_id,
            model=motor.model,
            serial_number=motor.serial_number,
            max_speed=motor.max_speed,
            max_torque=motor.max_torque,
            is_calibrated=motor.is_calibrated,
            is_functional=motor.is_functional,
            created_at=motor.created_at,
            last_updated=motor.last_updated,
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/{motor_id}/calibrate")
async def calibrate_motor(motor_id: int, db: Session = Depends(get_db)):
    """
    Calibrate a motor.

    Path Parameters:
        motor_id: Motor ID

    Returns:
        Calibration status
    """
    motor = MotorService.get_motor_by_id(db, motor_id)
    if not motor:
        raise HTTPException(status_code=404, detail=f"Motor {motor_id} not found")

    success = MotorService.calibrate_motor(db, motor_id)

    if not success:
        raise HTTPException(status_code=500, detail="Calibration failed")

    return {
        "motor_id": motor_id,
        "status": "calibration_completed",
        "is_calibrated": True,
        "message": "Motor calibration completed successfully",
    }


@router.get("/{motor_id}/status", response_model=MotorStatusResponse)
async def get_motor_status(motor_id: int, db: Session = Depends(get_db)):
    """
    Get current status of a motor.

    Path Parameters:
        motor_id: Motor ID

    Returns:
        Motor status with latest telemetry
    """
    status = MotorService.get_motor_status(db, motor_id)
    if not status:
        raise HTTPException(status_code=404, detail=f"Motor {motor_id} not found")

    return MotorStatusResponse(**status)


@router.delete("/{motor_id}", status_code=204)
async def delete_motor(motor_id: int, db: Session = Depends(get_db)):
    """
    Delete a motor (cascades to related data).

    Path Parameters:
        motor_id: Motor ID

    Returns:
        No content
    """
    success = MotorService.delete_motor(db, motor_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Motor {motor_id} not found")

    return None
