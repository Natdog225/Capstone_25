"""
Pydantic models for API request/response validation
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict


class WaitTimePredictionRequest(BaseModel):
    party_size: int = Field(..., ge=1, le=20, description="Number of people in party")
    timestamp: Optional[datetime] = Field(
        default=None, description="When they're arriving (defaults to now)"
    )
    current_occupancy: Optional[float] = Field(
        default=50.0, ge=0, le=100, description="Current occupancy percentage"
    )


class WaitTimePredictionResponse(BaseModel):
    predicted_wait_minutes: int
    confidence: float
    factors: Dict


class BusynessPredictionRequest(BaseModel):
    timestamp: Optional[datetime] = Field(default=None)
    weather: Optional[str] = None


class BusynessPredictionResponse(BaseModel):
    level: str  # "slow", "moderate", "peak"
    confidence: float
    expected_guests: int
    timestamp: str
