"""
DineMetra API - Main Application
Complete real-time restaurant analytics platform
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    logger.info("🚀 Starting DineMetra API...")

    # Import and start background tasks
    try:
        from app.tasks.background_tasks import get_background_task_service

        background_service = get_background_task_service()
        background_service.start()
        logger.info("✅ Background tasks started")
    except Exception as e:
        logger.warning(f"Background tasks not started: {e}")
        logger.info("Continuing without background tasks...")

    logger.info("✅ DineMetra API started successfully")
    logger.info("📊 Dashboard: http://localhost:8000/api/dashboard/dashboard")
    logger.info("📡 WebSocket: ws://localhost:8000/ws/dashboard")
    logger.info("📖 API Docs: http://localhost:8000/docs")
    logger.info("✅ CSV Upload API enabled (live demo feature)")

    yield

    # Shutdown
    logger.info("⏹️  Shutting down DineMetra API...")
    try:
        from app.tasks.background_tasks import get_background_task_service

        background_service = get_background_task_service()
        background_service.stop()
    except:
        pass
    logger.info("✅ Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="DineMetra API",
    description="Real-time restaurant analytics and prediction platform",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers - import only what exists
from app.api import dashboard, predictions, websocket
from app.api.upload import router as upload_router
from app.api.monitoring import router as monitoring_router


# Include core routers (always present)
app.include_router(dashboard.router)
app.include_router(predictions.router)
app.include_router(upload_router, prefix="/api/upload", tags=["Upload"])
app.include_router(monitoring_router, prefix="/api/monitoring", tags=["Monitoring"])


# Include legacy routers for backwards compatibility
try:
    app.include_router(dashboard.legacy_router)
    logger.info("✅ Legacy dashboard endpoints enabled for backwards compatibility")
except AttributeError:
    pass

try:
    app.include_router(predictions.legacy_router)
    logger.info("✅ Legacy prediction endpoints enabled for backwards compatibility")
except AttributeError:
    pass

app.include_router(websocket.router)

# Try to include optional routers (new features)
try:
    from app.api import historical

    app.include_router(historical.router)
    logger.info("✅ Historical API enabled")
except ImportError:
    logger.info("ℹ️  Historical API not available")

try:
    from app.api import alerts

    app.include_router(alerts.router)
    logger.info("✅ Alerts API enabled")
except ImportError:
    logger.info("ℹ️  Alerts API not available")

try:
    from app.api import experiments

    app.include_router(experiments.router)
    logger.info("✅ Experiments API enabled")
except ImportError:
    logger.info("ℹ️  Experiments API not available")


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "name": "DineMetra API",
        "version": "2.0.0",
        "status": "running",
        "features": [
            "Enhanced ML Predictions",
            "Real-time WebSocket Updates",
            "Historical Comparisons",
            "Alert System",
            "A/B Testing",
            "Background Task Automation",
        ],
        "endpoints": {
            "dashboard": "/api/dashboard/dashboard",
            "predictions": "/api/predictions/wait-time-enhanced",
            "historical": "/api/historical/compare/all",
            "alerts": "/api/alerts/active",
            "experiments": "/api/experiments/stats",
            "websocket": "ws://localhost:8000/ws/dashboard",
            "docs": "/docs",
        },
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    try:
        from app.tasks.background_tasks import get_background_task_service

        background_service = get_background_task_service()
        task_status = background_service.get_task_status()
    except:
        task_status = {"status": "not_running", "tasks": []}

    return {"status": "healthy", "background_tasks": task_status}


@app.get("/api/system/info")
def system_info():
    """System information endpoint"""
    info = {}

    try:
        from app.websocket.manager import get_connection_manager

        conn_manager = get_connection_manager()
        info["websocket_connections"] = conn_manager.get_connection_stats()
    except:
        pass

    try:
        from app.services.alert_service import get_alert_service

        alert_service = get_alert_service()
        info["alerts"] = alert_service.get_alert_stats()
    except:
        pass

    try:
        from app.services.ab_testing_service import get_ab_testing_service

        ab_service = get_ab_testing_service()
        info["ab_testing"] = ab_service.get_summary_stats()
    except:
        pass

    return {"success": True, "info": info}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
