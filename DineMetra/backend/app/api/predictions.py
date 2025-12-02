"""
Predictions API - Backwards Compatible Version
Supports BOTH old URLs and new organized URLs
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

# Create TWO routers - one with prefix, one without (for backwards compatibility)
router = APIRouter(prefix="/api/predictions", tags=["predictions"])
legacy_router = APIRouter(tags=["predictions-legacy"])


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
# SHARED IMPLEMENTATION FUNCTIONS
# =============================================================================


def _predict_wait_time_impl(request: WaitTimeRequest):
    """Shared implementation for wait time prediction"""
    timestamp = request.timestamp or datetime.now()

    forced_factors = None
    if request.test_weather_condition:
        forced_factors = {
            "test_weather_condition": request.test_weather_condition,
            "event_impact_minutes": 0,
        }

    return predict_wait_time(
        party_size=request.party_size,
        timestamp=timestamp,
        current_occupancy=request.current_occupancy,
        external_factors=forced_factors,
    )


def _predict_wait_time_enhanced_impl(request: WaitTimeRequest):
    """Shared implementation for enhanced wait time prediction"""
    timestamp = request.timestamp or datetime.now()

    return enhanced_prediction_service.predict_wait_time_enhanced(
        party_size=request.party_size,
        current_occupancy=request.current_occupancy,
        timestamp=timestamp,
    )


def _predict_busyness_impl(request: BusynessRequest):
    """Shared implementation for busyness prediction"""
    target_time = request.timestamp or datetime.now()
    return predict_busyness(timestamp=target_time, weather=request.weather_condition)


def _predict_busyness_enhanced_impl(request: BusynessRequest):
    """Shared implementation for enhanced busyness prediction"""
    target_time = request.timestamp or datetime.now()
    return enhanced_prediction_service.predict_busyness_enhanced(timestamp=target_time)


def _predict_sales_impl(request: SalesRequest):
    """Shared implementation for sales prediction"""
    target_date = request.date or datetime.now()
    return predict_item_sales(item_id=request.item_id, date=target_date)


def _predict_sales_enhanced_impl(request: SalesRequest):
    """Shared implementation for enhanced sales prediction"""
    target_date = request.date or datetime.now()
    return enhanced_prediction_service.predict_sales_enhanced(
        item_id=request.item_id,
        target_date=target_date,
        item_name=request.item_name,
        category=request.category,
    )


# =============================================================================
# NEW ORGANIZED ENDPOINTS (under /api/predictions)
# =============================================================================


@router.post("/wait-time", response_model=WaitTimePredictionResponse)
async def predict_wait_time_new(request: WaitTimeRequest):
    """Predict wait time (NEW URL: /api/predictions/wait-time)"""
    try:
        return _predict_wait_time_impl(request)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Wait time prediction failed: {str(e)}"
        )


@router.post("/busyness")
async def predict_busyness_new(request: BusynessRequest):
    """Predict busyness (NEW URL: /api/predictions/busyness)"""
    try:
        return _predict_busyness_impl(request)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Busyness prediction failed: {str(e)}"
        )


@router.post("/sales")
async def predict_sales_new(request: SalesRequest):
    """Predict item sales (NEW URL: /api/predictions/sales)"""
    try:
        return _predict_sales_impl(request)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Sales prediction failed: {str(e)}"
        )


@router.post("/wait-time-enhanced")
async def predict_wait_time_enhanced_new(request: WaitTimeRequest):
    """Enhanced wait time prediction (NEW URL: /api/predictions/wait-time-enhanced)"""
    try:
        return _predict_wait_time_enhanced_impl(request)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Enhanced wait time prediction failed: {str(e)}"
        )


@router.post("/busyness-enhanced")
async def predict_busyness_enhanced_new(request: BusynessRequest):
    """Enhanced busyness prediction (NEW URL: /api/predictions/busyness-enhanced)"""
    try:
        return _predict_busyness_enhanced_impl(request)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Enhanced busyness prediction failed: {str(e)}"
        )


@router.post("/sales-enhanced")
async def predict_sales_enhanced_new(request: SalesRequest):
    """Enhanced sales prediction (NEW URL: /api/predictions/sales-enhanced)"""
    try:
        return _predict_sales_enhanced_impl(request)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Enhanced sales prediction failed: {str(e)}"
        )


@router.post("/compare-predictions")
async def compare_predictions_new(request: WaitTimeRequest):
    """Compare predictions (NEW URL: /api/predictions/compare-predictions)"""
    try:
        timestamp = request.timestamp or datetime.now()

        original = predict_wait_time(
            party_size=request.party_size,
            timestamp=timestamp,
            current_occupancy=request.current_occupancy,
            external_factors=None,
        )

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


# =============================================================================
# LEGACY ENDPOINTS (OLD URLs - for backwards compatibility)
# Keep these so existing frontend doesn't break!
# =============================================================================


@legacy_router.post("/wait-time", response_model=WaitTimePredictionResponse)
async def predict_wait_time_legacy(request: WaitTimeRequest):
    """
    Predict wait time (LEGACY URL: /wait-time)

    ⚠️ DEPRECATED: Use /api/predictions/wait-time instead
    This endpoint is kept for backwards compatibility only.
    """
    try:
        return _predict_wait_time_impl(request)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Wait time prediction failed: {str(e)}"
        )


@legacy_router.post("/busyness")
async def predict_busyness_legacy(request: BusynessRequest):
    """
    Predict busyness (LEGACY URL: /busyness)

    ⚠️ DEPRECATED: Use /api/predictions/busyness instead
    This endpoint is kept for backwards compatibility only.
    """
    try:
        return _predict_busyness_impl(request)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Busyness prediction failed: {str(e)}"
        )


@legacy_router.post("/sales")
async def predict_sales_legacy(request: SalesRequest):
    """
    Predict item sales (LEGACY URL: /sales)

    ⚠️ DEPRECATED: Use /api/predictions/sales instead
    This endpoint is kept for backwards compatibility only.
    """
    try:
        return _predict_sales_impl(request)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Sales prediction failed: {str(e)}"
        )


@legacy_router.post("/wait-time-enhanced")
async def predict_wait_time_enhanced_legacy(request: WaitTimeRequest):
    """
    Enhanced wait time prediction (LEGACY URL: /wait-time-enhanced)

    ⚠️ DEPRECATED: Use /api/predictions/wait-time-enhanced instead
    This endpoint is kept for backwards compatibility only.
    """
    try:
        return _predict_wait_time_enhanced_impl(request)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Enhanced wait time prediction failed: {str(e)}"
        )


@legacy_router.post("/busyness-enhanced")
async def predict_busyness_enhanced_legacy(request: BusynessRequest):
    """
    Enhanced busyness prediction (LEGACY URL: /busyness-enhanced)

    ⚠️ DEPRECATED: Use /api/predictions/busyness-enhanced instead
    This endpoint is kept for backwards compatibility only.
    """
    try:
        return _predict_busyness_enhanced_impl(request)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Enhanced busyness prediction failed: {str(e)}"
        )


@legacy_router.post("/sales-enhanced")
async def predict_sales_enhanced_legacy(request: SalesRequest):
    """
    Enhanced sales prediction (LEGACY URL: /sales-enhanced)

    ⚠️ DEPRECATED: Use /api/predictions/sales-enhanced instead
    This endpoint is kept for backwards compatibility only.
    """
    try:
        return _predict_sales_enhanced_impl(request)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Enhanced sales prediction failed: {str(e)}"
        )


@legacy_router.post("/compare-predictions")
async def compare_predictions_legacy(request: WaitTimeRequest):
    """
    Compare predictions (LEGACY URL: /compare-predictions)

    ⚠️ DEPRECATED: Use /api/predictions/compare-predictions instead
    This endpoint is kept for backwards compatibility only.
    """
    try:
        timestamp = request.timestamp or datetime.now()

        original = predict_wait_time(
            party_size=request.party_size,
            timestamp=timestamp,
            current_occupancy=request.current_occupancy,
            external_factors=None,
        )

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
