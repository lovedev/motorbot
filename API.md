# Motor Setup and Monitoring Dashboard - API Documentation

## Overview

This document provides reference documentation for the Motor Setup and Monitoring Dashboard API. The API is built with FastAPI and provides endpoints for:

- Port discovery and management
- Motor configuration and setup
- Real-time telemetry streaming via WebSocket
- Motor testing and validation
- Operation logging and history

## Base URL

```
http://localhost:8000
```

## API Documentation Tools

### Interactive API Documentation

- **Swagger UI**: `GET /docs` - Interactive API explorer
- **ReDoc**: `GET /redoc` - Alternative documentation viewer
- **OpenAPI Schema**: `GET /openapi.json` - Raw OpenAPI specification

## Core Endpoints

### Health & Status

#### Health Check
- **Endpoint**: `GET /api/health`
- **Description**: Check API service health status
- **Response**:
  ```json
  {
    "status": "healthy",
    "service": "motor-dashboard-api"
  }
  ```

### Port Management

Port endpoints handle USB port discovery and management.

#### Discover Ports
- **Endpoint**: `GET /api/ports/discover`
- **Description**: Discover available USB ports
- **Response**:
  ```json
  {
    "ports": [
      {
        "id": 1,
        "port_name": "/dev/ttyUSB0",
        "vendor_id": "0403",
        "product_id": "6001",
        "description": "FT232R USB UART",
        "is_active": true,
        "is_assigned": false,
        "detected_at": "2024-11-09T10:30:00Z"
      }
    ]
  }
  ```

#### Get All Ports
- **Endpoint**: `GET /api/ports`
- **Description**: Get list of all detected ports
- **Query Parameters**:
  - `active_only` (bool, optional): Filter only active ports (default: false)

#### Get Port Details
- **Endpoint**: `GET /api/ports/{port_id}`
- **Description**: Get details for a specific port
- **Path Parameters**:
  - `port_id` (int): Port ID

### Motor Management

Motor endpoints handle motor configuration and control.

#### List Motors
- **Endpoint**: `GET /api/motors`
- **Description**: Get list of all motors
- **Query Parameters**:
  - `calibrated_only` (bool, optional): Filter only calibrated motors
  - `functional_only` (bool, optional): Filter only functional motors

#### Get Motor Details
- **Endpoint**: `GET /api/motors/{motor_id}`
- **Description**: Get details for a specific motor
- **Path Parameters**:
  - `motor_id` (int): Motor ID (1-12)
- **Response**:
  ```json
  {
    "id": 1,
    "name": "Shoulder Motor",
    "motor_index": 0,
    "port_id": 1,
    "model": "MG996R",
    "serial_number": "SN123456",
    "max_speed": 60,
    "max_torque": 12.0,
    "is_calibrated": false,
    "is_functional": true,
    "created_at": "2024-11-09T10:30:00Z",
    "last_updated": "2024-11-09T10:30:00Z"
  }
  ```

#### Create Motor
- **Endpoint**: `POST /api/motors`
- **Description**: Create a new motor configuration
- **Request Body**:
  ```json
  {
    "name": "Shoulder Motor",
    "motor_index": 0,
    "port_id": 1,
    "model": "MG996R",
    "serial_number": "SN123456"
  }
  ```

#### Update Motor
- **Endpoint**: `PUT /api/motors/{motor_id}`
- **Description**: Update motor configuration
- **Path Parameters**:
  - `motor_id` (int): Motor ID

#### Calibrate Motor
- **Endpoint**: `POST /api/motors/{motor_id}/calibrate`
- **Description**: Start motor calibration process
- **Path Parameters**:
  - `motor_id` (int): Motor ID
- **Response**:
  ```json
  {
    "motor_id": 1,
    "status": "calibration_started",
    "message": "Motor calibration in progress"
  }
  ```

### Motor Configuration

#### Get Configuration
- **Endpoint**: `GET /api/motors/{motor_id}/config`
- **Description**: Get motor configuration parameters
- **Path Parameters**:
  - `motor_id` (int): Motor ID

#### Update Configuration
- **Endpoint**: `PUT /api/motors/{motor_id}/config`
- **Description**: Update motor configuration
- **Path Parameters**:
  - `motor_id` (int): Motor ID
- **Request Body**:
  ```json
  {
    "min_angle": 0,
    "max_angle": 180,
    "default_speed": 50,
    "default_torque": 75,
    "acceleration": 10,
    "deceleration": 10
  }
  ```

### Motor Testing

#### Run Test
- **Endpoint**: `POST /api/motors/{motor_id}/test`
- **Description**: Run a test on a motor
- **Path Parameters**:
  - `motor_id` (int): Motor ID
- **Query Parameters**:
  - `test_type` (string): Type of test (communication, speed, torque, temperature)
- **Response**:
  ```json
  {
    "test_id": 1,
    "motor_id": 1,
    "test_type": "communication",
    "status": "running"
  }
  ```

#### Get Test Results
- **Endpoint**: `GET /api/motors/{motor_id}/tests`
- **Description**: Get test history for a motor
- **Path Parameters**:
  - `motor_id` (int): Motor ID

## WebSocket Endpoints

### Real-time Telemetry Stream

#### Subscribe to Motor Telemetry
- **Endpoint**: `WS /ws/motors/{motor_id}/telemetry`
- **Description**: Stream real-time telemetry data for a motor
- **Path Parameters**:
  - `motor_id` (int): Motor ID
- **Message Format**:
  ```json
  {
    "timestamp": "2024-11-09T10:30:00Z",
    "current_angle": 45.5,
    "target_angle": 90.0,
    "current_speed": 30,
    "current_torque": 5.2,
    "temperature": 35.2,
    "voltage": 12.0,
    "current": 0.5
  }
  ```

#### Subscribe to Dashboard Telemetry
- **Endpoint**: `WS /ws/dashboard/telemetry`
- **Description**: Stream telemetry for all motors
- **Message Format**:
  ```json
  {
    "timestamp": "2024-11-09T10:30:00Z",
    "motors": [
      {
        "motor_id": 1,
        "current_angle": 45.5,
        "current_speed": 30,
        "temperature": 35.2
      }
    ]
  }
  ```

## Operation Logging

#### Get Operation History
- **Endpoint**: `GET /api/motors/{motor_id}/operations`
- **Description**: Get operation history for a motor
- **Path Parameters**:
  - `motor_id` (int): Motor ID
- **Query Parameters**:
  - `operation_type` (string, optional): Filter by operation type
  - `limit` (int, optional): Maximum results (default: 50)
  - `offset` (int, optional): Pagination offset

## Error Handling

### Error Response Format

All errors follow this format:

```json
{
  "detail": "Error message description",
  "status_code": 400,
  "error_type": "validation_error"
}
```

### Common Status Codes

- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request parameters
- **404 Not Found**: Resource not found
- **409 Conflict**: Resource conflict (e.g., port already assigned)
- **500 Internal Server Error**: Server error

## Authentication & Security

Currently, the API has no authentication layer (development mode).

For production deployment:
- Implement JWT-based authentication
- Use HTTPS for all endpoints
- Implement rate limiting
- Add CORS security headers
- Validate all inputs

## Rate Limiting

Not currently implemented. To be added in production:
- Rate limit: 100 requests per minute per IP
- WebSocket limit: 10 concurrent connections per IP

## Pagination

Endpoints that return collections support pagination:

```json
{
  "items": [...],
  "total": 100,
  "limit": 50,
  "offset": 0
}
```

## Versioning

Current API version: **1.0.0**

## Changelog

### v1.0.0 (2024-11-09)
- Initial API release
- Port discovery and management
- Motor configuration endpoints
- WebSocket telemetry streaming
- Test execution endpoints
- Operation logging

## Support

For API questions or issues, refer to:
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [OpenAPI Specification](https://spec.openapis.org/oas/v3.0.3)
- Interactive documentation at `/docs`
