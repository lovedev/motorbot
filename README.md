# MotorBot 🤖

![Status](https://img.shields.io/badge/status-active-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)
![Version](https://img.shields.io/badge/version-0.0.0-orange)

**Motor Control Dashboard with real-time telemetry, configuration management, and automated testing**

## 📋 Overview

MotorBot is a comprehensive motor control system consisting of:
- **Frontend Dashboard** - React + TypeScript with Tailwind CSS
- **Backend API** - FastAPI with WebSocket support
- **Real-time Telemetry** - WebSocket-based live data streaming
- **Multi-language Support** - English & Korean

### Key Features
✅ Real-time motor telemetry monitoring
✅ Motor setup and calibration workflows
✅ Port configuration management
✅ Automated test execution
✅ Dark mode support
✅ Responsive design
✅ WebSocket integration for live updates

---

## 🚀 Quick Start

### Prerequisites
- Node.js v18+
- Python 3.10+
- npm v8+

### Frontend Setup

```bash
cd motorbot-frontend

# Install dependencies
npm install

# Development server
npm run dev      # http://localhost:3200

# Build for production
npm run build
```

### Backend Setup

```bash
cd motorbot-backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run development server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 3201
```

---

## 📂 Project Structure

```
motorbot/
├── motorbot-frontend/          # React + TypeScript frontend
│   ├── src/
│   │   ├── components/         # UI components
│   │   ├── pages/              # Page components
│   │   ├── services/           # API & WebSocket services
│   │   ├── context/            # React Context
│   │   └── i18n/               # Internationalization
│   ├── package.json
│   └── tailwind.config.ts
│
├── motorbot-backend/           # FastAPI backend
│   ├── app/
│   │   ├── api/routes/         # API endpoints
│   │   ├── models/             # SQLAlchemy models
│   │   ├── schemas/            # Pydantic schemas
│   │   ├── services/           # Business logic
│   │   └── database/           # Database config
│   └── requirements.txt
│
├── specs/                      # Feature specifications
├── troubleshooting.md          # Troubleshooting guide
├── DEVELOPMENT.md              # Development guide
└── docker-compose.yml          # Docker setup
```

---

## 🔧 Configuration

### Environment Variables

#### Frontend (.env)
```env
VITE_API_URL=http://localhost:3201/api
VITE_WS_URL=ws://localhost:3201/ws
```

#### Backend (.env)
```env
DATABASE_URL=sqlite:///./motorbot.db
DEBUG=true
CORS_ORIGINS=http://localhost:3200
```

---

## 📡 API Endpoints

### Motors
- `GET /api/motors` - List all motors
- `POST /api/motors` - Create motor
- `GET /api/motors/{id}` - Get motor details
- `PUT /api/motors/{id}` - Update motor
- `DELETE /api/motors/{id}` - Delete motor

### Telemetry
- `GET /api/telemetry/{motor_id}` - Get motor telemetry
- `WebSocket /ws` - Real-time telemetry stream

### Configuration
- `GET /api/configuration` - Get system configuration
- `PUT /api/configuration` - Update configuration

### Operations
- `POST /api/operations/calibrate` - Calibrate motor
- `POST /api/operations/test` - Run motor test

### Ports
- `GET /api/ports` - List available ports
- `POST /api/ports/configure` - Configure port

---

## 🌐 WebSocket Events

### Subscribe to Telemetry
```javascript
{
  "type": "subscribe_telemetry",
  "motor_id": 1
}
```

### Subscribe to Status Updates
```javascript
{
  "type": "subscribe_status",
  "motor_id": 1
}
```

### Telemetry Data
```javascript
{
  "type": "telemetry",
  "motor_id": 1,
  "angle": 45.5,
  "speed": 1200,
  "torque": 2.5,
  "temperature": 35.2,
  "voltage": 12.0,
  "current": 2.5,
  "error_code": null,
  "timestamp": "2025-11-09T14:30:00Z"
}
```

---

## 🛠️ Development

### Frontend Development
```bash
cd motorbot-frontend

# Development with hot reload
npm run dev

# Type checking
tsc

# Linting
npm run lint

# Build
npm run build

# Preview production build
npm run preview
```

### Backend Development
```bash
cd motorbot-backend

# Run with auto-reload
python -m uvicorn app.main:app --reload

# Run tests
pytest

# Database migrations
alembic upgrade head
```

---

## 🐛 Troubleshooting

See [troubleshooting.md](./troubleshooting.md) for detailed troubleshooting guides.

### Common Issues

#### CSS not loading
- Ensure Tailwind v3 is installed: `npm list tailwindcss`
- Clear browser cache: Cmd+Shift+Delete
- Restart dev server: `npm run dev`

#### API connection errors
- Check backend is running: `http://localhost:3201/docs`
- Verify CORS settings in backend
- Check network in browser DevTools

#### WebSocket connection fails
- Ensure backend WebSocket server is running
- Check firewall/proxy settings
- Verify `VITE_WS_URL` environment variable

---

## 📚 Documentation

- [DEVELOPMENT.md](./DEVELOPMENT.md) - Development setup & conventions
- [API.md](./API.md) - Complete API documentation
- [troubleshooting.md](./troubleshooting.md) - Troubleshooting guide
- [specs/](./specs/) - Feature specifications & technical documentation

---

## 📊 Project Status

### Phase 1: Motor Control Dashboard ✅
- [x] Dashboard UI with motor status
- [x] Real-time telemetry WebSocket
- [x] Motor setup workflow
- [x] Calibration interface
- [x] Dark mode support
- [x] i18n support (EN/KO)

### Phase 2: Advanced Features 🔄
- [ ] Advanced analytics
- [ ] Historical data visualization
- [ ] Performance optimization
- [ ] Enhanced testing suite

### Phase 3: Production Ready 📋
- [ ] Performance monitoring
- [ ] Security hardening
- [ ] CI/CD pipeline
- [ ] Load testing
- [ ] Documentation completion

See [PHASE1_SUMMARY.md](./PHASE1_SUMMARY.md) for detailed phase information.

---

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Commit changes: `git commit -am "Add your feature"`
3. Push branch: `git push origin feature/your-feature`
4. Open a Pull Request

---

## 📝 License

MIT License - See LICENSE file for details

---

## 👤 Author

Developed with Claude Code

**Get Help**:
- 📖 See [troubleshooting.md](./troubleshooting.md) for common issues
- 📞 Check [DEVELOPMENT.md](./DEVELOPMENT.md) for setup help
- 🐛 Report issues on GitHub

---

## 🎯 Next Steps

1. **Start Development**
   ```bash
   npm run dev  # Frontend
   python -m uvicorn app.main:app --reload  # Backend
   ```

2. **Access the Dashboard**
   - Frontend: http://localhost:3200
   - API Docs: http://localhost:3201/docs

3. **Read Documentation**
   - Start with [DEVELOPMENT.md](./DEVELOPMENT.md)
   - Check [API.md](./API.md) for endpoints
   - Review [troubleshooting.md](./troubleshooting.md) for common issues

---

**Last Updated**: 2025-11-09
**Repository**: https://github.com/lovedev/motorbot
