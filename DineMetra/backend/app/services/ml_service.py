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

        # This must match train_models.py EXACTLY
        self.feature_columns = [
            "party_size",
            "hour_of_day",
            "day_of_week",
            "current_table_occupancy_pct",
            "current_party_count",
            "is_weekend",
            "is_peak_hour",
            "is_lunch",
            "is_dinner",
            "occupancy_low",
            "occupancy_high",
            "party_small",
            "party_large",
        ]

    def load_model(self):
        """Load pre-trained model from disk"""
        if os.path.exists(self.model_path):
            with open(self.model_path, "rb") as f:
                data = pickle.load(f)
                self.model = data["model"]
                self.metadata = data.get("metadata", {})
            print(f"✓ Wait time model loaded")
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
        Predict wait time with full feature engineering
        """
        # 1. Extract Base Features
        hour = timestamp.hour
        day = timestamp.weekday()

        # 2. Engineer Derived Features (Match train_models.py logic)
        # This is the part your previous code was missing!
        is_weekend = 1 if day in [5, 6] else 0
        is_peak = 1 if hour in [11, 12, 13, 17, 18, 19, 20] else 0
        is_lunch = 1 if hour in [11, 12, 13] else 0
        is_dinner = 1 if hour in [17, 18, 19, 20] else 0

        occupancy_low = 1 if current_occupancy < 50 else 0
        occupancy_high = 1 if current_occupancy >= 75 else 0

        party_small = 1 if party_size <= 2 else 0
        party_large = 1 if party_size >= 6 else 0

        # Estimation: If we don't have exact party count, estimate from occupancy
        # Assuming ~30 tables max capacity
        est_party_count = int((current_occupancy / 100) * 30)

        # 3. Create Feature DataFrame (Must have 13 columns)
        features = pd.DataFrame(
            [
                [
                    party_size,
                    hour,
                    day,
                    current_occupancy,
                    est_party_count,
                    is_weekend,
                    is_peak,
                    is_lunch,
                    is_dinner,
                    occupancy_low,
                    occupancy_high,
                    party_small,
                    party_large,
                ]
            ],
            columns=self.feature_columns,
        )

        # 4. Predict
        if self.model is None:
            return self._baseline_prediction(party_size, hour, current_occupancy)

        try:
            predicted_minutes = int(self.model.predict(features)[0])
            confidence = self._calculate_confidence(party_size, current_occupancy)

            return {
                "predicted_wait_minutes": max(0, predicted_minutes),
                "confidence": confidence,
                "factors": {
                    "party_size": party_size,
                    "occupancy": current_occupancy,
                    "is_peak": bool(is_peak),
                    "is_weekend": bool(is_weekend),
                },
            }
        except Exception as e:
            print(f"Prediction Error: {e}")
            return self._baseline_prediction(party_size, hour, current_occupancy)

    def _baseline_prediction(self, party_size, hour, occupancy, *args):
        """Fallback if model fails or isn't loaded"""
        base = 10
        if hour in [18, 19]:
            base += 15
        if occupancy > 80:
            base += 10
        if party_size > 4:
            base += 5
        return {
            "predicted_wait_minutes": base,
            "confidence": 0.5,
            "factors": {"note": "Using baseline logic"},
        }

    def _calculate_confidence(self, party_size, occupancy):
        confidence = 0.85
        if party_size > 8:
            confidence -= 0.15
        if occupancy > 95:
            confidence -= 0.1
        return max(0.5, min(1.0, confidence))

    # (Note: I removed the train() method here because you should use
    # scripts/train_dummy_model.py or scripts/train_models.py instead.
    # Keeping training logic separate from prediction logic is cleaner.)


class BusynessPredictor:
    def __init__(self):
        self.model = None

    def predict(self, timestamp, weather=None):
        # Placeholder for now
        return {"level": "moderate", "expected_guests": 40, "confidence": 0.8}


class ItemSalesPredictor:
    def __init__(self):
        self.model = None

    def predict_daily_sales(self, item_id, date):
        # Placeholder for now
        return {"predicted_quantity": 50, "confidence": 0.7}


# Global instances
wait_time_predictor = WaitTimePredictor()
busyness_predictor = BusynessPredictor()
item_sales_predictor = ItemSalesPredictor()


def initialize_models():
    print("🤖 Initializing ML models...")
    wait_time_predictor.load_model()
    print("✓ ML models ready")


# API Wrappers
def predict_wait_time(
    party_size: int,
    timestamp: datetime,
    current_occupancy: float,
    external_factors: Optional[Dict] = None,
) -> Dict:
    """Convenience function for API endpoints"""
    return wait_time_predictor.predict(
        party_size, timestamp, current_occupancy, external_factors
    )


def predict_busyness(timestamp, weather=None):
    return busyness_predictor.predict(timestamp, weather)


def predict_item_sales(item_id, date):
    return item_sales_predictor.predict_daily_sales(item_id, date)
