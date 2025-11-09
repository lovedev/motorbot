# Development Setup Guide

## Motor Setup and Monitoring Dashboard

This guide covers local development setup for the Motor Setup and Monitoring Dashboard - a web-based interface for configuring and monitoring 12 motors in the SO-ARM 101 robot.

## Prerequisites

- **Node.js**: 18.0.0 or higher
- **Python**: 3.11 or higher
- **npm**: 9.0.0 or higher
- **Git**: Latest version
- **Docker** (optional): For containerized development

## Project Structure

```
lerobot-installer/
├── motorbot-frontend/          # React + TypeScript frontend
│   ├── src/
│   │   ├── components/         # UI components
│   │   ├── pages/              # Page components
│   │   ├── services/           # API client, WebSocket
│   │   ├── hooks/              # Custom React hooks
│   │   ├── types/              # TypeScript types
│   │   ├── i18n/               # Internationalization
│   │   └── context/            # React Context
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── tailwind.config.ts
│
├── motorbot-backend/           # FastAPI Python backend
│   ├── app/
│   │   ├── models/             # SQLAlchemy models
│   │   ├── services/           # Business logic
│   │   ├── api/routes/         # API endpoints
│   │   ├── database/           # Database config
│   │   └── main.py             # FastAPI app
│   ├── tests/
│   │   ├── unit/               # Unit tests
│   │   └── integration/        # Integration tests
│   ├── requirements.txt
│   └── .env.example
│
├── docker-compose.yml          # Docker compose config
└── DEVELOPMENT.md              # This file
```

## Frontend Setup

### 1. Install Node Dependencies

```bash
cd motorbot-frontend
npm install
```

### 2. Create Environment File

```bash
cp .env.example .env.local
```

Edit `.env.local` with your backend URL:
```
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
```

### 3. Start Development Server

```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

### Available Commands

```bash
# Development
npm run dev              # Start dev server with hot reload

# Building
npm run build            # Build for production
npm run preview          # Preview production build locally

# Code Quality
npm run lint             # Run ESLint
npm run type-check       # Run TypeScript type checking

# Testing
npm run test             # Run Vitest
npm run test:ui          # Run tests with UI
npm run test:coverage    # Generate coverage report
```

## Backend Setup

### 1. Create Virtual Environment

```bash
cd motorbot-backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Create Environment File

```bash
cp .env.example .env
```

Edit `.env` with your settings:
```
DATABASE_URL=sqlite:///./motorbot.db
DEBUG=True
PORT=8000
HOST=0.0.0.0
LOG_LEVEL=INFO
SERIAL_TIMEOUT=2
```

### 4. Initialize Database

```bash
python -c "from app.database.db import init_db; init_db()"
```

This will create the SQLite database and all tables.

### 5. Start Development Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The backend will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs` (Swagger UI)
- Alternative Docs: `http://localhost:8000/redoc` (ReDoc)

### Available Commands

```bash
# Development
uvicorn app.main:app --reload

# Database
python -c "from app.database.db import init_db; init_db()"     # Initialize database
python -c "from app.database.db import drop_db; drop_db()"     # Drop all tables

# Code Quality
black app tests                  # Format code
flake8 app tests                 # Lint code
mypy app                         # Type checking

# Testing
pytest                           # Run all tests
pytest tests/unit/               # Run unit tests only
pytest tests/integration/        # Run integration tests only
pytest --cov=app --cov-report=html  # Generate coverage report
```

## Docker Setup (Optional)

### Build and Run with Docker Compose

```bash
docker-compose up -d
```

This will start both frontend (port 5173) and backend (port 8000).

### View Logs

```bash
docker-compose logs -f frontend
docker-compose logs -f backend
```

### Stop Services

```bash
docker-compose down
```

## API Endpoints

### Health Check
- **GET** `/api/health` - Service health status
- **Response**: `{ "status": "healthy", "service": "motor-dashboard-api" }`

### Documentation
- **Swagger UI**: `GET /docs`
- **ReDoc**: `GET /redoc`
- **OpenAPI Schema**: `GET /openapi.json`

## Internationalization (i18n)

The frontend supports English and Korean. Add translations in:
- `motorbot-frontend/src/i18n/en.json` (English)
- `motorbot-frontend/src/i18n/ko.json` (Korean)

Switch language using the language selector in the header.

## Database Models

The backend uses these core models:

1. **Port** - USB port connections and detection
2. **Motor** - Individual motors (1-12) in the robot arm
3. **MotorConfiguration** - Motor setup parameters
4. **TelemetryDataPoint** - Real-time sensor data
5. **OperationLog** - Operation history and tracking
6. **MotorTestEvent** - Test results and events

## Testing

### Frontend Tests

```bash
cd motorbot-frontend
npm run test
```

### Backend Tests

```bash
cd motorbot-backend
pytest -v
```

## Troubleshooting

### Frontend Issues

**Port 5173 already in use**
```bash
# Kill the process using port 5173
lsof -ti:5173 | xargs kill -9
```

**Module not found errors**
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Backend Issues

**Database locked error**
```bash
# Remove the database and reinitialize
rm motorbot-backend/motorbot.db
python -c "from app.database.db import init_db; init_db()"
```

**Import errors**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

**Port 8000 already in use**
```bash
# Kill the process using port 8000
lsof -ti:8000 | xargs kill -9
```

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Run tests and linting
4. Commit with clear messages
5. Push and create a Pull Request

## Resources

- [LeRobot Documentation](https://huggingface.co/docs/lerobot/)
- [SO-ARM 101 Setup](https://huggingface.co/docs/lerobot/so101)
- [React Documentation](https://react.dev)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Tailwind CSS Documentation](https://tailwindcss.com)
- [Pydantic Documentation](https://docs.pydantic.dev)

## Support

For issues or questions, refer to the project documentation or create an issue in the repository.
