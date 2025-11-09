# Research & Design Decisions: Motor Setup and Monitoring Dashboard

**Date**: 2025-11-09
**Feature**: Motor Setup and Monitoring Dashboard (001-motor-setup-dashboard)
**Purpose**: Document technology choices, architectural patterns, and design rationale

---

## 1. UI/UX Framework & Styling

### Decision: shadcn-ui + Tailwind CSS + React

**Rationale**:
- User explicitly requested shadcn-ui for component styling
- shadcn-ui uses Radix UI for accessible components + Tailwind CSS for styling
- Provides consistent dark theme matching Hugging Face design system (user provided reference screenshot)
- Excellent TypeScript support for type-safe component development
- Extensive component library (buttons, forms, cards, alerts, etc.) ready for dashboard implementation
- Easy customization and theming for dark mode

**Alternatives Considered**:
- Material-UI: More opinionated, heavier bundle size
- Bootstrap: Less modern, less TypeScript-friendly
- Custom CSS: Would require more development time for consistent styling

**Implementation**:
- Install shadcn-ui via CLI with dark theme preset
- Use Tailwind CSS for responsive layout (Hugging Face-style: header + sidebar + content area)
- Create theme configuration matching screenshot colors (dark background, light text)

---

## 2. Frontend Framework Architecture

### Decision: React 18+ with NestJS (API layer)

**User Request Interpretation**: User mentioned "NestJS 그리고 typescript 기반으로" which indicated TypeScript + structured backend for API

**Rationale**:
- React 18+ provides modern hooks and concurrent rendering for responsive UI
- NestJS can provide a lightweight API gateway layer between React frontend and Python backend
- Alternative: Direct React + Vite without NestJS API layer
- **Final Decision**: Use React 18+ with Vite for frontend (no NestJS intermediary). Python FastAPI provides API directly.

**Alternative Considered**:
- NestJS full backend (but user specified "backend는 fastapi와 python 기반으로", so FastAPI is primary backend)
- Resolved: React 18 + Vite for frontend, FastAPI for backend services

**Component Architecture**:
- Page-based routing (React Router v6)
- Custom hooks for business logic (useMotorData, useWebSocket, useConfiguration)
- Container/Presentational component pattern
- Shared UI components from shadcn-ui

---

## 3. Real-Time Communication

### Decision: WebSocket via FastAPI

**Rationale**:
- Specification requires <500ms telemetry update latency
- WebSocket provides low-latency bidirectional communication
- FastAPI has excellent WebSocket support with automatic message management
- Avoids polling overhead which would impact latency requirement
- Browser APIs have native WebSocket support (ws/wss)

**Alternatives Considered**:
- REST polling: Cannot meet 500ms latency requirement reliably
- gRPC: Adds complexity, less suitable for browser clients
- Server-Sent Events (SSE): One-directional only, but combined with REST for commands could work

**Implementation**:
- FastAPI WebSocket endpoint at `/ws/telemetry`
- Frontend React hook (useWebSocket) manages connection lifecycle
- Automatic reconnection logic with exponential backoff
- Message compression for bandwidth efficiency (if needed)

---

## 4. State Management

### Decision: React Context API + Custom Hooks

**Rationale**:
- Application state is localized (single robot setup per user, single session)
- No complex cross-component state synchronization required beyond WebSocket telemetry
- Context API + hooks are sufficient for application of this scale
- Avoids Redux complexity and additional dependencies

**Alternatives Considered**:
- Redux: Overkill for single-user, session-based application
- Zustand: Lightweight alternative, but Context API is sufficient
- TanStack Query: Useful for server state, but WebSocket handles real-time updates

**Implementation**:
- MotorContext: Stores motor configuration, current state, error conditions
- TelemetryContext: Stores real-time telemetry data from all 12 motors
- useMotorConfiguration hook: Handles configuration CRUD operations
- Custom middleware for persistence (localStorage + backend sync)

---

## 5. Backend Framework & Serial Communication

### Decision: FastAPI + Python 3.10+ + pyserial

**Rationale**:
- User specified FastAPI + Python backend
- FastAPI provides:
  - Async I/O support (essential for serial port polling + WebSocket)
  - Built-in WebSocket support
  - Excellent Pydantic validation for request/response schemas
  - Auto-generated OpenAPI documentation
- pyserial: Standard library for serial port communication in Python, well-maintained
- Python ecosystem strong for robotics (NumPy, scipy, etc.)

**Alternatives Considered**:
- Django REST Framework: Heavier, less suitable for async real-time communication
- Node.js backend: Would require learning curve, Python/FastAPI already good fit

**Serial Port Discovery**:
- Use pyserial's `serial.tools.list_ports` for platform-independent port enumeration
- Test connectivity via simple command echo (motor controller responds with ACK)
- Store port labels in SQLite for persistence

---

## 6. Database & Persistence

### Decision: SQLite with SQLAlchemy ORM

**Rationale**:
- SQLite provides file-based, zero-configuration database
- Good for single-user desktop application (not multi-user SaaS)
- SQLAlchemy provides ORM abstraction layer
- Easy to backup/migrate configuration files
- Supports atomic transactions for configuration safety

**Stored Data**:
1. Motor Configuration (12 motors × parameters)
2. Port Labels (port name → user-friendly label mapping)
3. Operation Logs (timestamp, motor ID, operation type, status, error details)
4. Telemetry History (optional, sampled for performance)

**Alternatives Considered**:
- PostgreSQL: Overkill for single-user application
- MongoDB: Not ideal for structured relational data
- JSON files: Less queryable, no transaction support

---

## 7. Internationalization (i18n)

### Decision: i18next + React integration

**Rationale**:
- User requested English + Korean content
- i18next is industry-standard for React i18n
- Supports:
  - JSON-based translation files (easy to manage and version)
  - Namespace organization (e.g., en/setup.json, en/dashboard.json)
  - Right-to-left language support (preparation for future requirements)
  - Dynamic language switching without page reload
- React i18next hook provides easy integration with functional components

**Implementation**:
```
i18n/
├── en/
│   ├── setup.json         # "Port Discovery", "Test Motor", etc.
│   ├── configuration.json # "Configure Motors", "Motor ID", etc.
│   ├── dashboard.json     # "Telemetry", "Status", "Alerts", etc.
│   ├── calibration.json
│   └── common.json        # "Save", "Cancel", "Error", etc.
└── ko/
    ├── setup.json
    ├── configuration.json
    └── ...
```

**Alternatives Considered**:
- gettext (GNU i18n): More verbose, better for compiled languages
- Intl API (browser native): Limited feature set

---

## 8. Layout Architecture (Matching Hugging Face Reference)

### Decision: CSS Grid + Flexbox with shadcn-ui components

**Layout Structure**:
```
┌─────────────────────────────────────────┐
│           Header (Logo, Title)          │
├────────────┬──────────────────────────────┐
│  Sidebar   │                              │
│  (Menu)    │     Main Content Area        │
│            │                              │
│  - Setup   │  (Page content changes       │
│  - Cal     │   based on selected menu)    │
│  - Robot   │                              │
│  - Learn   │                              │
└────────────┴──────────────────────────────┘
```

**CSS Implementation**:
- Main container: CSS Grid with 2 columns (sidebar + content)
- Sidebar: Fixed width (200-250px), dark background
- Header: Full width, spans both columns, sticky positioning
- Content area: Flexible, scrollable
- Dark theme colors matching Hugging Face (dark blue/gray backgrounds, light text)

**Responsive Design**:
- Tablet (768px): Sidebar collapses into hamburger menu
- Mobile: Full-width stacked layout (if needed in future)
- Current focus: Desktop/laptop browsing (robotics development environment)

---

## 9. Component Library & UI Components

### Decision: shadcn-ui + custom components

**Core Components Needed**:
1. **Layout Components**:
   - Header with logo, title, language switcher
   - Sidebar with navigation menu
   - MainLayout wrapper

2. **Port Discovery Components**:
   - PortCard (shows port name, device ID, test button, label input)
   - PortDiscoveryPanel (12-grid layout of ports)
   - PortTestButton with loading state

3. **Configuration Components**:
   - MotorConfigWizard (form for 12 motors)
   - MotorInputForm (ID, port, type, torque limits)
   - ValidationErrorDisplay

4. **Dashboard Components**:
   - MotorTelemetryCard (position, velocity, torque, temp for single motor)
   - TelemetryGrid (12 cards in responsive grid)
   - StatusIndicator (color-coded health status)
   - AlertBanner (error/warning alerts)
   - HistoricalChart (optional, for P3 feature)

5. **Shared Components**:
   - LoadingSpinner
   - LanguageSwitcher (English/Korean toggle)
   - ErrorModal
   - SuccessNotification

---

## 10. API Contract & WebSocket Protocol

### Backend API Endpoints (REST)

```
GET  /api/ports                    # List detected serial ports
POST /api/ports/test               # Test connectivity to a port
POST /api/ports/{port}/label       # Save port label

GET  /api/motors/config            # Get current configuration
POST /api/motors/config            # Save motor configuration
GET  /api/motors/config/validate   # Validate configuration before saving

POST /api/motors/{id}/test         # Send test command to motor
POST /api/motors/emergency-stop    # Emergency stop all motors

GET  /api/logs                     # Get operation logs (filtered)
GET  /api/logs/{motor_id}          # Get logs for specific motor
```

### WebSocket Protocol

**Connection**: `ws://localhost:8000/ws/telemetry`

**Message Format**:
```json
{
  "timestamp": "2025-11-09T12:34:56Z",
  "motors": [
    {
      "motor_id": 1,
      "position": 45.5,
      "velocity": 23.1,
      "torque": 12.3,
      "temperature": 38.5,
      "status": "healthy",  // healthy | warning | error
      "error": null         // null or error message
    },
    ...
  ]
}
```

---

## 11. Error Handling & Resilience

### Decision: Graceful degradation with user feedback

**Port Disconnection**:
- Backend continuously monitors port availability
- WebSocket message includes per-motor status
- Frontend displays "Disconnected" badge on affected motor
- Prevent command queueing to disconnected ports

**Backend API Errors**:
- Frontend shows toast notification with error message
- Retry logic with exponential backoff (max 3 attempts)
- Queue commands for retry when connection restores

**WebSocket Failures**:
- Auto-reconnect with exponential backoff
- Show connection status indicator in header
- Buffer telemetry updates during outage (local state)
- Sync on reconnection

---

## 12. Testing Strategy

### Frontend Testing (Vitest + React Testing Library)

**Unit Tests**:
- Component rendering tests (hooks, props)
- Utility function tests (i18n, formatting)
- State management tests (Context)

**Integration Tests**:
- Multi-component workflows (Setup → Configuration → Dashboard)
- API mock testing
- WebSocket message handling

**E2E Tests** (Playwright - Phase 3):
- User journey from port discovery to motor testing
- Configuration persistence
- Real-time telemetry display

### Backend Testing (pytest)

**Unit Tests**:
- Serial port discovery mock tests
- Data model validation
- Business logic (configuration validation, etc.)

**Integration Tests**:
- API endpoint tests (FastAPI TestClient)
- Database persistence
- WebSocket message broadcast

---

## 13. Performance Optimization

### Telemetry Update Latency (<500ms requirement)

**Frontend**:
- React.memo for MotorTelemetryCard (prevent unnecessary re-renders)
- useCallback for event handlers
- Virtualization if log list becomes large (P3 feature)

**Backend**:
- Async serial port polling (non-blocking I/O)
- WebSocket broadcast without blocking
- Efficient message serialization (JSON compression if needed)

**Network**:
- Keep WebSocket connection open (avoid reconnect overhead)
- Message batching if multiple motor updates arrive within 10ms

### UI Responsiveness

- Lazy load telemetry charts (only render when visible)
- Debounce configuration form inputs
- Cancel in-flight requests when component unmounts

---

## 14. LeRobot Framework Integration

### Decision: Abstract motor control via service layer

**Rationale**:
- LeRobot provides motor control SDK, but we need USB MotorBus level control
- Create service layer (lerobot_bridge.py) that:
  - Wraps LeRobot motor abstractions
  - Provides our custom commands (discover, test, configure)
  - Abstracts away LeRobot implementation details
  - Allows future migration if needed

**Implementation**:
```python
# motorbot-backend/app/services/lerobot_bridge.py
class LeRobotBridge:
    def discover_motors(self) -> List[MotorConfig]:
        """Discover connected motors"""

    def configure_motor(self, motor_id: int, config: MotorConfig) -> bool:
        """Apply configuration to motor"""

    def send_test_command(self, motor_id: int, command: MotorCommand) -> MotorResponse:
        """Send test command and get immediate response"""

    def get_telemetry(self, motor_id: int) -> TelemetryData:
        """Get current motor telemetry"""
```

---

## 15. Security Considerations

### Current Scope (Non-multi-user)

- No authentication required (single-user desktop application)
- CORS not needed (single origin)
- No sensitive data (motor configs are not security-critical)

### Future Considerations

- Input validation on all API endpoints (Pydantic schemas handle this)
- Rate limiting on commands (prevent spam/abuse)
- Secure storage of port labels/configurations (already file-based)

---

## Summary of Key Decisions

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| Frontend | React 18 + Vite + shadcn-ui | User requested, modern, responsive |
| Backend | FastAPI + Python 3.10+ | User requested, excellent async support |
| Real-time | WebSocket | Meets <500ms latency requirement |
| Database | SQLite + SQLAlchemy | Simple, no-config, suitable for single-user |
| Styling | Tailwind CSS + shadcn-ui | User requested, matches reference design |
| i18n | i18next | Standard React practice, English + Korean |
| Layout | CSS Grid + Flexbox | Responsive, matches Hugging Face reference |
| Serial Comms | pyserial | Standard Python library, well-maintained |
| State Mgmt | React Context API | Sufficient for application scope |

---

## Next Steps (Phase 1: Design)

1. Generate `data-model.md` with entity definitions
2. Create OpenAPI contract in `contracts/`
3. Generate `quickstart.md` with development setup
4. Create detailed component specifications
5. Update agent context with technology decisions
