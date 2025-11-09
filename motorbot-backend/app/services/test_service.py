"""Motor test service"""

from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.motor_test import MotorTestEvent
from app.models.operation_log import OperationLog
from datetime import datetime
from typing import List, Optional
import logging
import asyncio

logger = logging.getLogger(__name__)


class TestService:
    """Service for motor testing and validation"""

    # Test specifications
    TEST_SPECS = {
        "communication": {
            "name": "Communication Test",
            "description": "Test motor communication and responsiveness",
            "timeout": 10000,  # milliseconds
        },
        "speed": {
            "name": "Speed Test",
            "description": "Test motor speed range and responsiveness",
            "timeout": 30000,
        },
        "torque": {
            "name": "Torque Test",
            "description": "Test motor torque output",
            "timeout": 30000,
        },
        "temperature": {
            "name": "Temperature Test",
            "description": "Test motor temperature under load",
            "timeout": 60000,
        },
    }

    @staticmethod
    def get_test_spec(test_type: str) -> Optional[dict]:
        """
        Get test specification.

        Args:
            test_type: Type of test

        Returns:
            Test specification dictionary or None
        """
        return TestService.TEST_SPECS.get(test_type)

    @staticmethod
    def get_available_tests() -> dict:
        """
        Get all available tests.

        Returns:
            Dictionary of available tests
        """
        return TestService.TEST_SPECS

    @staticmethod
    def create_test_event(
        db: Session,
        motor_id: int,
        test_type: str,
        test_name: str,
        status: str,
        success: bool,
        error_message: Optional[str] = None,
        max_value: Optional[float] = None,
        min_value: Optional[float] = None,
        avg_value: Optional[float] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> MotorTestEvent:
        """
        Create a test event record.

        Args:
            db: Database session
            motor_id: Motor ID
            test_type: Type of test
            test_name: Test name
            status: Test status
            success: Whether test passed
            error_message: Error message if failed
            max_value: Maximum measured value
            min_value: Minimum measured value
            avg_value: Average measured value
            start_time: Test start time
            end_time: Test end time

        Returns:
            Created MotorTestEvent object
        """
        if start_time is None:
            start_time = datetime.utcnow()
        if end_time is None:
            end_time = datetime.utcnow()

        duration = int((end_time - start_time).total_seconds() * 1000)

        test_event = MotorTestEvent(
            motor_id=motor_id,
            test_type=test_type,
            test_name=test_name,
            status=status,
            success=success,
            error_message=error_message,
            max_value=max_value,
            min_value=min_value,
            avg_value=avg_value,
            test_started_at=start_time,
            test_completed_at=end_time,
            duration=duration,
        )

        db.add(test_event)

        # Log the operation
        log = OperationLog(
            motor_id=motor_id,
            operation_type="test",
            status="completed",
            description=f"Test: {test_name}",
            result=f"Status: {status}, Success: {success}",
            duration=duration,
        )
        db.add(log)
        db.commit()
        db.refresh(test_event)

        logger.info(f"Created test event for motor {motor_id}: {test_name} - {status}")
        return test_event

    @staticmethod
    def get_test_by_id(db: Session, test_id: int) -> Optional[MotorTestEvent]:
        """
        Get test by ID.

        Args:
            db: Database session
            test_id: Test ID

        Returns:
            MotorTestEvent or None
        """
        return db.query(MotorTestEvent).filter(MotorTestEvent.id == test_id).first()

    @staticmethod
    def get_motor_tests(
        db: Session,
        motor_id: int,
        test_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[MotorTestEvent]:
        """
        Get tests for a motor.

        Args:
            db: Database session
            motor_id: Motor ID
            test_type: Optional filter by test type
            limit: Maximum results
            offset: Pagination offset

        Returns:
            List of MotorTestEvent objects
        """
        query = db.query(MotorTestEvent).filter(MotorTestEvent.motor_id == motor_id)

        if test_type:
            query = query.filter(MotorTestEvent.test_type == test_type)

        return query.order_by(desc(MotorTestEvent.created_at)).offset(offset).limit(limit).all()

    @staticmethod
    def get_test_history(db: Session, motor_id: int) -> dict:
        """
        Get test history summary for a motor.

        Args:
            db: Database session
            motor_id: Motor ID

        Returns:
            Dictionary with test history summary
        """
        tests = db.query(MotorTestEvent).filter(MotorTestEvent.motor_id == motor_id).all()

        if not tests:
            return {
                'motor_id': motor_id,
                'total_tests': 0,
                'passed_tests': 0,
                'failed_tests': 0,
                'success_rate': 0,
            }

        passed = sum(1 for t in tests if t.success)
        failed = sum(1 for t in tests if not t.success)

        # Count by test type
        test_type_counts = {}
        for test in tests:
            if test.test_type not in test_type_counts:
                test_type_counts[test.test_type] = {'total': 0, 'passed': 0}
            test_type_counts[test.test_type]['total'] += 1
            if test.success:
                test_type_counts[test.test_type]['passed'] += 1

        return {
            'motor_id': motor_id,
            'total_tests': len(tests),
            'passed_tests': passed,
            'failed_tests': failed,
            'success_rate': (passed / len(tests) * 100) if tests else 0,
            'last_test': tests[0].created_at if tests else None,
            'test_type_breakdown': test_type_counts,
        }

    @staticmethod
    def simulate_communication_test(motor_id: int) -> dict:
        """
        Simulate a communication test.

        Args:
            motor_id: Motor ID

        Returns:
            Test result dictionary
        """
        # Simulated test logic
        import random

        success = random.random() > 0.1  # 90% success rate
        response_time = random.uniform(50, 200)  # milliseconds

        return {
            'test_type': 'communication',
            'success': success,
            'status': 'passed' if success else 'failed',
            'error_message': None if success else 'Motor did not respond',
            'max_value': response_time,
            'min_value': response_time * 0.8,
            'avg_value': response_time,
        }

    @staticmethod
    def simulate_speed_test(motor_id: int) -> dict:
        """
        Simulate a speed test.

        Args:
            motor_id: Motor ID

        Returns:
            Test result dictionary
        """
        import random

        success = random.random() > 0.05  # 95% success rate
        avg_speed = random.uniform(40, 60)  # RPM percentage

        return {
            'test_type': 'speed',
            'success': success,
            'status': 'passed' if success else 'failed',
            'error_message': None if success else 'Speed out of range',
            'max_value': avg_speed * 1.1,
            'min_value': avg_speed * 0.9,
            'avg_value': avg_speed,
        }

    @staticmethod
    def simulate_torque_test(motor_id: int) -> dict:
        """
        Simulate a torque test.

        Args:
            motor_id: Motor ID

        Returns:
            Test result dictionary
        """
        import random

        success = random.random() > 0.08  # 92% success rate
        avg_torque = random.uniform(8, 12)  # Nm

        return {
            'test_type': 'torque',
            'success': success,
            'status': 'passed' if success else 'failed',
            'error_message': None if success else 'Torque below minimum',
            'max_value': avg_torque * 1.15,
            'min_value': avg_torque * 0.85,
            'avg_value': avg_torque,
        }

    @staticmethod
    def simulate_temperature_test(motor_id: int) -> dict:
        """
        Simulate a temperature test.

        Args:
            motor_id: Motor ID

        Returns:
            Test result dictionary
        """
        import random

        success = random.random() > 0.1  # 90% success rate
        avg_temp = random.uniform(35, 50)  # Celsius

        return {
            'test_type': 'temperature',
            'success': success,
            'status': 'passed' if success else 'warning',
            'error_message': None if success else 'Temperature high',
            'max_value': avg_temp + 5,
            'min_value': avg_temp - 5,
            'avg_value': avg_temp,
        }

    @staticmethod
    def get_simulator_for_test(test_type: str):
        """
        Get simulator function for test type.

        Args:
            test_type: Type of test

        Returns:
            Simulator function or None
        """
        simulators = {
            'communication': TestService.simulate_communication_test,
            'speed': TestService.simulate_speed_test,
            'torque': TestService.simulate_torque_test,
            'temperature': TestService.simulate_temperature_test,
        }
        return simulators.get(test_type)

    @staticmethod
    def delete_test(db: Session, test_id: int) -> bool:
        """
        Delete a test record.

        Args:
            db: Database session
            test_id: Test ID

        Returns:
            True if successful, False otherwise
        """
        test = db.query(MotorTestEvent).filter(MotorTestEvent.id == test_id).first()
        if not test:
            logger.warning(f"Test {test_id} not found")
            return False

        db.delete(test)
        db.commit()
        logger.info(f"Deleted test {test_id}")
        return True
