"""Telemetry data service"""

from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app.models.telemetry import TelemetryDataPoint
from app.schemas.telemetry import TelemetryCreate
from datetime import datetime, timedelta
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class TelemetryService:
    """Service for telemetry data management"""

    @staticmethod
    def record_telemetry(db: Session, telemetry_data: TelemetryCreate) -> TelemetryDataPoint:
        """
        Record a telemetry data point.

        Args:
            db: Database session
            telemetry_data: Telemetry data to record

        Returns:
            Created TelemetryDataPoint object
        """
        data_point = TelemetryDataPoint(**telemetry_data.model_dump())
        db.add(data_point)
        db.commit()
        db.refresh(data_point)

        logger.debug(f"Recorded telemetry for motor {telemetry_data.motor_id}")
        return data_point

    @staticmethod
    def get_latest_telemetry(db: Session, motor_id: int) -> Optional[TelemetryDataPoint]:
        """
        Get latest telemetry data point for a motor.

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
    def get_telemetry_range(
        db: Session,
        motor_id: int,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[TelemetryDataPoint]:
        """
        Get telemetry data points within a time range.

        Args:
            db: Database session
            motor_id: Motor ID
            start_time: Start time (if None, last 24 hours)
            end_time: End time (if None, now)
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            List of TelemetryDataPoint objects
        """
        if end_time is None:
            end_time = datetime.utcnow()

        if start_time is None:
            start_time = end_time - timedelta(hours=24)

        query = db.query(TelemetryDataPoint).filter(
            TelemetryDataPoint.motor_id == motor_id,
            TelemetryDataPoint.timestamp >= start_time,
            TelemetryDataPoint.timestamp <= end_time,
        ).order_by(desc(TelemetryDataPoint.timestamp))

        return query.offset(offset).limit(limit).all()

    @staticmethod
    def get_telemetry_statistics(
        db: Session,
        motor_id: int,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """
        Get telemetry statistics for a motor.

        Args:
            db: Database session
            motor_id: Motor ID
            start_time: Start time (if None, last 24 hours)
            end_time: End time (if None, now)

        Returns:
            Dictionary with statistics
        """
        if end_time is None:
            end_time = datetime.utcnow()

        if start_time is None:
            start_time = end_time - timedelta(hours=24)

        data_points = TelemetryService.get_telemetry_range(
            db, motor_id, start_time, end_time, limit=10000
        )

        if not data_points:
            return {
                'motor_id': motor_id,
                'data_points_count': 0,
                'start_time': start_time,
                'end_time': end_time,
            }

        # Extract values
        temperatures = [dp.temperature for dp in data_points if dp.temperature is not None]
        speeds = [dp.current_speed for dp in data_points if dp.current_speed is not None]
        torques = [dp.current_torque for dp in data_points if dp.current_torque is not None]

        def safe_avg(values):
            return sum(values) / len(values) if values else None

        def safe_max(values):
            return max(values) if values else None

        def safe_min(values):
            return min(values) if values else None

        return {
            'motor_id': motor_id,
            'data_points_count': len(data_points),
            'start_time': start_time,
            'end_time': end_time,
            # Temperature statistics
            'avg_temperature': safe_avg(temperatures),
            'max_temperature': safe_max(temperatures),
            'min_temperature': safe_min(temperatures),
            # Speed statistics
            'avg_speed': safe_avg(speeds),
            'max_speed': safe_max(speeds),
            'min_speed': safe_min(speeds),
            # Torque statistics
            'avg_torque': safe_avg(torques),
            'max_torque': safe_max(torques),
            'min_torque': safe_min(torques),
        }

    @staticmethod
    def detect_anomalies(db: Session, motor_id: int, limit: int = 100) -> List[dict]:
        """
        Detect anomalies in telemetry data.

        Anomalies include:
        - Abnormally high temperature
        - Abnormally high current
        - Error codes

        Args:
            db: Database session
            motor_id: Motor ID
            limit: Number of recent data points to analyze

        Returns:
            List of anomaly dictionaries
        """
        data_points = db.query(TelemetryDataPoint).filter(
            TelemetryDataPoint.motor_id == motor_id
        ).order_by(desc(TelemetryDataPoint.timestamp)).limit(limit).all()

        anomalies = []

        for dp in data_points:
            if dp.temperature and dp.temperature > 60:  # High temperature threshold
                anomalies.append({
                    'timestamp': dp.timestamp,
                    'type': 'high_temperature',
                    'value': dp.temperature,
                    'threshold': 60,
                })

            if dp.current and dp.current > 5:  # High current threshold
                anomalies.append({
                    'timestamp': dp.timestamp,
                    'type': 'high_current',
                    'value': dp.current,
                    'threshold': 5,
                })

            if dp.error_code and dp.error_code != 0:
                anomalies.append({
                    'timestamp': dp.timestamp,
                    'type': 'error_code',
                    'value': dp.error_code,
                })

        return anomalies

    @staticmethod
    def get_all_latest_telemetry(db: Session) -> dict:
        """
        Get latest telemetry for all motors.

        Args:
            db: Database session

        Returns:
            Dictionary mapping motor_id to latest telemetry
        """
        from app.models.motor import Motor

        motors = db.query(Motor).all()
        result = {}

        for motor in motors:
            latest = TelemetryService.get_latest_telemetry(db, motor.id)
            if latest:
                result[motor.id] = {
                    'motor_name': motor.name,
                    'motor_index': motor.motor_index,
                    'current_angle': latest.current_angle,
                    'current_speed': latest.current_speed,
                    'temperature': latest.temperature,
                    'voltage': latest.voltage,
                    'current': latest.current,
                    'timestamp': latest.timestamp,
                }

        return result

    @staticmethod
    def cleanup_old_telemetry(db: Session, days_to_keep: int = 30) -> int:
        """
        Delete telemetry data older than specified days.

        Args:
            db: Database session
            days_to_keep: Number of days to keep

        Returns:
            Number of deleted records
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)

        deleted_count = db.query(TelemetryDataPoint).filter(
            TelemetryDataPoint.timestamp < cutoff_date
        ).delete()

        db.commit()
        logger.info(f"Deleted {deleted_count} old telemetry records (older than {days_to_keep} days)")

        return deleted_count

    @staticmethod
    def get_telemetry_count(db: Session, motor_id: Optional[int] = None) -> int:
        """
        Get count of telemetry data points.

        Args:
            db: Database session
            motor_id: If specified, count only for this motor

        Returns:
            Count of telemetry data points
        """
        query = db.query(func.count(TelemetryDataPoint.id))

        if motor_id:
            query = query.filter(TelemetryDataPoint.motor_id == motor_id)

        return query.scalar() or 0
