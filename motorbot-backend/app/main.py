"""
Motor Setup and Monitoring Dashboard - FastAPI Backend
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database.db import init_db
from app.api.routes import ports, motors, configuration, telemetry, tests, operations

# Initialize app lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager"""
    # Startup
    print("Starting Motor Setup and Monitoring Dashboard API...")
    print("Initializing database...")
    init_db()
    print("✓ Database initialized")
    print("✓ API ready to serve requests")
    yield
    # Shutdown
    print("Shutting down API...")

# Create FastAPI app
app = FastAPI(
    title="Motor Setup and Monitoring Dashboard API",
    description="Backend API for SO-ARM 101 robot motor configuration and monitoring",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
origins = [
    "http://localhost:3200",
    "http://127.0.0.1:3200",
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Motor Setup and Monitoring Dashboard API",
        "docs": "/docs",
        "openapi": "/openapi.json",
    }

@app.get("/api/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "motor-dashboard-api",
    }

# Register API routes
app.include_router(ports.router)
app.include_router(motors.router)
app.include_router(configuration.router)
app.include_router(telemetry.router)
app.include_router(tests.router)
app.include_router(operations.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3201)
