"""Port discovery and management API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.services.port_service import PortService
from app.schemas.port import (
    PortResponse,
    PortCreate,
    PortUpdate,
    PortListResponse,
    PortDiscoveryResponse,
)
from typing import List
from datetime import datetime

router = APIRouter(prefix="/api/ports", tags=["Ports"])


@router.post("/discover", response_model=PortDiscoveryResponse)
async def discover_ports(db: Session = Depends(get_db)):
    """
    Discover available USB ports and sync with database.

    Returns:
        Dictionary with discovered ports and statistics
    """
    try:
        sync_result = PortService.sync_ports(db)

        ports = PortService.get_all_ports(db)
        available_ports = PortService.get_available_ports(db)

        return PortDiscoveryResponse(
            ports=[
                PortResponse(
                    id=port.id,
                    port_name=port.port_name,
                    device_id=port.device_id,
                    vendor_id=port.vendor_id,
                    product_id=port.product_id,
                    description=port.description,
                    is_active=port.is_active,
                    is_assigned=port.is_assigned,
                    detected_at=port.detected_at,
                    last_updated=port.last_updated,
                )
                for port in ports
            ],
            timestamp=datetime.utcnow(),
            available_count=len(available_ports),
            assigned_count=len([p for p in ports if p.is_assigned]),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Port discovery failed: {str(e)}")


@router.get("", response_model=PortListResponse)
async def get_ports(
    active_only: bool = Query(False, description="Filter only active ports"),
    db: Session = Depends(get_db)
):
    """
    Get all ports with optional filtering.

    Query Parameters:
        active_only: If true, return only active ports

    Returns:
        List of ports and total count
    """
    ports = PortService.get_all_ports(db, active_only=active_only)

    return PortListResponse(
        ports=[
            PortResponse(
                id=port.id,
                port_name=port.port_name,
                device_id=port.device_id,
                vendor_id=port.vendor_id,
                product_id=port.product_id,
                description=port.description,
                is_active=port.is_active,
                is_assigned=port.is_assigned,
                detected_at=port.detected_at,
                last_updated=port.last_updated,
            )
            for port in ports
        ],
        total=len(ports),
    )


@router.get("/{port_id}", response_model=PortResponse)
async def get_port(port_id: int, db: Session = Depends(get_db)):
    """
    Get a specific port by ID.

    Path Parameters:
        port_id: Port ID

    Returns:
        Port details
    """
    port = PortService.get_port_by_id(db, port_id)
    if not port:
        raise HTTPException(status_code=404, detail=f"Port {port_id} not found")

    return PortResponse(
        id=port.id,
        port_name=port.port_name,
        device_id=port.device_id,
        vendor_id=port.vendor_id,
        product_id=port.product_id,
        description=port.description,
        is_active=port.is_active,
        is_assigned=port.is_assigned,
        detected_at=port.detected_at,
        last_updated=port.last_updated,
    )


@router.post("", response_model=PortResponse, status_code=201)
async def create_port(port_data: PortCreate, db: Session = Depends(get_db)):
    """
    Create a new port entry.

    Request Body:
        port_name: System port name
        vendor_id: USB vendor ID
        product_id: USB product ID
        description: Port description

    Returns:
        Created port details
    """
    # Check if port already exists
    existing = PortService.get_port_by_name(db, port_data.port_name)
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Port {port_data.port_name} already exists"
        )

    port = PortService.create_port(db, port_data)
    return PortResponse(
        id=port.id,
        port_name=port.port_name,
        device_id=port.device_id,
        vendor_id=port.vendor_id,
        product_id=port.product_id,
        description=port.description,
        is_active=port.is_active,
        is_assigned=port.is_assigned,
        detected_at=port.detected_at,
        last_updated=port.last_updated,
    )


@router.put("/{port_id}", response_model=PortResponse)
async def update_port(
    port_id: int,
    port_data: PortUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a port.

    Path Parameters:
        port_id: Port ID

    Request Body:
        is_active: Port active status
        is_assigned: Port assignment status
        description: Port description

    Returns:
        Updated port details
    """
    port = PortService.update_port(db, port_id, port_data)
    if not port:
        raise HTTPException(status_code=404, detail=f"Port {port_id} not found")

    return PortResponse(
        id=port.id,
        port_name=port.port_name,
        device_id=port.device_id,
        vendor_id=port.vendor_id,
        product_id=port.product_id,
        description=port.description,
        is_active=port.is_active,
        is_assigned=port.is_assigned,
        detected_at=port.detected_at,
        last_updated=port.last_updated,
    )


@router.get("/available", response_model=PortListResponse)
async def get_available_ports(db: Session = Depends(get_db)):
    """
    Get available ports (active and not assigned to any motor).

    Returns:
        List of available ports
    """
    ports = PortService.get_available_ports(db)

    return PortListResponse(
        ports=[
            PortResponse(
                id=port.id,
                port_name=port.port_name,
                device_id=port.device_id,
                vendor_id=port.vendor_id,
                product_id=port.product_id,
                description=port.description,
                is_active=port.is_active,
                is_assigned=port.is_assigned,
                detected_at=port.detected_at,
                last_updated=port.last_updated,
            )
            for port in ports
        ],
        total=len(ports),
    )
