# Data Model: Motor Setup and Monitoring Dashboard

**Date**: 2025-11-09
**Feature**: Motor Setup and Monitoring Dashboard (001-motor-setup-dashboard)
**Purpose**: Define all data entities, relationships, and validation rules

---

## Core Entities

### 1. Port

Represents a USB serial port connection to a motor controller.

```typescript
interface Port {
  port_id: string;              // Unique identifier (e.g., "ttyACM0", "COM3")
  device_name: string;          // Full device path (e.g., "/dev/ttyACM0")
  device_id?: string;           // USB device ID (manufacturer:product)
  user_label?: string;          // User-friendly name (e.g., "Left Arm Port")
  is_active: boolean;           // Currently connected to USB bus
  last_tested_at?: ISO8601;     // Timestamp of last successful test
  test_status?: 'success' | 'failure' | 'timeout';
  connected_motor_id?: number;  // FK to Motor (which motor is on this port)
  created_at: ISO8601;
  updated_at: ISO8601;
}
```

**Validation Rules**:
- `port_id`: Must be non-empty, unique among active ports
- `device_name`: Must match OS serial port naming convention
- `user_label`: Optional, max 50 characters, unique if provided
- `is_active`: Automatically set based on OS port enumeration

**State Transitions**:
```
Discovered (is_active=true)
  ↓
Tested (test_status = success/failure)
  ↓
Labeled (user_label set)
  ↓
Configured (connected_motor_id set)
```

---

### 2. Motor

Represents a single servo motor in the 12-motor configuration.

```typescript
interface Motor {
  motor_id: number;              // 1-12 (position in arm)
  motor_type: string;            // "STS3215", "STS4015", etc.
  port_id: string;               // FK to Port (which USB port this motor uses)
  status: 'unconfigured' | 'configured' | 'online' | 'offline' | 'error';

  // Configuration
  max_torque: number;            // Newton-meters (Nm)
  max_velocity: number;          // Degrees per second (°/s)
  min_position: number;          // Degrees (°)
  max_position: number;          // Degrees (°)

  // Real-time State
  current_position?: number;     // Current position (°)
  current_velocity?: number;     // Current velocity (°/s)
  current_torque?: number;       // Current torque (Nm)
  current_temperature?: number;  // Temperature (°C)

  // Health Status
  health_status: 'healthy' | 'warning' | 'error';
  error_condition?: string;      // "OVERHEAT", "POSITION_LIMIT", "TORQUE_LIMIT", "NOT_RESPONDING"
  last_telemetry_at?: ISO8601;

  // History
  error_log: OperationLog[];     // List of recent errors
  test_history: MotorTestEvent[];
  created_at: ISO8601;
  updated_at: ISO8601;
}
```

**Validation Rules**:
- `motor_id`: Must be integer 1-12
- `motor_type`: Must be recognized motor type (whitelist: STS3215, STS4015, etc.)
- `port_id`: Must reference existing, tested Port
- `max_torque`: Must be positive number > 0
- `max_velocity`: Must be positive number > 0
- `min_position` < `max_position`: Always enforced
- Torque/velocity: Must not exceed motor hardware limits

**State Transitions**:
```
Unconfigured (port_id not set)
  ↓ (port discovered and labeled)
Configured (port_id set, parameters valid)
  ↓ (motor responds to telemetry requests)
Online (actively sending telemetry)

Online
  ↓ (no telemetry for 3 seconds)
Offline

Online/Offline
  ↓ (overheat, position limit, torque limit)
Error (with error_condition set)
```

---

### 3. MotorConfiguration

Represents the complete system configuration (all 12 motors).

```typescript
interface MotorConfiguration {
  config_id: string;             // UUID
  name: string;                  // "SO-ARM 101 Setup 1", etc.
  description?: string;
  motors: Motor[];               // Array of 12 Motor objects

  // Validation state
  is_valid: boolean;
  validation_errors: ValidationError[];

  // Metadata
  created_at: ISO8601;
  updated_at: ISO8601;
  saved_at?: ISO8601;            // Last successful save
  applied_at?: ISO8601;          // Last time config was loaded and applied
}

interface ValidationError {
  motor_id: number;
  field: string;
  message: string;
  severity: 'error' | 'warning';
}
```

**Validation Rules**:
- Must have exactly 12 motors
- All motors must have valid port_id (no duplicates)
- All motors must have motor_id 1-12 (no duplicates)
- All motors must have valid configuration (no incomplete motors)
- No circular dependencies

**Validation Workflow**:
```
User clicks "Save Configuration"
  ↓ (frontend validation)
Validate all 12 motors (required fields)
  ↓ (send to backend)
Backend validates (business rules)
  ↓
If valid: Save to database, return success
If invalid: Return validation_errors array
  ↓ (frontend displays errors)
User corrects and retries
```

---

### 4. TelemetryDataPoint

Represents a single telemetry reading from a motor.

```typescript
interface TelemetryDataPoint {
  telemetry_id: string;          // UUID
  motor_id: number;              // FK to Motor
  timestamp: ISO8601;            // When reading was taken

  // Sensor Readings
  position: number;              // Current position (°)
  velocity: number;              // Current velocity (°/s)
  torque: number;                // Current torque (Nm)
  temperature: number;           // Current temperature (°C)
  battery_voltage?: number;      // Optional: supply voltage (V)

  // Status Flags
  status_flags: {
    is_online: boolean;
    has_error: boolean;
    is_moving: boolean;
    temperature_warning: boolean;
    position_limit_reached: boolean;
    torque_limit_reached: boolean;
  };

  // Error Context
  error_message?: string;
  error_code?: number;
}
```

**Validation Rules**:
- `position`: Must be between motor's min/max position
- `velocity`: Must be between 0 and motor's max_velocity
- `torque`: Must be between 0 and motor's max_torque
- `temperature`: Typically 20-80°C (warning if >70°C)
- `timestamp`: Must be recent (within last 5 seconds for "fresh" data)

**Data Collection**:
- Backend collects telemetry at ~50-100Hz (from motor controllers)
- Aggregated and broadcast to frontend via WebSocket at ~20Hz (50ms interval)
- Stored in database for historical analysis (sampled, not every reading)

---

### 5. OperationLog

Represents a recorded motor operation, test, or error event.

```typescript
interface OperationLog {
  log_id: string;                // UUID
  motor_id: number;              // FK to Motor
  operation_type: 'test_command' | 'error' | 'state_change' | 'configuration' | 'emergency_stop';
  timestamp: ISO8601;
  user_action?: string;          // What user did (e.g., "Send Test Command")

  // Details
  details: {
    command?: string;            // Command sent (e.g., "MOVE_TO_45")
    command_params?: Record<string, any>;
    response?: string;           // Response received
    success: boolean;
    error_message?: string;
    duration_ms?: number;        // How long operation took
  };

  // Severity & Categorization
  severity: 'info' | 'warning' | 'error' | 'critical';
  category: string;              // "OVERHEAT", "POSITION_LIMIT", etc.

  // Context
  session_id?: string;           // Which user session (for future multi-user)
  metadata?: Record<string, any>;
}
```

**Validation Rules**:
- `operation_type`: Must be one of predefined types
- `timestamp`: Must be valid ISO8601, must be recent
- `severity`: Cannot be critical without error_message
- `details.success`: Boolean, must match presence of error_message

**Log Retention**:
- Keep all logs for past 30 days
- Archive older logs (separate table or export)
- Compress logs older than 7 days

---

### 6. MotorTestEvent

Represents the result of a motor test command sent by user.

```typescript
interface MotorTestEvent {
  test_id: string;               // UUID
  motor_id: number;              // FK to Motor
  test_type: 'position_move' | 'velocity_check' | 'torque_measure' | 'temperature_check' | 'emergency_stop_test';
  timestamp: ISO8601;

  // Test Parameters
  parameters: {
    target_position?: number;    // For position_move
    target_velocity?: number;    // For velocity_check
    duration_ms?: number;        // How long to run
  };

  // Test Results
  success: boolean;
  start_state: TelemetryDataPoint;
  end_state: TelemetryDataPoint;
  duration_ms: number;           // Actual execution time

  // Pass/Fail Criteria
  passed_criteria: string[];     // ["Position reached", "No temperature warning"]
  failed_criteria: string[];     // ["Torque limit exceeded", ...]

  error?: string;                // If test failed
  notes?: string;                // User notes
}
```

**Validation Rules**:
- `test_type`: Must be valid test type
- Parameters required based on test_type
- `start_state` and `end_state` must have valid TelemetryDataPoint
- `duration_ms` > 0
- If failed_criteria.length > 0, success must be false

---

## Relationships & Cardinality

```
Port (1) ──────────────── (0..1) Motor
         connected_motor_id

Motor (1) ──────────────── (0..12) Motor
         parent (in MotorConfiguration)

Motor (1) ──────────────── (0..*) TelemetryDataPoint
         motor_id

Motor (1) ──────────────── (0..*) OperationLog
         motor_id

Motor (1) ──────────────── (0..*) MotorTestEvent
         motor_id

MotorConfiguration (1) ────────────── (12) Motor
                      contains
```

---

## Database Schema (SQLite)

```sql
-- Ports table
CREATE TABLE ports (
  port_id TEXT PRIMARY KEY,
  device_name TEXT NOT NULL UNIQUE,
  device_id TEXT,
  user_label TEXT UNIQUE,
  is_active BOOLEAN NOT NULL DEFAULT true,
  last_tested_at TIMESTAMP,
  test_status TEXT,
  connected_motor_id INTEGER,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (connected_motor_id) REFERENCES motors(motor_id)
);

-- Motors table
CREATE TABLE motors (
  motor_id INTEGER PRIMARY KEY CHECK (motor_id >= 1 AND motor_id <= 12),
  motor_type TEXT NOT NULL,
  port_id TEXT NOT NULL UNIQUE,
  status TEXT NOT NULL DEFAULT 'unconfigured',
  max_torque REAL NOT NULL,
  max_velocity REAL NOT NULL,
  min_position REAL NOT NULL,
  max_position REAL NOT NULL,
  current_position REAL,
  current_velocity REAL,
  current_torque REAL,
  current_temperature REAL,
  health_status TEXT NOT NULL DEFAULT 'healthy',
  error_condition TEXT,
  last_telemetry_at TIMESTAMP,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (port_id) REFERENCES ports(port_id),
  CHECK (min_position < max_position),
  CHECK (max_torque > 0),
  CHECK (max_velocity > 0)
);

-- Motor Configurations table
CREATE TABLE motor_configurations (
  config_id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  is_valid BOOLEAN NOT NULL DEFAULT false,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  saved_at TIMESTAMP,
  applied_at TIMESTAMP
);

-- Telemetry Data table
CREATE TABLE telemetry_data (
  telemetry_id TEXT PRIMARY KEY,
  motor_id INTEGER NOT NULL,
  timestamp TIMESTAMP NOT NULL,
  position REAL NOT NULL,
  velocity REAL NOT NULL,
  torque REAL NOT NULL,
  temperature REAL NOT NULL,
  battery_voltage REAL,
  status_flags JSON NOT NULL,
  error_message TEXT,
  error_code INTEGER,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (motor_id) REFERENCES motors(motor_id),
  INDEX idx_motor_timestamp (motor_id, timestamp)
);

-- Operation Logs table
CREATE TABLE operation_logs (
  log_id TEXT PRIMARY KEY,
  motor_id INTEGER NOT NULL,
  operation_type TEXT NOT NULL,
  timestamp TIMESTAMP NOT NULL,
  user_action TEXT,
  details JSON NOT NULL,
  severity TEXT NOT NULL,
  category TEXT,
  session_id TEXT,
  metadata JSON,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (motor_id) REFERENCES motors(motor_id),
  INDEX idx_motor_timestamp (motor_id, timestamp)
);

-- Motor Test Events table
CREATE TABLE motor_test_events (
  test_id TEXT PRIMARY KEY,
  motor_id INTEGER NOT NULL,
  test_type TEXT NOT NULL,
  timestamp TIMESTAMP NOT NULL,
  parameters JSON NOT NULL,
  success BOOLEAN NOT NULL,
  start_state JSON NOT NULL,
  end_state JSON NOT NULL,
  duration_ms INTEGER NOT NULL,
  passed_criteria JSON NOT NULL,
  failed_criteria JSON NOT NULL,
  error TEXT,
  notes TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (motor_id) REFERENCES motors(motor_id),
  INDEX idx_motor_timestamp (motor_id, timestamp)
);
```

---

## State Machine Diagrams

### Motor Status State Machine

```
[Unconfigured]
     ↓ (port_id assigned, config saved)
     ↓
[Configured] ──→ [Online] ←──→ [Offline]
                    ↓  ↑           ↓
                    └──[Error]─────┘
                       (overheat, position limit, torque limit)
```

### Port Status State Machine

```
[Discovered] ──→ [Tested (Success)] ──→ [Labeled] ──→ [Configured]
     ↓
     └────→ [Tested (Failed)] ↗

[*] ──→ [Disconnected] (when is_active becomes false)
```

---

## Type Definitions (TypeScript Frontend)

```typescript
// motor.ts
export interface Motor {
  motor_id: number;
  motor_type: string;
  port_id: string;
  status: 'unconfigured' | 'configured' | 'online' | 'offline' | 'error';
  max_torque: number;
  max_velocity: number;
  min_position: number;
  max_position: number;
  current_position?: number;
  current_velocity?: number;
  current_torque?: number;
  current_temperature?: number;
  health_status: 'healthy' | 'warning' | 'error';
  error_condition?: string;
  last_telemetry_at?: string;
  error_log: OperationLog[];
  test_history: MotorTestEvent[];
  created_at: string;
  updated_at: string;
}

// port.ts
export interface Port {
  port_id: string;
  device_name: string;
  device_id?: string;
  user_label?: string;
  is_active: boolean;
  last_tested_at?: string;
  test_status?: 'success' | 'failure' | 'timeout';
  connected_motor_id?: number;
  created_at: string;
  updated_at: string;
}

// telemetry.ts
export interface TelemetryUpdate {
  timestamp: string;
  motors: Array<{
    motor_id: number;
    position: number;
    velocity: number;
    torque: number;
    temperature: number;
    status: 'healthy' | 'warning' | 'error';
    error?: string;
  }>;
}

// api.ts (request/response types)
export interface TestPortRequest {
  port_id: string;
}

export interface TestPortResponse {
  success: boolean;
  port_id: string;
  device_id?: string;
  error?: string;
}

export interface SaveMotorConfigRequest {
  motors: Motor[];
}

export interface SaveMotorConfigResponse {
  success: boolean;
  config_id: string;
  validation_errors?: ValidationError[];
}
```

---

## Data Persistence Strategy

### Configuration Data
- **Frequency**: Persist on explicit user save (after configuration wizard)
- **Storage**: SQLite motors table
- **Backup**: Auto-backup to JSON file in user home directory

### Telemetry Data
- **Frequency**: Real-time collection at source (50-100Hz), aggregated and sent to UI at 20Hz
- **Storage**: Retain latest 24 hours, archive older data (optional)
- **Sampling**: Every 5th reading stored to database (to manage disk usage)

### Operation Logs
- **Frequency**: Immediate write on each operation
- **Storage**: SQLite operation_logs table
- **Retention**: 30 days default, user-configurable (7-90 days)

---

## Next Steps

1. Create Pydantic models in `motorbot-backend/app/database/models.py`
2. Generate OpenAPI schema from these models
3. Create SQLAlchemy ORM models
4. Create TypeScript interfaces in `motorbot-frontend/src/types/`
