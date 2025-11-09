"""Motor management service"""

from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.motor import Motor
from app.models.telemetry import TelemetryDataPoint
from app.models.operation_log import OperationLog
from app.schemas.motor import MotorCreate, MotorUpdate
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class MotorService:
    """Service for motor management"""

    @staticmethod
    def get_all_motors(db: Session, calibrated_only: bool = False, functional_only: bool = False) -> List[Motor]:
        """
        Get all motors from database.

        Args:
            db: Database session
            calibrated_only: If True, return only calibrated motors
            functional_only: If True, return only functional motors

        Returns:
            List of Motor objects
        """
        query = db.query(Motor)

        if calibrated_only:
            query = query.filter(Motor.is_calibrated == True)
        if functional_only:
            query = query.filter(Motor.is_functional == True)

        return query.order_by(Motor.motor_index).all()

    @staticmethod
    def get_motor_by_id(db: Session, motor_id: int) -> Optional[Motor]:
        """
        Get motor by ID.

        Args:
            db: Database session
            motor_id: Motor ID

        Returns:
            Motor object or None
        """
        return db.query(Motor).filter(Motor.id == motor_id).first()

    @staticmethod
    def get_motor_by_index(db: Session, motor_index: int) -> Optional[Motor]:
        """
        Get motor by index (0-11).

        Args:
            db: Database session
            motor_index: Motor index

        Returns:
            Motor object or None
        """
        if not (0 <= motor_index <= 11):
            logger.warning(f"Invalid motor index: {motor_index}")
            return None
        return db.query(Motor).filter(Motor.motor_index == motor_index).first()

    @staticmethod
    def create_motor(db: Session, motor_data: MotorCreate) -> Motor:
        """
        Create a new motor.

        Args:
            db: Database session
            motor_data: Motor creation data

        Returns:
            Created Motor object
        """
        # Check if motor with same index already exists
        existing = db.query(Motor).filter(Motor.motor_index == motor_data.motor_index).first()
        if existing:
            logger.warning(f"Motor with index {motor_data.motor_index} already exists")
            raise ValueError(f"Motor index {motor_data.motor_index} already in use")

        db_motor = Motor(**motor_data.model_dump())
        db.add(db_motor)
        db.commit()
        db.refresh(db_motor)
        logger.info(f"Created motor: {motor_data.name} (index: {motor_data.motor_index})")
        return db_motor

    @staticmethod
    def update_motor(db: Session, motor_id: int, motor_data: MotorUpdate) -> Optional[Motor]:
        """
        Update a motor.

        Args:
            db: Database session
            motor_id: Motor ID
            motor_data: Motor update data

        Returns:
            Updated Motor object or None
        """
        db_motor = db.query(Motor).filter(Motor.id == motor_id).first()
        if not db_motor:
            logger.warning(f"Motor {motor_id} not found")
            return None

        update_data = motor_data.model_dump(exclude_unset=True)

        # If changing motor_index, check for conflicts
        if 'motor_index' in update_data:
            existing = db.query(Motor).filter(
                Motor.motor_index == update_data['motor_index'],
                Motor.id != motor_id
            ).first()
            if existing:
                logger.warning(f"Motor index {update_data['motor_index']} already in use")
                raise ValueError(f"Motor index {update_data['motor_index']} already in use")

        for key, value in update_data.items():
            setattr(db_motor, key, value)

        db.commit()
        db.refresh(db_motor)
        logger.info(f"Updated motor: {db_motor.name}")
        return db_motor

    @staticmethod
    def calibrate_motor(db: Session, motor_id: int) -> bool:
        """
        Mark motor as calibrated.

        Args:
            db: Database session
            motor_id: Motor ID

        Returns:
            True if successful, False otherwise
        """
        motor = db.query(Motor).filter(Motor.id == motor_id).first()
        if not motor:
            logger.warning(f"Motor {motor_id} not found")
            return False

        motor.is_calibrated = True
        db.commit()

        # Log the operation
        log = OperationLog(
            motor_id=motor_id,
            operation_type="calibration",
            status="completed",
            description="Motor calibration completed",
        )
        db.add(log)
        db.commit()

        logger.info(f"Calibrated motor: {motor.name}")
        return True

    @staticmethod
    def get_latest_telemetry(db: Session, motor_id: int) -> Optional[TelemetryDataPoint]:
        """
        Get latest telemetry data for a motor.

        Args:
            db: Database session
            motor_id: Motor ID

        Returns:
            Latest TelemetryDataPoint or None
        """
        return db.query(TelemetryDataPoint).filter(
            TelemetryDataPoint.motor_id == motor_id
        ).order_by(desc(TelemetryDataPoint.timestamp)).first()

    @staticmethod
    def get_motor_status(db: Session, motor_id: int) -> Optional[dict]:
        """
        Get current status of a motor.

        Args:
            db: Database session
            motor_id: Motor ID

        Returns:
            Dictionary with motor status or None
        """
        motor = db.query(Motor).filter(Motor.id == motor_id).first()
        if not motor:
            return None

        latest_telemetry = MotorService.get_latest_telemetry(db, motor_id)

        return {
            'motor_id': motor.id,
            'name': motor.name,
            'motor_index': motor.motor_index,
            'is_calibrated': motor.is_calibrated,
            'is_functional': motor.is_functional,
            'last_updated': motor.last_updated,
            'current_angle': latest_telemetry.current_angle if latest_telemetry else None,
            'current_speed': latest_telemetry.current_speed if latest_telemetry else None,
            'temperature': latest_telemetry.temperature if latest_telemetry else None,
        }

    @staticmethod
    def get_all_motors_status(db: Session) -> List[dict]:
        """
        Get status of all motors.

        Args:
            db: Database session

        Returns:
            List of motor status dictionaries
        """
        motors = MotorService.get_all_motors(db)
        statuses = []

        for motor in motors:
            status = MotorService.get_motor_status(db, motor.id)
            if status:
                statuses.append(status)

        return statuses

    @staticmethod
    def delete_motor(db: Session, motor_id: int) -> bool:
        """
        Delete a motor (cascades to related data).

        Args:
            db: Database session
            motor_id: Motor ID

        Returns:
            True if successful, False otherwise
        """
        motor = db.query(Motor).filter(Motor.id == motor_id).first()
        if not motor:
            logger.warning(f"Motor {motor_id} not found")
            return False

        db.delete(motor)
        db.commit()
        logger.info(f"Deleted motor: {motor.name}")
        return True

    @staticmethod
    def get_motor_operation_count(db: Session, motor_id: int) -> int:
        """
        Get count of operations for a motor.

        Args:
            db: Database session
            motor_id: Motor ID

        Returns:
            Number of operations
        """
        return db.query(OperationLog).filter(OperationLog.motor_id == motor_id).count()

    @staticmethod
    def get_calibration_stats(db: Session) -> dict:
        """
        Get calibration statistics.

        Args:
            db: Database session

        Returns:
            Dictionary with calibration stats
        """
        total = db.query(Motor).count()
        calibrated = db.query(Motor).filter(Motor.is_calibrated == True).count()
        functional = db.query(Motor).filter(Motor.is_functional == True).count()

        return {
            'total_motors': total,
            'calibrated_motors': calibrated,
            'functional_motors': functional,
            'calibration_percentage': (calibrated / total * 100) if total > 0 else 0,
        }
