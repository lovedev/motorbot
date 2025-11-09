# Implementation Plan: Motor Setup and Monitoring Dashboard

**Branch**: `001-motor-setup-dashboard` | **Date**: 2025-11-09 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-motor-setup-dashboard/spec.md`

**Status**: Phase 0 (Research) → Phase 1 (Design) → Phase 2 (Tasks)

## Summary

Motor Setup and Monitoring Dashboard for SO-ARM 101 robot arm assembly. System enables roboticists to:
1. Discover and test USB serial ports connected to motor controllers
2. Configure all 12 motors with parameter mapping
3. Monitor real-time telemetry (position, velocity, torque, temperature) via responsive web dashboard
4. Send test commands and emergency stop controls
5. Maintain historical logs for debugging

Frontend: NestJS + TypeScript + shadcn-ui (responsive layout with sidebar navigation, header, content area matching Hugging Face design language)
Backend: FastAPI + Python (serial port management, motor control bridge to LeRobot, WebSocket real-time telemetry)
Integration: LeRobot framework for motor control abstraction

## Technical Context

**Frontend Language/Version**: TypeScript 5+, Node.js 18+
**Frontend Framework**: NestJS 10+ (for structured backend API), React 18+ (UI layer with shadcn-ui components)
**UI Component Library**: shadcn-ui (Radix UI + Tailwind CSS)
**Backend Language/Version**: Python 3.10+
**Backend Framework**: FastAPI 0.100+
**Serial Communication**: pyserial (for USB MotorBus discovery and commands)
**Real-Time Communication**: WebSocket (FastAPI + frontend)
**Storage**: SQLite (configuration persistence, operation logs)
**Testing**: Frontend - Vitest/Jest, Backend - pytest
**Target Platform**: Web (cross-platform desktop browsers on Linux/macOS)
**Project Type**: Full-stack web application (separate frontend NestJS + backend FastAPI services)
**Performance Goals**: Port discovery <30s, telemetry updates <500ms latency, support 4+ hours continuous monitoring
**Constraints**: <500ms telemetry latency, all 12 motors displayed simultaneously without UI lag
**Scale/Scope**: 12 motors, ~5 primary screens (Setup/Port Discovery, Motor Configuration, Dashboard, Calibration, Learning Center), i18n (English + Korean)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Note**: Constitution template not yet filled (using defaults). Key architectural principles:
- ✅ **Separation of Concerns**: Frontend (NestJS/React) and Backend (FastAPI) clearly separated
- ✅ **Technology Stack Alignment**: User-specified stack (shadcn-ui + NestJS frontend, FastAPI backend)
- ✅ **Real-Time Communication**: WebSocket for telemetry meets performance requirements
- ✅ **Data Persistence**: SQLite suitable for configuration and logs
- ✅ **i18n Support**: shadcn-ui and React support multilingual content (English + Korean)

**GATE STATUS**: ✅ PASS (no violations against default practices)

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

**Selected Structure**: Option 2 - Full-stack web application (frontend + backend)

```text
motorbot-frontend/                          # NestJS + React + shadcn-ui
├── src/
│   ├── components/
│   │   ├── Layout/
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── MainLayout.tsx
│   │   ├── MotorSetup/
│   │   │   ├── PortDiscovery.tsx
│   │   │   ├── PortTestButton.tsx
│   │   │   └── MotorPortCard.tsx
│   │   ├── MotorConfiguration/
│   │   │   ├── ConfigurationWizard.tsx
│   │   │   ├── MotorForm.tsx
│   │   │   └── ConfigurationSummary.tsx
│   │   ├── Dashboard/
│   │   │   ├── TelemetryDisplay.tsx
│   │   │   ├── MotorTelemetryCard.tsx
│   │   │   ├── AlertPanel.tsx
│   │   │   └── HistoricalCharts.tsx
│   │   ├── Common/
│   │   │   ├── LanguageSwitcher.tsx
│   │   │   ├── StatusIndicator.tsx
│   │   │   └── LoadingSpinner.tsx
│   │   └── ui/
│   │       └── [shadcn-ui components]
│   ├── pages/
│   │   ├── SetupMotorBus.tsx
│   │   ├── Calibration.tsx
│   │   ├── LeRobotDashboard.tsx
│   │   ├── LearningCenter.tsx
│   │   └── NotFound.tsx
│   ├── services/
│   │   ├── api.ts
│   │   ├── websocket.ts
│   │   └── i18n.ts
│   ├── hooks/
│   │   ├── useMotorData.ts
│   │   ├── useWebSocket.ts
│   │   └── useConfiguration.ts
│   ├── types/
│   │   ├── motor.ts
│   │   ├── port.ts
│   │   └── telemetry.ts
│   ├── i18n/
│   │   ├── en.json
│   │   ├── ko.json
│   │   └── index.ts
│   ├── App.tsx
│   └── main.tsx
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.ts

motorbot-backend/                           # FastAPI + Python
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models/
│   │   ├── motor.py
│   │   ├── port.py
│   │   ├── telemetry.py
│   │   └── configuration.py
│   ├── services/
│   │   ├── port_discovery.py
│   │   ├── motor_controller.py
│   │   ├── telemetry_collector.py
│   │   ├── configuration_manager.py
│   │   └── lerobot_bridge.py
│   ├── api/
│   │   ├── routes/
│   │   │   ├── ports.py
│   │   │   ├── motors.py
│   │   │   ├── configuration.py
│   │   │   ├── telemetry.py
│   │   │   └── logs.py
│   │   └── websocket.py
│   ├── database/
│   │   ├── db.py
│   │   ├── models.py
│   │   └── schemas.py
│   └── config.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── requirements.txt
├── Dockerfile
└── pytest.ini
```

**Structure Decision**: Full-stack web application with clear separation:
- **motorbot-frontend**: TypeScript/React NestJS application handling UI, layout, i18n, and API communication
- **motorbot-backend**: Python FastAPI service managing serial port communication, motor control, telemetry, and WebSocket streaming
- Each can be developed/tested/deployed independently
- Shared types via OpenAPI/GraphQL contracts

## Complexity Tracking

**Status**: ✅ No violations - architecture is straightforward and justified

Two-service architecture (frontend + backend) is justified:
- User explicitly requested separate NestJS (frontend) and FastAPI (backend) implementations
- WebSocket real-time communication requirement necessitates async backend
- SQL database and serial port management are backend concerns
- React UI with responsive design is frontend concern
- Clear separation enables parallel development and independent testing

## Phase 0 Complete ✅

**Deliverables Generated**:
- ✅ `research.md` - Design decisions, technology choices, alternatives considered (15 sections, ~500 lines)
- ✅ `data-model.md` - Entity definitions, validation rules, state machines, database schema (300+ lines)
- ✅ `contracts/api.openapi.yaml` - Complete REST API specification with request/response schemas
- ✅ `contracts/websocket.md` - WebSocket protocol, message types, error handling, examples
- ✅ `quickstart.md` - Development setup, common tasks, testing, troubleshooting

## Phase 1 Complete ✅

**Design finalized**:
- Full-stack architecture with clear responsibilities
- Data model with 6 core entities and relationships
- API contracts (REST + WebSocket) with complete message specifications
- Development setup and workflow documentation

## Phase 2 Pending

**Next Steps**:
Run `/speckit.tasks` to generate detailed implementation tasks (`tasks.md`)
