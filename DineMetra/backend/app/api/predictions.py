from fastapi import APIRouter, HTTPException
from datetime import datetime
from app.models.schemas import WaitTimePredictionRequest, WaitTimePredictionResponse
from app.services.ml_service import predict_wait_time
from app.services.event_service import event_service

router = APIRouter()


@router.post("/wait-time", response_model=WaitTimePredictionResponse)
async def predict_wait_time_endpoint(request: WaitTimePredictionRequest):
    """
    Predict wait time for a party
    Automatically incorporates nearby events and weather
    """
    timestamp = request.timestamp or datetime.now()

    # Fetch external factors
    external_factors = {}

    # Get events for this date
    events = event_service.get_events_for_date(timestamp)
    if events:
        # Use the biggest/closest event
        primary_event = max(
            events, key=lambda e: e.get("event_attendance_estimated", 0)
        )
        external_factors.update(primary_event)

    # Get weather
    weather = event_service.get_weather_for_date(timestamp)
    external_factors.update(weather)

    # Make prediction
    result = predict_wait_time(
        party_size=request.party_size,
        timestamp=timestamp,
        current_occupancy=request.current_occupancy,
        external_factors=external_factors if external_factors else None,
    )

    return result
