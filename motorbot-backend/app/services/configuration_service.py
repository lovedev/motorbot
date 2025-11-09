"""Motor configuration service"""

from sqlalchemy.orm import Session
from app.models.motor_config import MotorConfiguration
from app.schemas.motor_config import MotorConfigCreate, MotorConfigUpdate
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ConfigurationService:
    """Service for motor configuration management"""

    # Preset configurations
    PRESETS = {
        "default": {
            "min_angle": 0.0,
            "max_angle": 360.0,
            "default_speed": 50.0,
            "default_torque": 50.0,
            "acceleration": 10.0,
            "deceleration": 10.0,
            "timeout": 5000,
        },
        "fast": {
            "min_angle": 0.0,
            "max_angle": 360.0,
            "default_speed": 100.0,
            "default_torque": 75.0,
            "acceleration": 20.0,
            "deceleration": 20.0,
            "timeout": 3000,
        },
        "slow": {
            "min_angle": 0.0,
            "max_angle": 360.0,
            "default_speed": 25.0,
            "default_torque": 25.0,
            "acceleration": 5.0,
            "deceleration": 5.0,
            "timeout": 10000,
        },
        "precision": {
            "min_angle": 0.0,
            "max_angle": 360.0,
            "default_speed": 20.0,
            "default_torque": 30.0,
            "acceleration": 3.0,
            "deceleration": 3.0,
            "timeout": 15000,
        },
    }

    @staticmethod
    def get_configuration(db: Session, motor_id: int) -> Optional[MotorConfiguration]:
        """
        Get configuration for a motor.

        Args:
            db: Database session
            motor_id: Motor ID

        Returns:
            MotorConfiguration object or None
        """
        return db.query(MotorConfiguration).filter(
            MotorConfiguration.motor_id == motor_id
        ).first()

    @staticmethod
    def create_configuration(db: Session, motor_id: int, config_data: MotorConfigCreate) -> MotorConfiguration:
        """
        Create configuration for a motor.

        Args:
            db: Database session
            motor_id: Motor ID
            config_data: Configuration data

        Returns:
            Created MotorConfiguration object
        """
        # Check if configuration already exists
        existing = db.query(MotorConfiguration).filter(
            MotorConfiguration.motor_id == motor_id
        ).first()

        if existing:
            logger.warning(f"Configuration for motor {motor_id} already exists")
            raise ValueError(f"Configuration for motor {motor_id} already exists")

        config_dict = config_data.model_dump()
        config_dict['motor_id'] = motor_id

        db_config = MotorConfiguration(**config_dict)
        db.add(db_config)
        db.commit()
        db.refresh(db_config)

        logger.info(f"Created configuration for motor {motor_id}")
        return db_config

    @staticmethod
    def update_configuration(db: Session, motor_id: int, config_data: MotorConfigUpdate) -> Optional[MotorConfiguration]:
        """
        Update configuration for a motor.

        Args:
            db: Database session
            motor_id: Motor ID
            config_data: Configuration update data

        Returns:
            Updated MotorConfiguration object or None
        """
        db_config = db.query(MotorConfiguration).filter(
            MotorConfiguration.motor_id == motor_id
        ).first()

        if not db_config:
            logger.warning(f"Configuration for motor {motor_id} not found")
            return None

        update_data = config_data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(db_config, key, value)

        db.commit()
        db.refresh(db_config)

        logger.info(f"Updated configuration for motor {motor_id}")
        return db_config

    @staticmethod
    def apply_preset(db: Session, motor_id: int, preset_name: str) -> Optional[MotorConfiguration]:
        """
        Apply a preset configuration to a motor.

        Args:
            db: Database session
            motor_id: Motor ID
            preset_name: Name of preset to apply

        Returns:
            Updated MotorConfiguration object or None
        """
        if preset_name not in ConfigurationService.PRESETS:
            logger.warning(f"Unknown preset: {preset_name}")
            raise ValueError(f"Unknown preset: {preset_name}")

        preset = ConfigurationService.PRESETS[preset_name]
        db_config = db.query(MotorConfiguration).filter(
            MotorConfiguration.motor_id == motor_id
        ).first()

        if not db_config:
            logger.warning(f"Configuration for motor {motor_id} not found")
            return None

        for key, value in preset.items():
            setattr(db_config, key, value)

        db.commit()
        db.refresh(db_config)

        logger.info(f"Applied preset '{preset_name}' to motor {motor_id}")
        return db_config

    @staticmethod
    def get_available_presets() -> dict:
        """
        Get all available configuration presets.

        Returns:
            Dictionary of preset names and configurations
        """
        return ConfigurationService.PRESETS

    @staticmethod
    def validate_angles(db: Session, motor_id: int, min_angle: float, max_angle: float) -> bool:
        """
        Validate angle range for a motor.

        Args:
            db: Database session
            motor_id: Motor ID
            min_angle: Minimum angle
            max_angle: Maximum angle

        Returns:
            True if valid, False otherwise
        """
        if min_angle >= max_angle:
            logger.warning(f"Invalid angle range: min={min_angle}, max={max_angle}")
            return False

        # Additional constraints
        if min_angle < -360 or max_angle > 360:
            logger.warning(f"Angle out of range: min={min_angle}, max={max_angle}")
            return False

        return True

    @staticmethod
    def get_all_configurations(db: Session) -> list:
        """
        Get all motor configurations.

        Args:
            db: Database session

        Returns:
            List of MotorConfiguration objects
        """
        return db.query(MotorConfiguration).all()

    @staticmethod
    def reset_to_default(db: Session, motor_id: int) -> Optional[MotorConfiguration]:
        """
        Reset a motor's configuration to default preset.

        Args:
            db: Database session
            motor_id: Motor ID

        Returns:
            Updated MotorConfiguration object or None
        """
        return ConfigurationService.apply_preset(db, motor_id, "default")

    @staticmethod
    def get_configuration_difference(db: Session, motor_id: int, other_motor_id: int) -> dict:
        """
        Compare configurations of two motors.

        Args:
            db: Database session
            motor_id: First motor ID
            other_motor_id: Second motor ID

        Returns:
            Dictionary showing differences
        """
        config1 = ConfigurationService.get_configuration(db, motor_id)
        config2 = ConfigurationService.get_configuration(db, other_motor_id)

        if not config1 or not config2:
            return {}

        differences = {}
        config1_dict = {
            'min_angle': config1.min_angle,
            'max_angle': config1.max_angle,
            'default_speed': config1.default_speed,
            'default_torque': config1.default_torque,
            'acceleration': config1.acceleration,
            'deceleration': config1.deceleration,
            'timeout': config1.timeout,
        }

        config2_dict = {
            'min_angle': config2.min_angle,
            'max_angle': config2.max_angle,
            'default_speed': config2.default_speed,
            'default_torque': config2.default_torque,
            'acceleration': config2.acceleration,
            'deceleration': config2.deceleration,
            'timeout': config2.timeout,
        }

        for key in config1_dict:
            if config1_dict[key] != config2_dict[key]:
                differences[key] = {
                    f'motor_{motor_id}': config1_dict[key],
                    f'motor_{other_motor_id}': config2_dict[key],
                }

        return differences
