from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import Optional

from app.models.schemas import WaitTimePredictionRequest, WaitTimePredictionResponse 

# Import ONLY the prediction wrapper
from app.services.ml_service import predict_wait_time

router = APIRouter()

@router.post("/wait-time", response_model=WaitTimePredictionResponse)
async def predict_wait_time_endpoint(request: WaitTimePredictionRequest):
    """
    Predict wait time for a party.
    
    The ML Service automatically handles:
    - Determining seasonality (Month/Day)
    - Fetching live Weather impact
    - Fetching live Ticketmaster Event impact
    """
    try:
        # 1. Prepare the timestamp
        timestamp = request.timestamp or datetime.now()

        # 2. Call the ML Service 
        # The service will auto-fetch them if they are None.
        result = predict_wait_time(
            party_size=request.party_size,
            timestamp=timestamp,
            current_occupancy=request.current_occupancy,
            external_factors=None  # Let the service fetch the real data
        )

        # 3. Return the result
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")