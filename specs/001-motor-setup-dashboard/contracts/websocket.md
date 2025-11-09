# WebSocket Protocol Specification

**Feature**: Motor Setup and Monitoring Dashboard
**Purpose**: Real-time telemetry streaming from backend to frontend

---

## Connection Details

### Endpoint
```
ws://localhost:8000/ws/telemetry
wss://example.com/ws/telemetry  (production with TLS)
```

### Authentication
- **Current Implementation**: None required (single-user desktop app)
- **Future**: Optional bearer token in query parameter

### Connection Lifecycle

```
Client (Browser)                    Server (FastAPI)
       │                                    │
       ├──────── WebSocket Connect ────────→│
       │                                    │
       │←────────── Connection ACK ────────┤
       │                                    │
       │←──── Telemetry Update (50ms) ─────┤
       │←──── Telemetry Update (50ms) ─────┤
       │←──── Telemetry Update (50ms) ─────┤
       │                                    │
       ├──────── Close Connection ─────────→│
       │                                    │
       │←───────── Close Confirmation ─────┤
       │                                    │
```

---

## Message Types

### 1. Telemetry Update (Server → Client)

**Frequency**: Every 50ms (20 Hz) when motors are configured and running

**Message Structure**:
```json
{
  "type": "telemetry_update",
  "timestamp": "2025-11-09T12:34:56.789Z",
  "motors": [
    {
      "motor_id": 1,
      "position": 45.5,
      "velocity": 23.1,
      "torque": 12.3,
      "temperature": 38.5,
      "status": "healthy",
      "error": null
    },
    {
      "motor_id": 2,
      "position": 32.1,
      "velocity": 15.8,
      "torque": 8.9,
      "temperature": 40.2,
      "status": "healthy",
      "error": null
    },
    // ... motors 3-12 ...
    {
      "motor_id": 12,
      "position": null,
      "velocity": null,
      "torque": null,
      "temperature": null,
      "status": "offline",
      "error": "No telemetry received (port disconnected?)"
    }
  ],
  "sequence_number": 1234
}
```

**Field Descriptions**:
- `type`: String, always "telemetry_update"
- `timestamp`: ISO 8601 timestamp when data was collected
- `motors`: Array of exactly 12 motor objects (even if offline)
- `motors[i].status`: One of "healthy", "warning", "error", "offline"
- `motors[i].error`: null if healthy, error message string if not
- `sequence_number`: Monotonically increasing, useful for detecting dropped messages

**Status Mapping**:
- **healthy**: All telemetry values nominal, no errors
- **warning**: One or more metrics approaching limits (temp >65°C, torque >90% max, etc.)
- **error**: Motor has error condition (overheat, position limit, torque limit)
- **offline**: Motor not responding (port disconnected or motor powered off)

**Error Examples**:
```json
{
  "motor_id": 5,
  "status": "error",
  "error": "OVERHEAT: Temperature 85°C exceeds max 80°C"
}
```

```json
{
  "motor_id": 8,
  "status": "error",
  "error": "POSITION_LIMIT: Current position 0° at minimum limit"
}
```

```json
{
  "motor_id": 12,
  "status": "offline",
  "error": "No response on port /dev/ttyACM3 for 3+ seconds"
}
```

---

### 2. Connection Confirmation (Server → Client)

**Timing**: Sent immediately after WebSocket connection established

```json
{
  "type": "connection_confirmed",
  "timestamp": "2025-11-09T12:34:50.000Z",
  "message": "Connected to telemetry stream",
  "server_version": "1.0.0"
}
```

---

### 3. Configuration Update (Server → Client)

**Timing**: Sent when motor configuration changes (via REST API POST /api/motors/config)

```json
{
  "type": "configuration_updated",
  "timestamp": "2025-11-09T12:34:56.789Z",
  "config_id": "uuid-12345",
  "message": "Motor configuration updated"
}
```

**Purpose**: Notifies frontend that configuration changed (possibly from another tab/window), triggers reload

---

### 4. Error Message (Server → Client)

**Timing**: Sent when server encounters error (e.g., serial port failure)

```json
{
  "type": "error",
  "timestamp": "2025-11-09T12:34:56.789Z",
  "error_code": "PORT_ENUMERATION_FAILED",
  "message": "Failed to enumerate serial ports: Permission denied",
  "severity": "warning",
  "recoverable": true
}
```

**Error Codes**:
- `PORT_ENUMERATION_FAILED`: Cannot enumerate serial ports (permission/hardware issue)
- `TELEMETRY_COLLECTION_FAILED`: Error collecting telemetry from one or more motors
- `DATABASE_ERROR`: Cannot save logs or configuration
- `SERVER_ERROR`: Unexpected internal server error

**Severity**:
- `info`: Informational message
- `warning`: Warning, non-critical (e.g., high latency)
- `error`: Error occurred, but service continuing
- `critical`: Critical error, service may stop

---

### 5. Connection Status (Server → Client)

**Timing**: Sent periodically (every 5 seconds) or on status change

```json
{
  "type": "connection_status",
  "timestamp": "2025-11-09T12:34:56.789Z",
  "status": "healthy",
  "metrics": {
    "message_count": 1234,
    "last_telemetry_age_ms": 45,
    "connected_motors": 11,
    "disconnected_motors": 1,
    "pending_messages": 0
  }
}
```

**Status Values**:
- `healthy`: All systems operational, telemetry flowing
- `degraded`: Some motors offline, but service continuing
- `disconnected`: WebSocket disconnected from server
- `error`: Error occurred, may not be receiving telemetry

---

## Client → Server Messages (Future Extensibility)

Currently, clients receive only (no send required). Future messages might include:

### Command Acknowledgment Request
```json
{
  "type": "request_ack",
  "sequence_number": 1234
}
```

### Motor Test Command Initiation
```json
{
  "type": "motor_test",
  "motor_id": 5,
  "test_type": "position_move",
  "target_position": 45.0
}
```

*Note: Currently use REST API POST /api/motors/{id}/test instead*

---

## Error Handling & Recovery

### Client Reconnection Logic

```javascript
const reconnect = async () => {
  const maxRetries = 5;
  const baseDelay = 1000; // ms

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      await connectWebSocket();
      return; // Success
    } catch (error) {
      const delay = baseDelay * Math.pow(2, attempt); // Exponential backoff
      console.log(`Reconnect attempt ${attempt + 1} failed, retrying in ${delay}ms...`);
      await sleep(delay);
    }
  }

  // All retries exhausted
  showError("Failed to connect to telemetry stream after 5 attempts");
};
```

### Server Connection Timeout

- **Read timeout**: No message received for 10 seconds → close connection
- **Write timeout**: Cannot send message for 5 seconds → log error, continue
- **Telemetry stale**: No fresh telemetry for >3 seconds → mark motors as offline

### Network Interruption Recovery

- **Brief interruption** (<10 seconds): Automatic reconnect, resume telemetry
- **Extended interruption** (>30 seconds): Show "Disconnected" UI state, prompt user
- **Message buffering**: During reconnect, don't queue messages; show "stale" indicator

---

## Message Frequency & Bandwidth

### Telemetry Update Frequency

| Scenario | Frequency | Bytes per Message | Bandwidth |
|----------|-----------|-------------------|-----------|
| All 12 motors online | 20 Hz (50ms) | ~2.5 KB | ~50 KB/s |
| 6 motors online, 6 offline | 20 Hz | ~1.5 KB | ~30 KB/s |
| All offline | 1 Hz (1s) | ~1.5 KB | ~1.5 KB/s |

### Optimization Strategies

1. **Delta compression**: Send only changed values (not yet implemented)
2. **Message batching**: Group multiple updates (not applicable at 50ms interval)
3. **Sampling**: Reduce update frequency during high CPU usage (future)
4. **Binary encoding**: Use MessagePack instead of JSON (future optimization)

---

## Example Client Implementation (React)

```typescript
// hooks/useWebSocket.ts
import { useEffect, useRef, useCallback } from 'react';
import { TelemetryUpdate } from '@/types/telemetry';

export const useWebSocket = (onTelemetry: (data: TelemetryUpdate) => void) => {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);

  const connect = useCallback(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const url = `${protocol}//${window.location.host}/ws/telemetry`;

    wsRef.current = new WebSocket(url);

    wsRef.current.onopen = () => {
      console.log('WebSocket connected');
      reconnectAttemptsRef.current = 0;
    };

    wsRef.current.onmessage = (event) => {
      const message = JSON.parse(event.data);

      switch (message.type) {
        case 'telemetry_update':
          onTelemetry(message);
          break;
        case 'error':
          console.error('WebSocket error:', message);
          break;
        case 'connection_confirmed':
          console.log('Connection confirmed:', message);
          break;
      }
    };

    wsRef.current.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    wsRef.current.onclose = () => {
      console.log('WebSocket disconnected');
      reconnectWithBackoff();
    };
  }, [onTelemetry]);

  const reconnectWithBackoff = useCallback(() => {
    if (reconnectAttemptsRef.current < 5) {
      const delay = Math.pow(2, reconnectAttemptsRef.current) * 1000;
      reconnectAttemptsRef.current += 1;
      setTimeout(connect, delay);
    }
  }, [connect]);

  useEffect(() => {
    connect();
    return () => {
      wsRef.current?.close();
    };
  }, [connect]);

  return {
    isConnected: wsRef.current?.readyState === WebSocket.OPEN,
  };
};
```

---

## Testing & Debugging

### WebSocket Test Server (for development)

```bash
# Start test server that generates fake telemetry
python motorbot-backend/tests/websocket_test_server.py
```

### Browser Console Testing

```javascript
// Connect to WebSocket manually
const ws = new WebSocket('ws://localhost:8000/ws/telemetry');
ws.onmessage = (e) => console.log(JSON.parse(e.data));
ws.send(JSON.stringify({ type: 'ping' }));
```

### Network Inspection

- **Chrome DevTools**: Network tab → WS → Messages (shows all frames)
- **WebSocket Inspector Extensions**: Monitor frame size, latency, etc.

---

## Future Enhancements

1. **Bidirectional commands**: Send motor test commands over WebSocket
2. **Binary frames**: Reduce bandwidth using MessagePack/protobuf
3. **Message compression**: gzip compression for large payloads
4. **Priority queuing**: High-priority alerts sent immediately
5. **Heartbeat/ping-pong**: Detect stale connections sooner
