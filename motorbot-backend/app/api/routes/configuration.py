"""Motor configuration API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.services.configuration_service import ConfigurationService
from app.services.motor_service import MotorService
from app.schemas.motor_config import (
    MotorConfigResponse,
    MotorConfigCreate,
    MotorConfigUpdate,
    MotorConfigDetailResponse,
    ConfigPreset,
)
from typing import List

router = APIRouter(prefix="/api/motors", tags=["Motor Configuration"])


@router.get("/{motor_id}/config", response_model=MotorConfigDetailResponse)
async def get_motor_config(motor_id: int, db: Session = Depends(get_db)):
    """
    Get configuration for a motor.

    Path Parameters:
        motor_id: Motor ID

    Returns:
        Motor configuration details
    """
    motor = MotorService.get_motor_by_id(db, motor_id)
    if not motor:
        raise HTTPException(status_code=404, detail=f"Motor {motor_id} not found")

    config = ConfigurationService.get_configuration(db, motor_id)
    if not config:
        raise HTTPException(status_code=404, detail=f"Configuration for motor {motor_id} not found")

    return MotorConfigDetailResponse(
        id=config.id,
        motor_id=config.motor_id,
        motor_name=motor.name,
        min_angle=config.min_angle,
        max_angle=config.max_angle,
        default_speed=config.default_speed,
        default_torque=config.default_torque,
        acceleration=config.acceleration,
        deceleration=config.deceleration,
        timeout=config.timeout,
        custom_params=config.custom_params,
        created_at=config.created_at,
        last_updated=config.last_updated,
        presets=list(ConfigurationService.get_available_presets().keys()),
    )


@router.post("/{motor_id}/config", response_model=MotorConfigResponse, status_code=201)
async def create_motor_config(
    motor_id: int,
    config_data: MotorConfigCreate,
    db: Session = Depends(get_db)
):
    """
    Create configuration for a motor.

    Path Parameters:
        motor_id: Motor ID

    Request Body:
        min_angle: Minimum angle (degrees)
        max_angle: Maximum angle (degrees)
        default_speed: Default speed (0-100%)
        default_torque: Default torque (0-100%)
        acceleration: Acceleration rate (degrees/sec²)
        deceleration: Deceleration rate (degrees/sec²)
        timeout: Motor timeout (milliseconds)

    Returns:
        Created configuration details
    """
    motor = MotorService.get_motor_by_id(db, motor_id)
    if not motor:
        raise HTTPException(status_code=404, detail=f"Motor {motor_id} not found")

    try:
        config = ConfigurationService.create_configuration(db, motor_id, config_data)
        return MotorConfigResponse(
            id=config.id,
            motor_id=config.motor_id,
            min_angle=config.min_angle,
            max_angle=config.max_angle,
            default_speed=config.default_speed,
            default_torque=config.default_torque,
            acceleration=config.acceleration,
            deceleration=config.deceleration,
            timeout=config.timeout,
            custom_params=config.custom_params,
            created_at=config.created_at,
            last_updated=config.last_updated,
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.put("/{motor_id}/config", response_model=MotorConfigResponse)
async def update_motor_config(
    motor_id: int,
    config_data: MotorConfigUpdate,
    db: Session = Depends(get_db)
):
    """
    Update configuration for a motor.

    Path Parameters:
        motor_id: Motor ID

    Request Body:
        All fields optional - only specified fields will be updated

    Returns:
        Updated configuration details
    """
    motor = MotorService.get_motor_by_id(db, motor_id)
    if not motor:
        raise HTTPException(status_code=404, detail=f"Motor {motor_id} not found")

    config = ConfigurationService.update_configuration(db, motor_id, config_data)
    if not config:
        raise HTTPException(status_code=404, detail=f"Configuration for motor {motor_id} not found")

    return MotorConfigResponse(
        id=config.id,
        motor_id=config.motor_id,
        min_angle=config.min_angle,
        max_angle=config.max_angle,
        default_speed=config.default_speed,
        default_torque=config.default_torque,
        acceleration=config.acceleration,
        deceleration=config.deceleration,
        timeout=config.timeout,
        custom_params=config.custom_params,
        created_at=config.created_at,
        last_updated=config.last_updated,
    )


@router.post("/{motor_id}/config/preset/{preset_name}", response_model=MotorConfigResponse)
async def apply_config_preset(
    motor_id: int,
    preset_name: str,
    db: Session = Depends(get_db)
):
    """
    Apply a preset configuration to a motor.

    Path Parameters:
        motor_id: Motor ID
        preset_name: Name of preset (default, fast, slow, precision)

    Returns:
        Updated configuration details
    """
    motor = MotorService.get_motor_by_id(db, motor_id)
    if not motor:
        raise HTTPException(status_code=404, detail=f"Motor {motor_id} not found")

    try:
        config = ConfigurationService.apply_preset(db, motor_id, preset_name)
        if not config:
            raise HTTPException(status_code=404, detail=f"Configuration for motor {motor_id} not found")

        return MotorConfigResponse(
            id=config.id,
            motor_id=config.motor_id,
            min_angle=config.min_angle,
            max_angle=config.max_angle,
            default_speed=config.default_speed,
            default_torque=config.default_torque,
            acceleration=config.acceleration,
            deceleration=config.deceleration,
            timeout=config.timeout,
            custom_params=config.custom_params,
            created_at=config.created_at,
            last_updated=config.last_updated,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/config/presets", response_model=dict)
async def get_presets():
    """
    Get all available configuration presets.

    Returns:
        Dictionary of available presets
    """
    presets = ConfigurationService.get_available_presets()
    return {
        "presets": {
            name: ConfigPreset(**config)
            for name, config in presets.items()
        }
    }


@router.post("/{motor_id}/config/reset", response_model=MotorConfigResponse)
async def reset_config_to_default(motor_id: int, db: Session = Depends(get_db)):
    """
    Reset a motor's configuration to default preset.

    Path Parameters:
        motor_id: Motor ID

    Returns:
        Reset configuration details
    """
    motor = MotorService.get_motor_by_id(db, motor_id)
    if not motor:
        raise HTTPException(status_code=404, detail=f"Motor {motor_id} not found")

    config = ConfigurationService.reset_to_default(db, motor_id)
    if not config:
        raise HTTPException(status_code=404, detail=f"Configuration for motor {motor_id} not found")

    return MotorConfigResponse(
        id=config.id,
        motor_id=config.motor_id,
        min_angle=config.min_angle,
        max_angle=config.max_angle,
        default_speed=config.default_speed,
        default_torque=config.default_torque,
        acceleration=config.acceleration,
        deceleration=config.deceleration,
        timeout=config.timeout,
        custom_params=config.custom_params,
        created_at=config.created_at,
        last_updated=config.last_updated,
    )


@router.get("/config/compare", response_model=dict)
async def compare_configurations(
    motor_id_1: int = Query(..., description="First motor ID"),
    motor_id_2: int = Query(..., description="Second motor ID"),
    db: Session = Depends(get_db)
):
    """
    Compare configurations of two motors.

    Query Parameters:
        motor_id_1: First motor ID
        motor_id_2: Second motor ID

    Returns:
        Dictionary showing configuration differences
    """
    motor1 = MotorService.get_motor_by_id(db, motor_id_1)
    motor2 = MotorService.get_motor_by_id(db, motor_id_2)

    if not motor1 or not motor2:
        raise HTTPException(status_code=404, detail="One or both motors not found")

    differences = ConfigurationService.get_configuration_difference(
        db, motor_id_1, motor_id_2
    )

    return {
        "motor_id_1": motor_id_1,
        "motor_id_2": motor_id_2,
        "differences": differences,
        "identical": len(differences) == 0,
    }
