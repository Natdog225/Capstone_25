from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

# Import ALL service wrappers
from app.services.ml_service import (
    predict_wait_time,
    predict_busyness,
    predict_item_sales
)

# If you have these in app/models/schemas.py, you can import them.
# If not, defining them here is perfectly fine and safer for now.
from app.models.schemas import WaitTimePredictionRequest, WaitTimePredictionResponse 

router = APIRouter()

# --- Request Models for the missing endpoints ---
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
    Auto-fetches Weather & Events via ML Service.
    """
    try:
        timestamp = request.timestamp or datetime.now()

        result = predict_wait_time(
            party_size=request.party_size,
            timestamp=timestamp,
            current_occupancy=request.current_occupancy,
            external_factors=None # Service handles the fetching
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Wait time prediction failed: {str(e)}")

# --- 2. Busyness Endpoint (ADDED) ---
@router.post("/busyness")
async def predict_busyness_endpoint(request: BusynessRequest):
    """
    Predicts if the restaurant will be Slow, Moderate, or Peak.
    """
    try:
        target_time = request.timestamp or datetime.now()
        
        result = predict_busyness(
            timestamp=target_time,
            weather=request.weather_condition
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Busyness prediction failed: {str(e)}")

# --- 3. Sales Endpoint (ADDED) ---
@router.post("/sales")
async def predict_sales_endpoint(request: SalesRequest):
    """
    Predicts how many of a specific item will sell on a given date.
    """
    try:
        target_date = request.date or datetime.now()
        
        result = predict_item_sales(
            item_id=request.item_id,
            date=target_date
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")
