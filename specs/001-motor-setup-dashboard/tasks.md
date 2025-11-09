# Implementation Tasks: Motor Setup and Monitoring Dashboard

**Feature**: Motor Setup and Monitoring Dashboard (001-motor-setup-dashboard)
**Branch**: `001-motor-setup-dashboard`
**Created**: 2025-11-09
**Tech Stack**: React 18 + TypeScript + shadcn-ui (Frontend), FastAPI + Python 3.10+ (Backend)
**Total Tasks**: 87 (organized by 5 user stories + setup + foundational + polish phases)

---

## Implementation Strategy

**MVP Scope** (Recommended for Phase 1 release): User Stories 1, 2, 3
- Complete port discovery and testing (US1)
- Complete motor configuration wizard (US2)
- Complete real-time monitoring dashboard (US3)
- **Value**: Users can assemble, configure, and monitor 12-motor system
- **Estimated Effort**: 2 weeks (10 days development)

**Phase 2 Scope**: User Stories 4, 5
- Motor testing interface (US4)
- Historical logging and analytics (US5)
- **Estimated Effort**: 1 week (5 days development)

**Parallel Development Opportunities**:
- Frontend and backend development can proceed in parallel (API contracts defined)
- Frontend pages can be developed independently (Setup, Configuration, Dashboard, etc.)
- Backend services can be developed independently (Port discovery, Motor control, Telemetry)

---

## Dependencies & Execution Order

**Sequential Must-Complete Before User Stories**:
1. Phase 1: Setup (project structure, dependencies)
2. Phase 2: Foundational (database, core services, API contracts)

**User Story Dependencies** (can be executed in parallel within each story):
- **US1 (Port Discovery)**: Independent, no dependencies
- **US2 (Motor Configuration)**: Depends on US1 (ports must be discovered first)
- **US3 (Real-Time Dashboard)**: Depends on US2 (motors must be configured first)
- **US4 (Motor Testing)**: Depends on US3 (can test motors from dashboard)
- **US5 (Historical Logs)**: Independent from US1-US4 (can be developed in parallel)

**Recommended Execution**:
```
Phase 1 (Setup)
  ↓
Phase 2 (Foundational - Database, Core Services)
  ↓
Phase 3 (US1 - Port Discovery) [1-2 days]
  ↓
Phase 4 (US2 - Motor Configuration) [2-3 days]
  ↓
Phase 5 (US3 - Real-Time Dashboard) [3-4 days]  OR  Phase 5b (US5 - Historical Logs) [2-3 days in parallel]
  ↓
Phase 6 (US4 - Motor Testing) [2-3 days]
  ↓
Phase 7 (US5 - Historical Logs) [if not done in parallel]
  ↓
Phase 8 (Polish & Cross-Cutting)
```

---

## Phase 1: Project Setup & Initialization

### Frontend Project Structure

- [ ] T001 Initialize frontend project with React 18, TypeScript, Vite: `mkdir motorbot-frontend && cd motorbot-frontend && npm create vite@latest . -- --template react-ts`
- [ ] T002 Install core frontend dependencies: `npm install react@18 react-dom@18 react-router-dom@6 typescript @types/react @types/react-dom`
- [ ] T003 Install shadcn-ui and dependencies: `npm install -D tailwindcss postcss autoprefixer && npx shadcn-ui@latest init && npm install @radix-ui/react-*`
- [ ] T004 Install state management and utilities: `npm install zustand@4 axios use-context-selector`
- [ ] T005 Install i18n library: `npm install i18next react-i18next`
- [ ] T006 Install dev dependencies (testing, linting): `npm install -D vitest @testing-library/react @testing-library/jest-dom eslint prettier @typescript-eslint/eslint-plugin`
- [ ] T007 Configure TypeScript paths alias for imports: Edit `tsconfig.json` with `"@/*": ["./src/*"]`
- [ ] T008 Setup Tailwind CSS configuration: Configure `tailwind.config.ts` with dark mode and shadcn-ui theme
- [ ] T009 Create core directory structure in `motorbot-frontend/src/`: components/, pages/, services/, hooks/, types/, i18n/
- [ ] T010 Initialize git repository and .gitignore: `git init && echo "node_modules/\n.env\nbuild/" > .gitignore`

### Backend Project Structure

- [ ] T011 Initialize backend project: `mkdir motorbot-backend && cd motorbot-backend && python3.10 -m venv venv && source venv/bin/activate`
- [ ] T012 Create project structure: Create `app/`, `tests/`, `motorbot-backend/` directories with `__init__.py` files
- [ ] T013 Create requirements.txt with core dependencies: `fastapi>=0.100,uvicorn>=0.23,sqlalchemy>=2.0,pydantic>=2.0,pyserial>=3.5,python-multipart>=0.0.6`
- [ ] T014 Create development requirements: Add `pytest>=7.0,pytest-asyncio>=0.21,httpx>=0.24` to requirements.txt
- [ ] T015 Install Python dependencies: `pip install -r requirements.txt`
- [ ] T016 Create FastAPI app initialization: `motorbot-backend/app/main.py` with basic FastAPI app setup
- [ ] T017 Setup environment configuration: Create `.env` file with DATABASE_URL, DEBUG, PORT, CORS_ORIGINS settings
- [ ] T018 Create database initialization script: `motorbot-backend/app/database/db.py` with SQLAlchemy session management
- [ ] T019 Create directory structure for models, services, routes: `app/models/`, `app/services/`, `app/api/routes/`, `app/database/`
- [ ] T020 Initialize git repository: `git init && echo "venv/\n__pycache__/\n*.pyc\n.env\n*.db" > .gitignore`

### Documentation & Configuration

- [ ] T021 Create docker-compose.yml for local development: Services for frontend (port 5173), backend (port 8000), optional PostgreSQL
- [ ] T022 Create .env.example files for both frontend and backend with all required variables
- [ ] T023 Create DEVELOPMENT.md with setup instructions for new developers
- [ ] T024 Create API documentation index linking to contracts/api.openapi.yaml
- [ ] T025 Setup CI/CD placeholder (GitHub Actions workflow file)

---

## Phase 2: Foundational Infrastructure & Core Services

### Database & ORM Setup

- [ ] T026 Create SQLAlchemy database models: `motorbot-backend/app/database/models.py` with Port, Motor, MotorConfiguration, TelemetryDataPoint, OperationLog tables
- [ ] T027 Create Pydantic schemas for validation: `motorbot-backend/app/database/schemas.py` with request/response models
- [ ] T028 Implement database initialization function: `motorbot-backend/app/database/db.py` with `init_db()` and session management
- [ ] T029 Create database migration setup (Alembic): `alembic init alembic && setup migration templates`
- [ ] T030 Create initial migration: `alembic revision --autogenerate -m "Initial schema"`
- [ ] T031 Implement database connection pooling and error handling in `motorbot-backend/app/config.py`

### Core Backend Services

- [ ] T032 Implement Port Discovery service: `motorbot-backend/app/services/port_discovery.py` with `list_ports()`, `test_port()`, `save_port_label()`
- [ ] T033 Implement Motor Controller service: `motorbot-backend/app/services/motor_controller.py` with motor initialization and command sending
- [ ] T034 Implement Telemetry Collector service: `motorbot-backend/app/services/telemetry_collector.py` with real-time data collection from motors
- [ ] T035 Implement Configuration Manager service: `motorbot-backend/app/services/configuration_manager.py` with save, load, validate operations
- [ ] T036 Implement LeRobot Bridge service: `motorbot-backend/app/services/lerobot_bridge.py` abstracting LeRobot API calls
- [ ] T037 Implement Operation Logger service: `motorbot-backend/app/services/operation_logger.py` for recording operations and errors
- [ ] T038 Implement error handling middleware: Create `motorbot-backend/app/middleware/error_handler.py` for consistent error responses

### Frontend Core Infrastructure

- [ ] T039 Create API client service: `motorbot-frontend/src/services/api.ts` with axios instance and helper methods
- [ ] T040 Create WebSocket service: `motorbot-frontend/src/services/websocket.ts` with connection management and reconnection logic
- [ ] T041 Create i18n configuration: `motorbot-frontend/src/i18n/index.ts` with English and Korean translation support
- [ ] T042 Create translation files: `motorbot-frontend/src/i18n/en.json` and `ko.json` with all UI strings
- [ ] T043 Create TypeScript type definitions: `motorbot-frontend/src/types/motor.ts`, `port.ts`, `telemetry.ts`, `api.ts`
- [ ] T044 Create state management context: `motorbot-frontend/src/context/MotorContext.tsx` for motor configuration state
- [ ] T045 Create telemetry context: `motorbot-frontend/src/context/TelemetryContext.tsx` for real-time motor data
- [ ] T046 Create custom hooks: `motorbot-frontend/src/hooks/useMotorData.ts`, `useWebSocket.ts`, `useConfiguration.ts`
- [ ] T047 Create Layout components: `motorbot-frontend/src/components/Layout/Header.tsx`, `Sidebar.tsx`, `MainLayout.tsx`
- [ ] T048 Create Common components: `motorbot-frontend/src/components/Common/LoadingSpinner.tsx`, `StatusIndicator.tsx`, `LanguageSwitcher.tsx`, `ErrorModal.tsx`

### API Routes & WebSocket Setup

- [ ] T049 Create health check endpoint: `motorbot-backend/app/api/routes/health.py` with GET /api/health
- [ ] T050 Create port discovery routes: `motorbot-backend/app/api/routes/ports.py` with GET /api/ports, POST /api/ports/{id}/test, POST /api/ports/{id}/label
- [ ] T051 Create motor configuration routes: `motorbot-backend/app/api/routes/motors.py` with GET/POST /api/motors/config, POST /api/motors/{id}/test, POST /api/motors/emergency-stop
- [ ] T052 Create logging routes: `motorbot-backend/app/api/routes/logs.py` with GET /api/logs, GET /api/logs/{motor_id}
- [ ] T053 Implement WebSocket handler: `motorbot-backend/app/api/websocket.py` with /ws/telemetry endpoint for telemetry streaming
- [ ] T054 Create telemetry routes: `motorbot-backend/app/api/routes/telemetry.py` for HTTP telemetry endpoints (fallback)
- [ ] T055 Register all routes in FastAPI app: Update `motorbot-backend/app/main.py` with all route includes
- [ ] T056 Setup CORS and middleware: Configure CORS, request logging, error handling in `motorbot-backend/app/main.py`
- [ ] T057 Create OpenAPI documentation: Auto-generated Swagger UI at /docs and ReDoc at /redoc
- [ ] T058 Implement request/response validation with Pydantic

### Testing Infrastructure Setup

- [ ] T059 Create test configuration: `motorbot-backend/tests/conftest.py` with pytest fixtures for database and API client
- [ ] T060 Create test database session setup: In-memory SQLite for testing
- [ ] T061 Create frontend test configuration: `motorbot-frontend/vitest.config.ts` with testing library setup
- [ ] T062 Create mock services: `motorbot-frontend/tests/mocks/api.ts`, `websocket.ts` for testing without backend

---

## Phase 3: User Story 1 - Discover and Identify Motor Ports

**Goal**: Enable users to discover USB ports and test connectivity
**Independent Test**: User can open port discovery UI, see all connected ports, test each port, and label them
**Acceptance Criteria**: All discovered ports displayed within 30 seconds, port testing returns success/failure within 2 seconds

### Backend Implementation (US1)

- [ ] T063 Implement port enumeration logic: `motorbot-backend/app/services/port_discovery.py` - `enumerate_ports()` function using pyserial
- [ ] T064 Implement port testing logic: `motorbot-backend/app/services/port_discovery.py` - `test_port_connectivity()` with timeout handling
- [ ] T065 Implement port label persistence: `motorbot-backend/app/services/port_discovery.py` - `save_port_label()` and `get_labeled_ports()`
- [ ] T066 Create Port database operations: In `motorbot-backend/app/database/models.py` - CRUD operations for Port entity
- [ ] T067 [P] Implement GET /api/ports endpoint: Returns list of discovered ports with labels
- [ ] T068 [P] Implement POST /api/ports/{port_id}/test endpoint: Tests port and returns status
- [ ] T069 [P] Implement POST /api/ports/{port_id}/label endpoint: Saves user-friendly port label
- [ ] T070 Create unit tests for port discovery: `motorbot-backend/tests/unit/test_port_discovery.py`
- [ ] T071 [P] Create integration tests for port endpoints: `motorbot-backend/tests/integration/test_port_endpoints.py`

### Frontend Implementation (US1)

- [ ] T072 Create Port types and interfaces: `motorbot-frontend/src/types/port.ts` with Port, TestPortResponse interfaces
- [ ] T073 Create API client methods for ports: `motorbot-frontend/src/services/api.ts` - `listPorts()`, `testPort()`, `labelPort()`
- [ ] T074 [P] Create PortCard component: `motorbot-frontend/src/components/MotorSetup/PortCard.tsx` displaying port info with test button
- [ ] T075 [P] Create PortTestButton component: `motorbot-frontend/src/components/MotorSetup/PortTestButton.tsx` with loading and status states
- [ ] T076 [P] Create PortDiscovery page: `motorbot-frontend/src/pages/SetupMotorBus.tsx` with grid of PortCards
- [ ] T077 Create usePortDiscovery hook: `motorbot-frontend/src/hooks/usePortDiscovery.ts` managing port data fetching and caching
- [ ] T078 Create unit tests for Port components: `motorbot-frontend/tests/unit/components/PortCard.test.tsx`
- [ ] T079 [P] Create integration tests for port discovery page: `motorbot-frontend/tests/integration/SetupMotorBus.test.tsx`
- [ ] T080 Add port discovery translations: Update `motorbot-frontend/src/i18n/en.json` and `ko.json` with port-related strings

**Independent Validation**: User opens `/` (SetupMotorBus page), sees list of available USB ports, can test connectivity, can save labels, and configuration persists

---

## Phase 4: User Story 2 - Configure and Map 12 Motors to Ports

**Goal**: Enable users to configure all 12 motors and assign them to discovered ports
**Independent Test**: User can fill out 12-motor configuration form, receive validation feedback, save valid configuration, and load it on restart
**Acceptance Criteria**: Configuration wizard guides through 12 motors, validation prevents incomplete saves, configuration persists across restarts

### Backend Implementation (US2)

- [ ] T081 Implement configuration validation logic: `motorbot-backend/app/services/configuration_manager.py` - validate all 12 motors, check port uniqueness
- [ ] T082 Implement configuration save/load: `motorbot-backend/app/services/configuration_manager.py` - persist and retrieve from database
- [ ] T083 Create Motor database operations: In `motorbot-backend/app/database/models.py` - CRUD for Motor entity
- [ ] T084 Create MotorConfiguration database operations: CRUD for system-wide configuration
- [ ] T085 [P] Implement GET /api/motors/config endpoint: Returns current 12-motor configuration
- [ ] T086 [P] Implement POST /api/motors/config endpoint: Saves and validates new configuration
- [ ] T087 Create configuration validation tests: `motorbot-backend/tests/unit/test_configuration_validation.py`
- [ ] T088 [P] Create integration tests for configuration endpoints: `motorbot-backend/tests/integration/test_configuration_endpoints.py`

### Frontend Implementation (US2)

- [ ] T089 Create Motor types and interfaces: `motorbot-frontend/src/types/motor.ts` with Motor, MotorConfiguration interfaces
- [ ] T090 Create configuration API methods: `motorbot-frontend/src/services/api.ts` - `getConfig()`, `saveConfig()`
- [ ] T091 [P] Create MotorForm component: `motorbot-frontend/src/components/MotorConfiguration/MotorForm.tsx` for single motor input (ID, port, type, limits)
- [ ] T092 [P] Create ConfigurationWizard page: `motorbot-frontend/src/pages/ConfigurationWizard.tsx` with 12 MotorForm instances
- [ ] T093 [P] Create ConfigurationSummary component: `motorbot-frontend/src/components/MotorConfiguration/ConfigurationSummary.tsx` displaying validation results
- [ ] T094 Create useConfiguration hook: `motorbot-frontend/src/hooks/useConfiguration.ts` managing form state and submission
- [ ] T095 Create unit tests for Motor components: `motorbot-frontend/tests/unit/components/MotorForm.test.tsx`
- [ ] T096 [P] Create integration tests for configuration wizard: `motorbot-frontend/tests/integration/ConfigurationWizard.test.tsx`
- [ ] T097 Add configuration translations: Update i18n files with configuration-related strings
- [ ] T098 Create validation error display component: `motorbot-frontend/src/components/Common/ValidationErrorDisplay.tsx`
- [ ] T099 Implement local storage persistence: Save configuration draft to localStorage while editing

**Independent Validation**: User navigates to Calibration page (or configuration page), fills 12-motor config with valid ports and parameters, sees validation errors on incomplete fields, successfully saves, application persists and reloads config on restart

---

## Phase 5: User Story 3 - Monitor Motor Status and Output in Real-Time

**Goal**: Display real-time telemetry from all 12 motors on a live dashboard
**Independent Test**: User can view dashboard with live telemetry updates for all motors, see color-coded status, receive alerts for errors within 500ms latency
**Acceptance Criteria**: All 12 motors displayed with position/velocity/torque/temperature, updates within 500ms, color-coded health status, alerts for error conditions

### Backend Implementation (US3)

- [ ] T100 Implement telemetry collection loop: `motorbot-backend/app/services/telemetry_collector.py` - continuously poll motors at 50-100Hz
- [ ] T101 Implement telemetry storage: Save telemetry snapshots to database for historical access
- [ ] T102 Implement error detection: Identify overheat, position limits, torque limits, unresponsive motors
- [ ] T103 [P] Implement WebSocket telemetry streaming: `motorbot-backend/app/api/websocket.py` - broadcast telemetry at 20Hz to connected clients
- [ ] T104 [P] Implement telemetry message format: Structure messages with motor data, status, errors per data model
- [ ] T105 Implement connection lifecycle: Handle WebSocket connect/disconnect, cleanup, status messages
- [ ] T106 Implement reconnection handling: Auto-resend configuration on reconnect, resume telemetry stream
- [ ] T107 [P] Create integration tests for WebSocket telemetry: `motorbot-backend/tests/integration/test_websocket_telemetry.py`
- [ ] T108 Create telemetry unit tests: `motorbot-backend/tests/unit/test_telemetry_collector.py`

### Frontend Implementation (US3)

- [ ] T109 Create TelemetryDataPoint type: `motorbot-frontend/src/types/telemetry.ts`
- [ ] T110 Implement WebSocket connection hook: `motorbot-frontend/src/hooks/useWebSocket.ts` with auto-reconnect logic
- [ ] T111 [P] Create MotorTelemetryCard component: `motorbot-frontend/src/components/Dashboard/MotorTelemetryCard.tsx` displaying single motor metrics
- [ ] T112 [P] Create status color mapping utility: Helper function mapping motor status to Tailwind colors (green/yellow/red)
- [ ] T113 [P] Create StatusIndicator component: Visual badge showing motor health status with color coding
- [ ] T114 [P] Create TelemetryDisplay component: `motorbot-frontend/src/components/Dashboard/TelemetryDisplay.tsx` grid of all 12 motor cards
- [ ] T115 [P] Create AlertPanel component: `motorbot-frontend/src/components/Dashboard/AlertPanel.tsx` showing error alerts for affected motors
- [ ] T116 [P] Create LeRobotDashboard page: `motorbot-frontend/src/pages/LeRobotDashboard.tsx` main monitoring interface
- [ ] T117 Create useTelemetry hook: `motorbot-frontend/src/hooks/useTelemetry.ts` managing telemetry state updates
- [ ] T118 Implement telemetry update debouncing: Prevent excessive re-renders while maintaining <500ms latency perception
- [ ] T119 Create unit tests for TelemetryCard: `motorbot-frontend/tests/unit/components/MotorTelemetryCard.test.tsx`
- [ ] T120 [P] Create integration tests for Dashboard: `motorbot-frontend/tests/integration/LeRobotDashboard.test.tsx`
- [ ] T121 Add dashboard translations: Update i18n with telemetry and alert strings
- [ ] T122 Implement responsive grid for 12 motors: Ensure layout works on different screen sizes

**Independent Validation**: User navigates to LeRobotDashboard page, WebSocket connects and streams telemetry, all 12 motors displayed with live data, status colors reflect health, error alerts appear for problematic motors within latency budget

---

## Phase 6: User Story 4 - Test Individual Motors Through UI Commands

**Goal**: Enable users to send test commands to motors from the dashboard
**Independent Test**: User can select motor, send test command, observe motor response, see updated telemetry
**Acceptance Criteria**: Test commands (position move, stop) execute within 2 seconds, motor response reflected in telemetry, command status shown to user

### Backend Implementation (US4)

- [ ] T123 Implement motor test command handler: `motorbot-backend/app/services/motor_controller.py` - execute position move, velocity change, emergency stop
- [ ] T124 Implement command validation: Validate target positions within motor limits, velocity within max
- [ ] T125 [P] Implement POST /api/motors/{motor_id}/test endpoint: Send test command and return execution status
- [ ] T126 [P] Implement POST /api/motors/emergency-stop endpoint: Send stop command to all motors immediately
- [ ] T127 Create MotorTestEvent recording: Log all test commands with results to database
- [ ] T128 Implement command timeout handling: Abort commands that don't complete within timeout
- [ ] T129 Create unit tests for motor commands: `motorbot-backend/tests/unit/test_motor_commands.py`
- [ ] T130 [P] Create integration tests for motor endpoints: `motorbot-backend/tests/integration/test_motor_endpoints.py`

### Frontend Implementation (US4)

- [ ] T131 Create MotorTestCommand type: `motorbot-frontend/src/types/motor.ts`
- [ ] T132 Create motor test API methods: `motorbot-frontend/src/services/api.ts` - `sendTestCommand()`, `emergencyStop()`
- [ ] T133 [P] Create MotorTestPanel component: `motorbot-frontend/src/components/Dashboard/MotorTestPanel.tsx` with command controls
- [ ] T134 [P] Create PositionTestInput component: Input for target position with validation against motor limits
- [ ] T135 [P] Create StopMotorButton component: Emergency stop button with confirmation
- [ ] T136 [P] Create TestCommandStatus component: Shows command execution progress and result
- [ ] T137 Implement motor test command submission: Hook calling API endpoint and updating dashboard
- [ ] T138 Create unit tests for TestPanel components: `motorbot-frontend/tests/unit/components/MotorTestPanel.test.tsx`
- [ ] T139 [P] Create integration tests for motor testing: `motorbot-frontend/tests/integration/MotorTesting.test.tsx`
- [ ] T140 Add motor testing translations: Update i18n with test command strings
- [ ] T141 Implement command confirmation dialog: User confirms before sending commands to motors

**Independent Validation**: User clicks on motor card in dashboard, sees test controls, sends position move command, motor moves and telemetry updates, sees command success/failure status

---

## Phase 7: User Story 5 - View Historical Motor Data and Performance Logs

**Goal**: Enable users to review historical telemetry and error logs
**Independent Test**: User can access logs page, filter by date/motor/severity, view detailed log entries
**Acceptance Criteria**: Logs displayed with timestamps, filtering works correctly, detailed context shown for each entry

### Backend Implementation (US5)

- [ ] T142 Implement log retrieval service: `motorbot-backend/app/services/operation_logger.py` - query logs with filters
- [ ] T143 Implement log filtering: By motor_id, date range, severity, operation type
- [ ] T144 Implement log pagination: Support limit/offset for large result sets
- [ ] T145 Implement telemetry history sampling: Store every Nth reading to database (avoid storage bloat)
- [ ] T146 [P] Implement GET /api/logs endpoint: Returns filtered operation logs with pagination
- [ ] T147 [P] Implement GET /api/logs/{motor_id} endpoint: Returns logs specific to one motor
- [ ] T148 Create log retention policy: Archive logs older than 30 days (optional)
- [ ] T149 Create unit tests for logging: `motorbot-backend/tests/unit/test_operation_logger.py`
- [ ] T150 [P] Create integration tests for log endpoints: `motorbot-backend/tests/integration/test_log_endpoints.py`

### Frontend Implementation (US5)

- [ ] T151 Create OperationLog type: `motorbot-frontend/src/types/telemetry.ts`
- [ ] T152 Create log API methods: `motorbot-frontend/src/services/api.ts` - `getLogs()`, `getMotorLogs()`
- [ ] T153 [P] Create LogTable component: `motorbot-frontend/src/components/Dashboard/LogTable.tsx` displaying logs in table format
- [ ] T154 [P] Create LogFilterBar component: Date range, motor selector, severity filter controls
- [ ] T155 [P] Create LogDetailModal component: Shows full context for selected log entry
- [ ] T156 [P] Create HistoricalLogsPage component: `motorbot-frontend/src/pages/HistoricalLogs.tsx` main logs interface
- [ ] T157 Implement log filtering state management: Track selected filters and apply to queries
- [ ] T158 Implement log pagination UI: Load more / pagination controls
- [ ] T159 Create unit tests for Log components: `motorbot-frontend/tests/unit/components/LogTable.test.tsx`
- [ ] T160 [P] Create integration tests for logs page: `motorbot-frontend/tests/integration/HistoricalLogs.test.tsx`
- [ ] T161 Add logs translations: Update i18n with log-related strings
- [ ] T162 Implement log export functionality: Export selected logs as CSV or JSON

**Independent Validation**: User navigates to logs page, sees historical entries, filters by date/motor/severity, clicks entry to see details, exports subset of logs

---

## Phase 8: Polish & Cross-Cutting Concerns

### Responsive Design & Layout Refinement

- [ ] T163 Implement responsive grid for port discovery: Works on tablet (768px breakpoint)
- [ ] T164 Implement responsive grid for motor cards: Adapts 12 motors to different screen sizes (3 cols → 2 cols → 1 col)
- [ ] T165 Implement responsive sidebar: Collapses to hamburger menu on mobile (optional for MVP)
- [ ] T166 Test layout on multiple screen sizes: 1920x1080, 1366x768, 768x1024 (tablet)
- [ ] T167 Implement dark mode refinement: Ensure all components use correct dark theme colors

### Error Handling & User Feedback

- [ ] T168 Implement API error boundary: Catch API errors and display user-friendly messages
- [ ] T169 Implement network error handling: Show UI when backend is unavailable
- [ ] T170 Implement port disconnection handling: Gracefully handle and alert user when port disconnects
- [ ] T171 Implement motor unresponsive handling: Mark motors as offline, prevent command queuing
- [ ] T172 Implement loading state indicators: Spinners and skeleton screens for async operations
- [ ] T173 Implement success notifications: Toast messages confirming actions (configuration saved, port tested, etc.)
- [ ] T174 Implement error notifications: Toast messages for failures with actionable advice

### Performance Optimization

- [ ] T175 Implement lazy loading for pages: Code-split configuration and logs pages
- [ ] T176 Implement telemetry message batching: Aggregate updates within 50ms window
- [ ] T177 Implement React.memo for TelemetryCard: Prevent unnecessary re-renders on data updates
- [ ] T178 Implement WebSocket message compression: gzip if payload exceeds threshold
- [ ] T179 Optimize database queries: Add indexes on frequently queried fields (motor_id, timestamp)
- [ ] T180 Profile frontend performance: Check Core Web Vitals (LCP, FID, CLS) with Lighthouse

### Documentation & Examples

- [ ] T181 Create component storybook stories: Document UI components with usage examples
- [ ] T182 Create API usage guide: Examples for common operations (port discovery, motor config, etc.)
- [ ] T183 Create troubleshooting guide: Common issues and solutions
- [ ] T184 Create deployment guide: Instructions for deploying frontend and backend
- [ ] T185 Create developer onboarding guide: How new developers get started

### Security Hardening

- [ ] T186 Implement input validation on all forms: Sanitize user inputs
- [ ] T187 Implement CORS properly: Only allow expected origins
- [ ] T188 Implement rate limiting on backend: Prevent API abuse (optional for single-user app)
- [ ] T189 Implement secure configuration: Use environment variables for sensitive data
- [ ] T190 Review data storage security: Ensure sensitive config is encrypted if applicable

### Testing Coverage

- [ ] T191 Achieve 80% code coverage for backend services: Run `pytest --cov=app`
- [ ] T192 Achieve 70% code coverage for frontend components: Run `npm run test:coverage`
- [ ] T193 Create E2E test for complete setup flow: Port discovery → Configuration → Dashboard monitoring
- [ ] T194 Create E2E test for motor testing flow: Configuration → Test motor → Verify response
- [ ] T195 Create E2E test for error handling: Simulate port disconnect, API errors, etc.

### Documentation in Code

- [ ] T196 Add JSDoc comments to all exported functions (frontend)
- [ ] T197 Add docstrings to all service classes (backend)
- [ ] T198 Add inline comments for complex logic
- [ ] T199 Create API endpoint documentation in comments
- [ ] T200 Create WebSocket message type documentation

### Final Validation & QA

- [ ] T201 Manual testing: Run complete user journey (Setup → Config → Monitor)
- [ ] T202 Manual testing: Test error scenarios (port disconnect, invalid config, etc.)
- [ ] T203 Performance testing: Verify <500ms telemetry latency under load
- [ ] T204 Performance testing: Verify port discovery completes in <30 seconds
- [ ] T205 Browser compatibility testing: Chrome, Firefox, Safari, Edge
- [ ] T206 Accessibility testing: WCAG 2.1 AA compliance check
- [ ] T207 Create release notes: Document features, known issues, migration guide
- [ ] T208 Create changelog: All commits and PRs summarized

---

## Task Summary by Phase

| Phase | Name | Tasks | Effort |
|-------|------|-------|--------|
| 1 | Setup | T001-T025 | ~1 day |
| 2 | Foundational | T026-T062 | ~2-3 days |
| 3 | US1: Port Discovery | T063-T080 | ~1-2 days |
| 4 | US2: Motor Configuration | T081-T099 | ~2-3 days |
| 5 | US3: Real-Time Monitoring | T100-T122 | ~3-4 days |
| 6 | US4: Motor Testing | T123-T141 | ~2-3 days |
| 7 | US5: Historical Logs | T142-T162 | ~2-3 days |
| 8 | Polish & QA | T163-T208 | ~3-4 days |

**Total Estimated Effort**: 17-25 days (for 2 developers in parallel, roughly 2.5-3.5 weeks)

---

## Parallelization Opportunities

### Frontend & Backend (Immediate)
- All frontend component development can proceed in parallel with backend services
- API contracts defined in OpenAPI schema serve as integration contract
- Mock backend in frontend tests enables development without backend

### Within Frontend
- Page development can proceed in parallel:
  - Developer A: Port Discovery page (T074-T080)
  - Developer B: Motor Configuration page (T089-T099)
  - Developer C: Dashboard page (T109-T122)

### Within Backend
- Service development can proceed in parallel:
  - Developer A: Port Discovery service (T063-T068)
  - Developer B: Configuration service (T081-T086)
  - Developer C: Telemetry service (T100-T106)

### Testing
- Unit tests can be written in parallel with features
- Integration tests can be created once APIs stabilize

---

## MVP Definition (Recommended Phase 1 Release)

**Scope**: User Stories 1, 2, 3 + Foundational + Setup
**Tasks**: T001-T025 (Setup) + T026-T062 (Foundational) + T063-T122 (US1-US3)
**Total**: ~60 tasks
**Estimated Time**: 10-14 days (2 developers)
**Value Delivered**:
- Complete port discovery and testing
- Complete motor configuration interface
- Live monitoring dashboard
- Users can assemble and configure 12-motor SO-ARM 101

**Future Releases**:
- Phase 2: Add motor testing (US4) and historical logs (US5)
- Phase 3: Add calibration assistance, advanced analytics

---

## Quality Gate Checkpoints

**Before Each Phase**:
1. All previous phase tasks marked complete
2. Tests written and passing
3. Code reviewed for quality
4. Documentation updated

**Before Release**:
1. All MVP tasks (T001-T122) complete and tested
2. >80% backend code coverage
3. >70% frontend code coverage
4. Manual E2E testing passed
5. Performance targets met (<500ms latency, <30s discovery)
6. Security review completed

---

## File Path Reference

### Frontend Key Files
```
motorbot-frontend/
├── src/
│   ├── components/Layout/*.tsx        → T047-T048
│   ├── components/MotorSetup/*.tsx    → T074-T075
│   ├── components/MotorConfiguration/ → T091-T093, T098
│   ├── components/Dashboard/*.tsx     → T111-T116
│   ├── components/Common/*.tsx        → T048, T173-T174
│   ├── pages/*.tsx                    → T076, T092, T116, T156
│   ├── services/api.ts                → T039
│   ├── services/websocket.ts          → T040
│   ├── services/i18n.ts               → T041
│   ├── hooks/*.ts                     → T046, T077, T094, T110, T117
│   ├── types/*.ts                     → T043, T071, T131, T151
│   ├── i18n/en.json, ko.json          → T042, T080, T097, T121, T140, T161
│   └── context/*.tsx                  → T044-T045
```

### Backend Key Files
```
motorbot-backend/
├── app/
│   ├── main.py                              → T016, T055-T056
│   ├── services/
│   │   ├── port_discovery.py                → T032, T063-T065
│   │   ├── motor_controller.py              → T033, T123-T124
│   │   ├── telemetry_collector.py           → T034, T100-T102
│   │   ├── configuration_manager.py         → T035, T081-T082
│   │   ├── lerobot_bridge.py                → T036
│   │   └── operation_logger.py              → T037, T142-T144
│   ├── api/
│   │   ├── routes/ports.py                  → T050, T067-T069
│   │   ├── routes/motors.py                 → T051, T085-T086, T125-T126
│   │   ├── routes/logs.py                   → T052, T146-T147
│   │   ├── routes/telemetry.py              → T054
│   │   ├── routes/health.py                 → T049
│   │   └── websocket.py                     → T053, T103-T106
│   ├── database/
│   │   ├── models.py                        → T026, T066, T083
│   │   ├── schemas.py                       → T027
│   │   └── db.py                            → T018, T028, T031
│   └── config.py                            → T017, T031
├── tests/
│   ├── unit/test_*.py                       → T070, T087, T108, T129, T149
│   └── integration/test_*.py                → T071, T088, T107, T130, T150
```

---

**Generated**: 2025-11-09
**Status**: Ready for implementation
**Next Step**: Begin Phase 1 (Setup)
