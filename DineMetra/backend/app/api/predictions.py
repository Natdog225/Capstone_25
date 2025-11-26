from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

# Import ALL service wrappers
from app.services.ml_service import (
    predict_wait_time,
    predict_busyness,
    predict_item_sales,
)

# Import Schemas (or define them here if you prefer)
from app.models.schemas import WaitTimePredictionRequest, WaitTimePredictionResponse

router = APIRouter()


# --- Request Models ---
class BusynessRequest(BaseModel):
    timestamp: Optional[datetime] = None
    weather_condition: Optional[str] = None


class SalesRequest(BaseModel):
    item_id: int
    date: Optional[datetime] = None
    item_name: Optional[str] = "Unknown"
    category: Optional[str] = "Entrees"


# --- 1. Wait Time Endpoint ---
@router.post("/wait-time", response_model=WaitTimePredictionResponse)
async def predict_wait_time_endpoint(request: WaitTimePredictionRequest):
    """
    Predict wait time.
    Auto-fetches Weather & Events, OR uses manual test overrides.
    """
    try:
        timestamp = request.timestamp or datetime.now()

        # Check for manual overrides (The "What-If" Simulator)
        forced_factors = None

        if request.test_weather_condition:
            # FIX: Pass the STRING so the ML model can encode it (e.g., w_snowy=1)
            forced_factors = {
                "test_weather_condition": request.test_weather_condition,
                # We set event impact to 0 for this specific test to isolate weather
                "event_impact_minutes": 0,
            }

        result = predict_wait_time(
            party_size=request.party_size,
            timestamp=timestamp,
            current_occupancy=request.current_occupancy,
            external_factors=forced_factors,
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Wait time prediction failed: {str(e)}"
        )


# --- 2. Busyness Endpoint ---
@router.post("/busyness")
async def predict_busyness_endpoint(request: BusynessRequest):
    try:
        target_time = request.timestamp or datetime.now()
        result = predict_busyness(
            timestamp=target_time, weather=request.weather_condition
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Busyness prediction failed: {str(e)}"
        )


# --- 3. Sales Endpoint ---
@router.post("/sales")
async def predict_sales_endpoint(request: SalesRequest):
    try:
        target_date = request.date or datetime.now()
        result = predict_item_sales(item_id=request.item_id, date=target_date)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Sales prediction failed: {str(e)}"
        )
