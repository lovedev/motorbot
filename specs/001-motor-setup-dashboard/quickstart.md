# Quickstart: Motor Setup and Monitoring Dashboard

**Date**: 2025-11-09
**Feature**: Motor Setup and Monitoring Dashboard (001-motor-setup-dashboard)
**Status**: Development Setup Guide

---

## Project Overview

Motor Setup and Monitoring Dashboard enables roboticists to configure, test, and monitor the SO-ARM 101 robot's 12 servo motors through a web-based interface.

**Architecture**:
- **Frontend**: React 18 + TypeScript + shadcn-ui (dark theme, responsive layout)
- **Backend**: FastAPI + Python 3.10+ (serial port management, real-time telemetry)
- **Communication**: REST API + WebSocket (telemetry streaming)
- **Database**: SQLite (configuration persistence, operation logs)

---

## Prerequisites

### System Requirements
- **OS**: macOS, Linux (Windows with WSL2)
- **Node.js**: 18+ (for frontend)
- **Python**: 3.10+ (for backend)
- **USB**: Robot arm connected via USB serial port

### Development Tools
- **IDE**: VS Code with ESLint, Prettier, Python extensions
- **Git**: For version control
- **Package Managers**: npm (Node), pip (Python)

---

## Setup Instructions

### 1. Clone and Navigate to Project

```bash
cd /Users/lovedev/workspace/lerobot-installer
git checkout 001-motor-setup-dashboard
```

### 2. Backend Setup (FastAPI)

#### Create Python Virtual Environment

```bash
cd motorbot-backend
python3.10 -m venv venv
source venv/bin/activate  # macOS/Linux
# or: venv\Scripts\activate  # Windows
```

#### Install Dependencies

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

#### Environment Configuration

Create `.env` file:

```bash
# motorbot-backend/.env
PYTHONUNBUFFERED=1
DEBUG=True
DATABASE_URL=sqlite:///motorbot.db
LOG_LEVEL=INFO
PORT=8000
HOST=0.0.0.0
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

#### Database Initialization

```bash
# Create database and tables
python -m app.main --init-db

# Or manually in Python shell:
# python
# >>> from app.database.db import init_db; init_db()
```

#### Start Backend Server

```bash
# Development server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or:
python -m app.main
```

**Expected Output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

**API Documentation**: http://localhost:8000/docs (Swagger UI)

---

### 3. Frontend Setup (React + Vite)

#### Install Dependencies

```bash
cd motorbot-frontend
npm install
```

#### Environment Configuration

Create `.env` file:

```bash
# motorbot-frontend/.env
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
VITE_APP_NAME=MotorBot
```

#### Start Development Server

```bash
npm run dev
```

**Expected Output**:
```
VITE v5.0.0  ready in 234 ms

➜  Local:   http://localhost:5173/
➜  press h to show help
```

**Access Frontend**: http://localhost:5173

---

## Development Workflow

### File Structure

```
motorbot-frontend/
├── src/
│   ├── components/
│   │   ├── Layout/          # Header, Sidebar, MainLayout
│   │   ├── MotorSetup/      # Port discovery, port cards
│   │   ├── MotorConfiguration/ # Config wizard, forms
│   │   ├── Dashboard/       # Telemetry display, alerts
│   │   └── Common/          # Shared components
│   ├── pages/               # Page components (routing)
│   ├── services/            # API client, WebSocket client
│   ├── hooks/               # Custom React hooks
│   ├── types/               # TypeScript interfaces
│   ├── i18n/                # Translation files (en.json, ko.json)
│   └── App.tsx              # Root component
├── tests/                   # Unit, integration, E2E tests
└── package.json

motorbot-backend/
├── app/
│   ├── main.py             # FastAPI app initialization
│   ├── models/             # Pydantic data models
│   ├── services/           # Business logic
│   ├── api/
│   │   ├── routes/         # API endpoints
│   │   └── websocket.py    # WebSocket handler
│   ├── database/           # SQLAlchemy ORM, schemas
│   └── config.py           # Configuration management
├── tests/                  # Unit, integration tests
├── requirements.txt        # Python dependencies
└── Dockerfile             # Production container
```

### Common Development Tasks

#### Adding a New API Endpoint

1. **Define request/response models** in `motorbot-backend/app/models/`:
   ```python
   from pydantic import BaseModel

   class MotorTestRequest(BaseModel):
       motor_id: int
       test_type: str
   ```

2. **Create route handler** in `motorbot-backend/app/api/routes/motors.py`:
   ```python
   from fastapi import APIRouter

   router = APIRouter(prefix="/motors", tags=["motors"])

   @router.post("/{motor_id}/test")
   async def test_motor(motor_id: int, request: MotorTestRequest):
       # Implementation
       return {"success": True}
   ```

3. **Register route** in `motorbot-backend/app/main.py`:
   ```python
   from app.api.routes import motors
   app.include_router(motors.router, prefix="/api")
   ```

4. **Update OpenAPI contract** in `specs/001-motor-setup-dashboard/contracts/api.openapi.yaml`

5. **Test with curl**:
   ```bash
   curl -X POST http://localhost:8000/api/motors/5/test \
     -H "Content-Type: application/json" \
     -d '{"test_type": "position_move"}'
   ```

#### Adding a New Frontend Component

1. **Create component file** in `motorbot-frontend/src/components/`:
   ```tsx
   // MotorCard.tsx
   import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

   interface MotorCardProps {
     motorId: number;
     status: 'healthy' | 'warning' | 'error';
   }

   export const MotorCard: React.FC<MotorCardProps> = ({ motorId, status }) => {
     return (
       <Card className="w-full">
         <CardHeader>
           <CardTitle>Motor {motorId}</CardTitle>
         </CardHeader>
         <CardContent>
           <div className={`status-${status}`}>{status}</div>
         </CardContent>
       </Card>
     );
   };
   ```

2. **Use in page**:
   ```tsx
   // pages/Dashboard.tsx
   import { MotorCard } from "@/components/Dashboard/MotorCard";

   export default function Dashboard() {
     return (
       <div className="grid grid-cols-3 gap-4">
         {motors.map((motor) => (
           <MotorCard key={motor.id} motorId={motor.id} status={motor.status} />
         ))}
       </div>
     );
   }
   ```

#### Adding Translations

1. **Update translation files**:
   ```json
   // motorbot-frontend/src/i18n/en.json
   {
     "setup": {
       "title": "Setup MotorBus",
       "portDiscovery": "Discover Ports",
       "testMotor": "Test Motor"
     }
   }
   ```

   ```json
   // motorbot-frontend/src/i18n/ko.json
   {
     "setup": {
       "title": "모터버스 설정",
       "portDiscovery": "포트 발견",
       "testMotor": "모터 테스트"
     }
   }
   ```

2. **Use in component**:
   ```tsx
   import { useTranslation } from '@/services/i18n';

   export function SetupPage() {
     const t = useTranslation();
     return <h1>{t('setup.title')}</h1>;
   }
   ```

---

## Testing

### Frontend Tests

```bash
cd motorbot-frontend

# Run all tests
npm run test

# Run with coverage
npm run test:coverage

# Watch mode
npm run test:watch
```

**Test Structure**:
```
motorbot-frontend/tests/
├── unit/              # Component unit tests
├── integration/       # Multi-component tests
└── e2e/               # End-to-end tests (Playwright)
```

### Backend Tests

```bash
cd motorbot-backend
source venv/bin/activate

# Run all tests
pytest

# Run specific test file
pytest tests/test_ports.py

# Run with coverage
pytest --cov=app

# Watch mode (requires pytest-watch)
ptw
```

**Test Structure**:
```
motorbot-backend/tests/
├── unit/              # Model, service tests
├── integration/       # API endpoint tests
└── fixtures/          # Test data, mocks
```

### Manual Testing

**Port Discovery**:
```bash
# Terminal 1: Start backend
cd motorbot-backend && uvicorn app.main:app --reload

# Terminal 2: Test port discovery
curl http://localhost:8000/api/ports | json_pp

# Terminal 3: Test specific port
curl -X POST http://localhost:8000/api/ports/ttyACM0/test | json_pp
```

**WebSocket Telemetry**:
```bash
# Use websocat or wscat
wscat -c ws://localhost:8000/ws/telemetry

# Or in Python
import websocket
ws = websocket.create_connection("ws://localhost:8000/ws/telemetry")
while True:
    print(ws.recv())
```

---

## Building for Production

### Frontend Build

```bash
cd motorbot-frontend
npm run build

# Output: dist/
# Serve with: npx serve dist
```

### Backend Docker Build

```bash
cd motorbot-backend
docker build -t motorbot-backend:latest .
docker run -p 8000:8000 motorbot-backend:latest
```

### Docker Compose (Full Stack)

```bash
# From repo root
docker-compose up

# Access:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

---

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn app.main:app --port 8001
```

### WebSocket Connection Refused

- Ensure backend is running: `http://localhost:8000/docs`
- Check CORS settings in `motorbot-backend/.env`
- Verify frontend URL in `motorbot-frontend/.env`

### Database Locked

```bash
# SQLite sometimes locks during concurrent access
# Solution: Clear and reinit database
rm motorbot.db
python motorbot-backend/app/main.py --init-db
```

### Module Not Found (Python)

```bash
# Ensure virtual environment is activated
source motorbot-backend/venv/bin/activate

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

### Import Errors (TypeScript/JavaScript)

```bash
# Clear node_modules and reinstall
cd motorbot-frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

---

## Key Endpoints & URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:5173 | Web UI |
| Backend API | http://localhost:8000 | REST endpoints |
| API Docs | http://localhost:8000/docs | Swagger UI |
| ReDoc | http://localhost:8000/redoc | Alternative API docs |
| WebSocket | ws://localhost:8000/ws/telemetry | Real-time telemetry |
| Database | ./motorbot.db | SQLite database (backend) |

---

## Next Steps

1. **Review Design Specifications**: Read `data-model.md` and `research.md`
2. **Study API Contracts**: Review `contracts/api.openapi.yaml` and `contracts/websocket.md`
3. **Generate Implementation Tasks**: Run `/speckit.tasks` to create detailed task breakdown
4. **Start Development**: Implement features per task list

---

## Resources

- **LeRobot Documentation**: https://huggingface.co/docs/lerobot/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **React Docs**: https://react.dev/
- **shadcn/ui**: https://ui.shadcn.com/
- **Tailwind CSS**: https://tailwindcss.com/
- **i18next**: https://www.i18next.com/

---

## Support & Questions

For questions or issues during setup:
1. Check troubleshooting section above
2. Review implementation plan in `plan.md`
3. Check test fixtures for example usage
4. Review API documentation at `http://localhost:8000/docs`
