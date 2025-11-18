"""
DineMetra ML Service
Handles all machine learning predictions for wait times, busyness, and item sales
"""

import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
import pickle
import os


class WaitTimePredictor:
    """
    Predicts restaurant wait times based on:
    - Party size
    - Time of day
    - Day of week
    - Current occupancy
    - Historical patterns
    """

    def __init__(self):
        self.model = None
        self.model_path = "models/wait_time_model.pkl"

    def train(self, training_data: pd.DataFrame):
        """
        Train the wait time prediction model

        Expected columns:
        - party_size
        - hour_of_day
        - day_of_week
        - current_occupancy_pct
        - actual_wait_minutes (target)
        """
        from sklearn.ensemble import RandomForestRegressor

        # Feature engineering
        X = training_data[
            ["party_size", "hour_of_day", "day_of_week", "current_occupancy_pct"]
        ]
        y = training_data["actual_wait_minutes"]

        # Train model (start simple!)
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X, y)

        # Save model
        os.makedirs("models", exist_ok=True)
        with open(self.model_path, "wb") as f:
            pickle.dump(self.model, f)

        print(f"✓ Model trained and saved to {self.model_path}")

    def load_model(self):
        """Load pre-trained model from disk"""
        if os.path.exists(self.model_path):
            with open(self.model_path, "rb") as f:
                self.model = pickle.load(f)
            print("✓ Model loaded successfully")
        else:
            print("⚠ No trained model found. Using baseline prediction.")
            self.model = None

    def predict(
        self,
        party_size: int,
        timestamp: datetime,
        current_occupancy: float,
        external_factors: Optional[Dict] = None,
    ) -> Dict:
        """
        Predict wait time for a party

        Args:
            party_size: Number of people in party
            timestamp: When they're arriving
            current_occupancy: Current table occupancy percentage (0-100)
            external_factors: Dict with weather, events, holidays

        Returns:
            {
                "predicted_wait_minutes": int,
                "confidence": float (0-1),
                "factors": dict of contributing factors
            }
        """
        # Extract time features
        hour_of_day = timestamp.hour
        day_of_week = timestamp.weekday()

        # Extract external factors if provided
        event_impact = 0
        weather_impact = 0
        if external_factors:
            event_impact = self._calculate_event_impact(external_factors, timestamp)
            weather_impact = self._calculate_weather_impact(external_factors)

        # If no model trained yet, use baseline heuristic
        if self.model is None:
            return self._baseline_prediction(
                party_size,
                hour_of_day,
                current_occupancy,
                event_impact,
                weather_impact,
                external_factors,
            )

        # Prepare features (add event and weather features)
        features = np.array(
            [
                [
                    party_size,
                    hour_of_day,
                    day_of_week,
                    current_occupancy,
                    event_impact,
                    weather_impact,
                ]
            ]
        )

        # Make prediction
        predicted_minutes = int(self.model.predict(features)[0])

        # Calculate confidence (simplified for now)
        confidence = self._calculate_confidence(party_size, current_occupancy)

        return {
            "predicted_wait_minutes": max(0, predicted_minutes),  # Never negative
            "confidence": confidence,
            "factors": {
                "party_size": party_size,
                "hour": hour_of_day,
                "day_of_week": day_of_week,
                "occupancy_pct": current_occupancy,
                "event_impact": event_impact,
                "weather_impact": weather_impact,
                "external_factors": external_factors,
            },
        }

    def _baseline_prediction(
        self,
        party_size: int,
        hour: int,
        occupancy: float,
        event_impact: float = 0,
        weather_impact: float = 0,
        external_factors: Optional[Dict] = None,
    ) -> Dict:
        """
        Simple rule-based prediction when no ML model is available
        This is your Week 1 fallback!
        """
        base_wait = 5  # Base 5 minutes

        # Party size factor (larger parties wait longer)
        party_factor = (party_size - 1) * 3

        # Peak hours factor (dinner rush = longer waits)
        peak_hours = [11, 12, 13, 17, 18, 19, 20]
        peak_factor = 10 if hour in peak_hours else 0

        # Occupancy factor (busier = longer wait)
        occupancy_factor = occupancy * 0.3

        # Add event impact
        # Add weather impact

        total_wait = (
            base_wait
            + party_factor
            + peak_factor
            + occupancy_factor
            + event_impact
            + weather_impact
        )

        factors = {
            "party_size": party_size,
            "hour": hour,
            "occupancy_pct": occupancy,
            "event_impact_minutes": event_impact,
            "weather_impact_minutes": weather_impact,
            "note": "Using baseline prediction (model not trained yet)",
        }

        if external_factors:
            factors["external_factors"] = external_factors

        return {
            "predicted_wait_minutes": int(total_wait),
            "confidence": 0.6,  # Lower confidence for baseline
            "factors": factors,
        }

    def _calculate_confidence(self, party_size: int, occupancy: float) -> float:
        """
        Calculate prediction confidence score
        Lower confidence for edge cases
        """
        confidence = 0.85

        # Reduce confidence for very large parties (less training data)
        if party_size > 8:
            confidence -= 0.15

        # Reduce confidence for very high/low occupancy (edge cases)
        if occupancy < 10 or occupancy > 95:
            confidence -= 0.1

        return max(0.5, min(1.0, confidence))

    def _calculate_event_impact(
        self, external_factors: Dict, timestamp: datetime
    ) -> float:
        """
        Calculate how much a nearby event will increase wait times

        Returns: Additional wait time in minutes (0-30)
        """
        if not external_factors or "event_name" not in external_factors:
            return 0

        # Base impact from event type
        event_type = external_factors.get("event_type", "").lower()
        type_impact = {
            "sports": 15,  # Thunder game = big impact
            "concert": 12,  # Concert = moderate impact
            "festival": 10,  # Festival = moderate impact
            "conference": 5,  # Conference = small impact
        }.get(event_type, 0)

        # Adjust by attendance
        attendance = external_factors.get("event_attendance_estimated", 0)
        if attendance > 15000:
            attendance_multiplier = 1.5  # Massive event
        elif attendance > 5000:
            attendance_multiplier = 1.2  # Large event
        elif attendance > 1000:
            attendance_multiplier = 1.0  # Medium event
        else:
            attendance_multiplier = 0.5  # Small event

        # Adjust by distance from restaurant
        distance_miles = external_factors.get("event_distance_miles", 10)
        if distance_miles < 0.5:
            distance_multiplier = 1.5  # Right next door!
        elif distance_miles < 1:
            distance_multiplier = 1.2  # Walking distance
        elif distance_miles < 3:
            distance_multiplier = 1.0  # Short drive
        elif distance_miles < 5:
            distance_multiplier = 0.5  # Nearby
        else:
            distance_multiplier = 0.2  # Far away

        # Adjust by time proximity to event
        # Events impact 1-2 hours before and after
        event_time = external_factors.get("event_time")  # Should be a datetime
        if event_time:
            hours_until_event = (event_time - timestamp).total_seconds() / 3600
            if -2 <= hours_until_event <= 2:
                time_multiplier = 1.0  # During event window
            elif -3 <= hours_until_event <= 3:
                time_multiplier = 0.5  # Near event time
            else:
                time_multiplier = 0.1  # Event is far away in time
        else:
            time_multiplier = 1.0  # Assume it's during event time

        total_impact = (
            type_impact * attendance_multiplier * distance_multiplier * time_multiplier
        )

        return min(30, max(0, total_impact))  # Cap at 30 minutes, minimum 0

    def _calculate_weather_impact(self, external_factors: Dict) -> float:
        """
        Calculate how weather affects wait times

        Returns: Impact on wait time in minutes (-5 to +10)
        """
        if not external_factors:
            return 0

        weather = external_factors.get("weather_condition", "").lower()
        precipitation = external_factors.get("precipitation_inches", 0)
        temp = external_factors.get("temperature_high_f", 70)

        impact = 0

        # Rain/snow drives people indoors (increases wait)
        if weather in ["rainy", "snowy", "stormy"]:
            impact += 5 + (precipitation * 2)  # More rain = more impact

        # Extreme temperatures drive people indoors
        if temp < 32 or temp > 95:
            impact += 3  # Too cold or too hot

        # Nice weather reduces indoor dining (negative impact)
        if weather in ["sunny", "clear"] and 65 <= temp <= 85:
            impact -= 5  # People want to be outside

        return max(-5, min(10, impact))  # Cap between -5 and +10 minutes


class BusynessPredictor:
    """
    Predicts restaurant busyness level (slow/moderate/peak)
    """

    def __init__(self):
        self.model = None

    def predict(self, timestamp: datetime, weather: Optional[str] = None) -> Dict:
        """
        Predict busyness level

        Returns:
            {
                "level": "slow" | "moderate" | "peak",
                "confidence": float,
                "expected_guests": int
            }
        """
        hour = timestamp.hour
        day_of_week = timestamp.weekday()

        # Simple rule-based prediction for Week 1
        if hour in [11, 12, 13, 17, 18, 19, 20]:
            level = "peak"
            expected_guests = 80
        elif hour in [10, 14, 15, 16, 21]:
            level = "moderate"
            expected_guests = 40
        else:
            level = "slow"
            expected_guests = 15

        # Weekend boost
        if day_of_week in [5, 6]:  # Saturday, Sunday
            expected_guests = int(expected_guests * 1.3)

        return {
            "level": level,
            "confidence": 0.75,
            "expected_guests": expected_guests,
            "timestamp": timestamp.isoformat(),
        }


class ItemSalesPredictor:
    """
    Predicts menu item sales for inventory planning
    """

    def __init__(self):
        self.model = None

    def predict_daily_sales(self, item_id: int, date: datetime) -> Dict:
        """
        Predict how many of an item will be ordered on a given day

        Returns:
            {
                "item_id": int,
                "predicted_quantity": int,
                "confidence": float
            }
        """
        # Placeholder for Week 2-3 implementation
        day_of_week = date.weekday()

        # Weekend items sell more
        base_quantity = 50
        if day_of_week in [5, 6]:
            base_quantity = int(base_quantity * 1.4)

        return {
            "item_id": item_id,
            "predicted_quantity": base_quantity,
            "confidence": 0.7,
            "date": date.date().isoformat(),
        }


# Global instances (loaded once on server start)
wait_time_predictor = WaitTimePredictor()
busyness_predictor = BusynessPredictor()
item_sales_predictor = ItemSalesPredictor()


def initialize_models():
    """
    Load all models on server startup
    Call this from main.py
    """
    print("🤖 Initializing ML models...")
    wait_time_predictor.load_model()
    print("✓ ML models ready")


# API-friendly wrapper functions
def predict_wait_time(
    party_size: int, timestamp: datetime, current_occupancy: float
) -> Dict:
    """Convenience function for API endpoints"""
    return wait_time_predictor.predict(party_size, timestamp, current_occupancy)


def predict_busyness(timestamp: datetime, weather: Optional[str] = None) -> Dict:
    """Convenience function for API endpoints"""
    return busyness_predictor.predict(timestamp, weather)


def predict_item_sales(item_id: int, date: datetime) -> Dict:
    """Convenience function for API endpoints"""
    return item_sales_predictor.predict_daily_sales(item_id, date)
