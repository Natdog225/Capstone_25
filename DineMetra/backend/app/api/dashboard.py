"""
Dashboard API - Updated to use Enhanced Prediction Service
Integrates with your existing services + new dashboard aggregation
"""

from fastapi import APIRouter, Query
from datetime import datetime
from typing import Optional

# Import existing services
from app.services.event_service import EventService
from app.services.weather_service import WeatherService

# Import new enhanced services
from app.services.enhanced_prediction_service import enhanced_prediction_service
from app.services.dashboard_service import dashboard_service

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

# Initialize services
event_service = EventService()
weather_service = WeatherService()


# =============================================================================
# CONSOLIDATED DASHBOARD ENDPOINT
# =============================================================================


@router.get("/dashboard")
async def get_full_dashboard():
    """
    Get complete dashboard in ONE call

    Returns highlights, metrics, info sections, and user data
    """
    try:
        return {
            "highlights": dashboard_service.get_highlights(),
            "metrics": dashboard_service.get_metrics(),
            "info_sections": dashboard_service.get_info_sections(),
            "sales_chart": dashboard_service.get_sales_chart_data(period="this-week"),
            "user": {"name": "Manager", "restaurant": "Tulsa Capstone Grill"},
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {
            "error": str(e),
            "highlights": [],
            "metrics": {},
            "info_sections": {},
            "user": {},
        }


# =============================================================================
# INDIVIDUAL DASHBOARD ENDPOINTS (for flexibility)
# =============================================================================


@router.get("/highlights")
async def get_dashboard_highlights():
    """
    Returns key events for the week (Powered by Ticketmaster + Weather)
    Enhanced with detailed event and weather information
    """
    try:
        highlights = dashboard_service.get_highlights()
        return {"highlights": highlights, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        return {"highlights": [], "error": str(e)}


@router.get("/sales-chart")
async def get_sales_chart(
    week: str = Query("this-week", description="Period: this-week, last-week, custom")
):
    """
    Returns sales data with THIS WEEK vs LAST WEEK comparison
    Shows actual progression and historical comparison
    """
    try:
        # Get THIS week's data (last 7 days of data)
        this_week = dashboard_service.get_sales_chart_data(period="this-week")
        this_week_data = this_week.get('data', [])
        
        # Get LAST week's data (previous 7 days)
        last_week = dashboard_service.get_sales_chart_data(period="last-week")
        last_week_data = last_week.get('data', [])
        
        # Build comparison chart
        formatted = []
        for i in range(7):
            this_item = this_week_data[i] if i < len(this_week_data) else {'date': '', 'sales': 0}
            last_item = last_week_data[i] if i < len(last_week_data) else {'sales': 0}
            
            day_name = this_item.get('date', ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][i])
            this_sales = round(this_item.get('sales', 0), 2)
            past_sales = round(last_item.get('sales', 0), 2)
            
            formatted.append({
                'day': day_name,
                'thisWeek': this_sales,      # Current week (yellow)
                'pastData': past_sales,       # Last week (blue)
                'actual': this_sales          # Same as thisWeek (green) - shows actual vs predicted later
            })
        
        return formatted
        
    except Exception as e:
        logger.error(f"Sales chart error: {e}", exc_info=True)
        return []


@router.get("/metrics")
async def get_metrics_grid():
    """
    Returns top sellers, KPI summaries, and purchasing estimates
    Enhanced with ML-powered purchasing predictions
    """
    try:
        metrics = dashboard_service.get_metrics()
        return {
            "categories": metrics.get("categories", []),
            "summaries": metrics.get("summaries", []),
            "purchasing": metrics.get("purchasing", []),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {"categories": [], "summaries": [], "purchasing": [], "error": str(e)}


@router.get("/info-sections")
async def get_info_sections():
    """
    Aggregates Weather, Events, Labor, and Historical data
    Uses real weather.gov + Ticketmaster data
    """
    try:
        info = dashboard_service.get_info_sections()
        return {
            "events": info.get("events", []),
            "weather": info.get("weather", {}),
            "labor": info.get("labor", {}),
            "historical": info.get("historical", {}),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {
            "events": [],
            "weather": {},
            "labor": {},
            "historical": {},
            "error": str(e),
        }


# =============================================================================
# ENHANCED PREDICTION ENDPOINTS (with detailed factors)
# =============================================================================


@router.post("/predictions/wait-time-enhanced")
async def predict_wait_time_enhanced(
    party_size: int = Query(..., ge=1, le=20),
    current_occupancy: float = Query(..., ge=0, le=100),
    timestamp: Optional[str] = Query(None, description="ISO format datetime"),
):
    """
    Enhanced wait time prediction with detailed factor breakdown

    Shows WHY the prediction is what it is:
    - Weather impact
    - Event impact
    - Time/occupancy factors
    - Historical comparison
    """
    try:
        target_time = datetime.fromisoformat(timestamp) if timestamp else None

        result = enhanced_prediction_service.predict_wait_time_enhanced(
            party_size=party_size,
            current_occupancy=current_occupancy,
            timestamp=target_time,
        )

        return result

    except Exception as e:
        return {"predicted_wait_minutes": 15, "error": str(e), "factors": {}}


@router.get("/predictions/busyness-enhanced")
async def predict_busyness_enhanced(
    timestamp: Optional[str] = Query(None, description="ISO format datetime")
):
    """
    Enhanced busyness prediction with detailed factor breakdown

    Shows:
    - Expected busyness level
    - Weather impact
    - Nearby events
    - Staffing recommendations
    """
    try:
        target_time = datetime.fromisoformat(timestamp) if timestamp else None

        result = enhanced_prediction_service.predict_busyness_enhanced(
            timestamp=target_time
        )

        return result

    except Exception as e:
        return {"level": "Moderate", "error": str(e), "factors": {}}


@router.get("/predictions/sales-enhanced")
async def predict_sales_enhanced(
    item_id: int = Query(..., description="Menu item ID"),
    target_date: Optional[str] = Query(None, description="ISO format date"),
    item_name: str = Query("Unknown", description="Item name"),
    category: str = Query("Entrees", description="Item category"),
):
    """
    Enhanced sales prediction with detailed factor breakdown

    Shows:
    - Predicted quantity
    - Confidence with margin
    - Weather sensitivity
    - Event impact
    - Purchasing recommendation
    """
    try:
        target = datetime.fromisoformat(target_date) if target_date else None

        result = enhanced_prediction_service.predict_sales_enhanced(
            item_id=item_id, target_date=target, item_name=item_name, category=category
        )

        return result

    except Exception as e:
        return {
            "item_id": item_id,
            "predicted_quantity": 0,
            "error": str(e),
            "factors": {},
        }


# =============================================================================
# USER PROFILE
# =============================================================================


@router.get("/user-profile")
async def get_user_profile():
    """Get user profile information"""
    # TODO: Implement actual auth
    return {
        "name": "Manager",
        "restaurant": "Tulsa Capstone Grill",
        "email": "manager@tulsagrill.com",
    }


# =============================================================================
# FEEDBACK ENDPOINT (for model improvement)
# =============================================================================


@router.post("/feedback")
async def submit_feedback(
    prediction_type: str,
    prediction_id: str,
    actual_value: float,
    notes: Optional[str] = None,
):
    """
    Submit feedback on prediction accuracy

    This data can be used to retrain and improve models
    """
    try:
        feedback_record = {
            "prediction_type": prediction_type,
            "prediction_id": prediction_id,
            "actual_value": actual_value,
            "notes": notes,
            "timestamp": datetime.now().isoformat(),
        }

        # TODO: Store in database for model retraining
        # For now, just log it
        print(f"Feedback received: {feedback_record}")

        return {
            "success": True,
            "message": "Thank you for your feedback!",
            "feedback_id": f"fb_{datetime.now().timestamp()}",
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


# =============================================================================
# HEALTH CHECK
# =============================================================================


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test services
        weather_ok = weather_service.grid_info is not None
        events_ok = event_service.ticketmaster_key is not None

        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "weather": "operational" if weather_ok else "degraded",
                "events": "operational" if events_ok else "no_api_key",
                "predictions": "operational",
                "dashboard": "operational",
            },
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
