from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

# Import the router
from app.api import predictions

# Import the model loader
from app.services.ml_service import initialize_models
from app.api import websocket
from app.api import historical

#Dashboard stuff
from app.api import predictions, dashboard, monitoring

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --- LIFESPAN MANAGER ---
# This handles both startup and shutdown logic in one place.
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. STARTUP LOGIC (Runs before the app starts accepting requests)
    logger.info("Starting Dinemetra API...")
    try:
        initialize_models()
        logger.info("✅ ML Models loaded and ready.")
    except Exception as e:
        logger.error(f" Failed to load ML models: {e}")

    yield  # The app runs while execution pauses here

    # 2. SHUTDOWN LOGIC
    logger.info("Dinemetra API shutting down...")


# --- APP INITIALIZATION ---
app = FastAPI(
    title="Dinemetra API",
    description="Backend for Restaurant Prediction System",
    version="1.1.0",
    lifespan=lifespan,  # <--- Register the lifespan handler here
)

# --- CORS CONFIGURATION ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ROUTERS ---
app.include_router(predictions.router, prefix="/api/predictions", tags=["Predictions"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(monitoring.router, prefix="/api/monitoring", tags=["monitoring"])
app.include_router(websocket.router)
app.include_router(historical.router)


# --- HEALTH CHECK ---
@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Dinemetra Intelligence Engine is running",
        "version": "1.1.0",
    }
