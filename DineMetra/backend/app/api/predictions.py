"""
Predictions API - Updated with Enhanced Factor Breakdowns
Keeps your existing endpoints + adds enhanced versions with detailed factors
"""

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

from app.services.enhanced_prediction_service import enhanced_prediction_service

# Import Response Schema
from app.models.schemas import WaitTimePredictionResponse

# ✅ FIX: Add proper prefix to organize endpoints
router = APIRouter(prefix="/api/predictions", tags=["predictions"])


# =============================================================================
# REQUEST MODELS
# =============================================================================


class WaitTimeRequest(BaseModel):
    party_size: int
    current_occupancy: float
    timestamp: Optional[datetime] = None
    test_weather_condition: Optional[str] = None


class BusynessRequest(BaseModel):
    timestamp: Optional[datetime] = None
    weather_condition: Optional[str] = None


class SalesRequest(BaseModel):
    item_id: int
    date: Optional[datetime] = None
    item_name: Optional[str] = "Unknown"
    category: Optional[str] = "Entrees"


# =============================================================================
# ENHANCED ENDPOINTS (Primary - with detailed factor breakdowns)
# =============================================================================


@router.post("/wait-time")
async def predict_wait_time_enhanced_endpoint(request: WaitTimeRequest):
    """
    Enhanced wait time prediction with detailed factor breakdown

    Returns:
    - Predicted wait minutes
    - Confidence score
    - Detailed factors:
      * Current occupancy impact
      * Weather impact (from weather.gov)
      * Event impact (from Ticketmaster)
      * Time/day factors
      * Historical comparison
    - Human-readable explanation
    """
    try:
        timestamp = request.timestamp or datetime.now()

        result = enhanced_prediction_service.predict_wait_time_enhanced(
            party_size=request.party_size,
            current_occupancy=request.current_occupancy,
            timestamp=timestamp,
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Enhanced wait time prediction failed: {str(e)}"
        )


@router.post("/busyness")
async def predict_busyness_enhanced_endpoint(request: BusynessRequest):
    """
    Enhanced busyness prediction with detailed factor breakdown

    Returns:
    - Busyness level (Slow/Moderate/Busy/Peak)
    - Percentage (0-100)
    - Expected guest count
    - Confidence score
    - Detailed factors:
      * Day/time factors
      * Weather conditions
      * Nearby events
      * Historical comparison
    - Staffing recommendation
    """
    try:
        target_time = request.timestamp or datetime.now()

        result = enhanced_prediction_service.predict_busyness_enhanced(
            timestamp=target_time
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Enhanced busyness prediction failed: {str(e)}"
        )


@router.post("/sales")
async def predict_sales_enhanced_endpoint(request: SalesRequest):
    """
    Enhanced sales prediction with detailed factor breakdown

    Returns:
    - Predicted quantity
    - Confidence score
    - Confidence margin (low/high range)
    - Detailed factors:
      * Day/date factors
      * Weather impact (for weather-sensitive items)
      * Event impact
      * Historical trends
    - Purchasing recommendation
    """
    try:
        target_date = request.date or datetime.now()

        result = enhanced_prediction_service.predict_sales_enhanced(
            item_id=request.item_id,
            target_date=target_date,
            item_name=request.item_name,
            category=request.category,
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Enhanced sales prediction failed: {str(e)}"
        )


# =============================================================================
# ORIGINAL ENDPOINTS (for backwards compatibility)
# =============================================================================


@router.post("/wait-time-legacy", response_model=WaitTimePredictionResponse)
async def predict_wait_time_legacy(request: WaitTimeRequest):
    """
    Predict wait time (LEGACY VERSION - for backwards compatibility)

    Auto-fetches Weather & Events, OR uses manual test overrides.
    Use /wait-time for the enhanced version with factor breakdown.
    """
    try:
        timestamp = request.timestamp or datetime.now()

        forced_factors = None
        if request.test_weather_condition:
            forced_factors = {
                "test_weather_condition": request.test_weather_condition,
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


@router.post("/busyness-legacy")
async def predict_busyness_legacy(request: BusynessRequest):
    """
    Predict busyness (LEGACY VERSION - for backwards compatibility)

    Use /busyness for the enhanced version with factor breakdown.
    """
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


@router.post("/sales-legacy")
async def predict_sales_legacy(request: SalesRequest):
    """
    Predict item sales (LEGACY VERSION - for backwards compatibility)

    Use /sales for the enhanced version with factor breakdown.
    """
    try:
        target_date = request.date or datetime.now()
        result = predict_item_sales(item_id=request.item_id, date=target_date)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Sales prediction failed: {str(e)}"
        )


# =============================================================================
# COMPARISON ENDPOINT (helps understand the difference)
# =============================================================================


@router.post("/compare")
async def compare_predictions(request: WaitTimeRequest):
    """
    Compare original vs enhanced predictions

    Useful for testing and understanding the differences between
    legacy predictions and enhanced predictions with detailed factors.
    """
    try:
        timestamp = request.timestamp or datetime.now()

        # Get original prediction
        original = predict_wait_time(
            party_size=request.party_size,
            timestamp=timestamp,
            current_occupancy=request.current_occupancy,
            external_factors=None,
        )

        # Get enhanced prediction
        enhanced = enhanced_prediction_service.predict_wait_time_enhanced(
            party_size=request.party_size,
            current_occupancy=request.current_occupancy,
            timestamp=timestamp,
        )

        return {
            "original": original,
            "enhanced": enhanced,
            "differences": {
                "has_detailed_factors": len(enhanced.get("factors", {}))
                > len(original.get("factors", {})),
                "has_explanation": "explanation" in enhanced,
                "has_category": "wait_category" in enhanced,
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")
