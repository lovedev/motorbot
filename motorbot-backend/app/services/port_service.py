"""Port discovery and management service"""

import serial.tools.list_ports
from sqlalchemy.orm import Session
from app.models.port import Port
from app.schemas.port import PortCreate, PortUpdate
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class PortService:
    """Service for port discovery and management"""

    @staticmethod
    def discover_ports() -> List[dict]:
        """
        Discover available USB ports using pyserial.

        Returns:
            List of discovered port information dictionaries
        """
        ports = []
        try:
            for port in serial.tools.list_ports.comports():
                port_info = {
                    'port_name': port.device,
                    'vendor_id': port.vid if hasattr(port, 'vid') else None,
                    'product_id': port.pid if hasattr(port, 'pid') else None,
                    'description': port.description if hasattr(port, 'description') else None,
                    'device_id': port.serial_number if hasattr(port, 'serial_number') else None,
                }
                ports.append(port_info)
                logger.info(f"Discovered port: {port_info['port_name']} - {port_info['description']}")
        except Exception as e:
            logger.error(f"Error discovering ports: {str(e)}")
        return ports

    @staticmethod
    def sync_ports(db: Session) -> dict:
        """
        Sync discovered ports with database.

        Adds new ports and marks missing ones as inactive.

        Args:
            db: Database session

        Returns:
            Dictionary with sync results
        """
        discovered_ports = PortService.discover_ports()
        discovered_port_names = {p['port_name'] for p in discovered_ports}

        # Mark ports not in discovered list as inactive
        inactive_ports = db.query(Port).filter(Port.port_name.notin_(discovered_port_names)).all()
        for port in inactive_ports:
            port.is_active = False
            logger.info(f"Marked port {port.port_name} as inactive")

        # Add or update discovered ports
        added = 0
        updated = 0

        for port_data in discovered_ports:
            existing_port = db.query(Port).filter(Port.port_name == port_data['port_name']).first()

            if existing_port:
                existing_port.is_active = True
                existing_port.vendor_id = port_data.get('vendor_id')
                existing_port.product_id = port_data.get('product_id')
                existing_port.description = port_data.get('description')
                existing_port.device_id = port_data.get('device_id')
                updated += 1
                logger.info(f"Updated port: {port_data['port_name']}")
            else:
                new_port = Port(
                    port_name=port_data['port_name'],
                    vendor_id=port_data.get('vendor_id'),
                    product_id=port_data.get('product_id'),
                    description=port_data.get('description'),
                    device_id=port_data.get('device_id'),
                    is_active=True,
                    is_assigned=False,
                )
                db.add(new_port)
                added += 1
                logger.info(f"Added new port: {port_data['port_name']}")

        db.commit()

        return {
            'discovered': len(discovered_ports),
            'added': added,
            'updated': updated,
            'marked_inactive': len(inactive_ports),
        }

    @staticmethod
    def get_all_ports(db: Session, active_only: bool = False) -> List[Port]:
        """
        Get all ports from database.

        Args:
            db: Database session
            active_only: If True, return only active ports

        Returns:
            List of Port objects
        """
        query = db.query(Port)
        if active_only:
            query = query.filter(Port.is_active == True)
        return query.all()

    @staticmethod
    def get_port_by_id(db: Session, port_id: int) -> Optional[Port]:
        """
        Get port by ID.

        Args:
            db: Database session
            port_id: Port ID

        Returns:
            Port object or None
        """
        return db.query(Port).filter(Port.id == port_id).first()

    @staticmethod
    def get_port_by_name(db: Session, port_name: str) -> Optional[Port]:
        """
        Get port by name.

        Args:
            db: Database session
            port_name: Port name (e.g., /dev/ttyUSB0, COM3)

        Returns:
            Port object or None
        """
        return db.query(Port).filter(Port.port_name == port_name).first()

    @staticmethod
    def create_port(db: Session, port_data: PortCreate) -> Port:
        """
        Create a new port.

        Args:
            db: Database session
            port_data: Port creation data

        Returns:
            Created Port object
        """
        db_port = Port(**port_data.model_dump())
        db.add(db_port)
        db.commit()
        db.refresh(db_port)
        logger.info(f"Created port: {port_data.port_name}")
        return db_port

    @staticmethod
    def update_port(db: Session, port_id: int, port_data: PortUpdate) -> Optional[Port]:
        """
        Update a port.

        Args:
            db: Database session
            port_id: Port ID
            port_data: Port update data

        Returns:
            Updated Port object or None
        """
        db_port = db.query(Port).filter(Port.id == port_id).first()
        if not db_port:
            return None

        update_data = port_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_port, key, value)

        db.commit()
        db.refresh(db_port)
        logger.info(f"Updated port: {db_port.port_name}")
        return db_port

    @staticmethod
    def assign_port_to_motor(db: Session, port_id: int, motor_id: int) -> bool:
        """
        Assign a port to a motor.

        Args:
            db: Database session
            port_id: Port ID
            motor_id: Motor ID

        Returns:
            True if successful, False otherwise
        """
        port = db.query(Port).filter(Port.id == port_id).first()
        if not port:
            logger.warning(f"Port {port_id} not found")
            return False

        port.is_assigned = True
        db.commit()
        logger.info(f"Assigned port {port.port_name} to motor {motor_id}")
        return True

    @staticmethod
    def unassign_port(db: Session, port_id: int) -> bool:
        """
        Unassign a port from a motor.

        Args:
            db: Database session
            port_id: Port ID

        Returns:
            True if successful, False otherwise
        """
        port = db.query(Port).filter(Port.id == port_id).first()
        if not port:
            logger.warning(f"Port {port_id} not found")
            return False

        port.is_assigned = False
        db.commit()
        logger.info(f"Unassigned port {port.port_name}")
        return True

    @staticmethod
    def get_available_ports(db: Session) -> List[Port]:
        """
        Get available ports (active and not assigned).

        Args:
            db: Database session

        Returns:
            List of available Port objects
        """
        return db.query(Port).filter(
            Port.is_active == True,
            Port.is_assigned == False
        ).all()
