"""
Dinemetra ML Service
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
        self, party_size: int, timestamp: datetime, current_occupancy: float
    ) -> Dict:
        """
        Predict wait time for a party

        Args:
            party_size: Number of people in party
            timestamp: When they're arriving
            current_occupancy: Current table occupancy percentage (0-100)

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

        # If no model trained yet, use baseline heuristic
        if self.model is None:
            return self._baseline_prediction(party_size, hour_of_day, current_occupancy)

        # Prepare features
        features = np.array([[party_size, hour_of_day, day_of_week, current_occupancy]])

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
            },
        }

    def _baseline_prediction(
        self, party_size: int, hour: int, occupancy: float
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

        total_wait = base_wait + party_factor + peak_factor + occupancy_factor

        return {
            "predicted_wait_minutes": int(total_wait),
            "confidence": 0.6,  # Lower confidence for baseline
            "factors": {
                "party_size": party_size,
                "hour": hour,
                "occupancy_pct": occupancy,
                "note": "Using baseline prediction (model not trained yet)",
            },
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
