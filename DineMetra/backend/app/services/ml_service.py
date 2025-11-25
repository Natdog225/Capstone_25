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
            "month",
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
        month = timestamp.month

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
                    month,
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
                    "month": month,
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


class BusynessPredictor:
    """
    Predicts restaurant busyness level (slow/moderate/peak)
    based on Time, Month, and Weather.
    """

    def __init__(self):
        self.model = None
        self.model_path = "models/busyness_model.pkl"
        self.label_mapping = {0: "slow", 1: "moderate", 2: "peak"}

        # Must match training_report.json EXACTLY
        self.feature_columns = [
            "hour",
            "day_of_week",
            "month",
            "avg_party_size",
            "is_weekend",
            "is_lunch",
            "is_dinner",
            "is_peak_hour",
            "is_holiday",
            "weather_cloudy",
            "weather_rainy",
            "weather_snowy",
            "weather_sunny",
        ]
        self.load_model()  # Load immediately on init

    def load_model(self):
        if os.path.exists(self.model_path):
            with open(self.model_path, "rb") as f:
                data = pickle.load(f)
                self.model = data["model"]
                self.label_mapping = {
                    v: k for k, v in data.get("label_mapping", {}).items()
                }
            print(f"✓ Busyness model loaded")
        else:
            print("⚠ No Busyness model found.")

    def predict(self, timestamp: datetime, weather: Optional[str] = None) -> Dict:
        if self.model is None:
            return {"level": "moderate", "confidence": 0.0, "note": "Model not loaded"}

        # 1. Base Time Features
        hour = timestamp.hour
        day = timestamp.weekday()
        month = timestamp.month

        # 2. Derived Features
        is_weekend = 1 if day in [5, 6] else 0
        is_peak = 1 if hour in [11, 12, 13, 17, 18, 19, 20] else 0
        is_lunch = 1 if hour in [11, 12, 13] else 0
        is_dinner = 1 if hour in [17, 18, 19, 20] else 0
        # Holiday: Simplified check (could use external service in future)
        is_holiday = 0

        # 3. Weather Features (One-Hot Encoding)
        # Default to all 0
        w_cloudy = w_rainy = w_snowy = w_sunny = 0

        if weather:
            w = weather.lower()
            if "rain" in w or "drizzle" in w or "storm" in w:
                w_rainy = 1
            elif "snow" in w or "ice" in w:
                w_snowy = 1
            elif "cloud" in w or "overcast" in w:
                w_cloudy = 1
            elif "sun" in w or "clear" in w:
                w_sunny = 1

        # 4. Avg Party Size (Future prediction requires an estimate)
        # We use the historical average (approx 2.4 from your data)
        avg_party_size = 2.4

        # 5. Create Feature DataFrame
        features = pd.DataFrame(
            [
                [
                    hour,
                    day,
                    month,
                    avg_party_size,
                    is_weekend,
                    is_lunch,
                    is_dinner,
                    is_peak,
                    is_holiday,
                    w_cloudy,
                    w_rainy,
                    w_snowy,
                    w_sunny,
                ]
            ],
            columns=self.feature_columns,
        )

        try:
            # Predict
            prediction_idx = self.model.predict(features)[0]
            level = self.label_mapping.get(prediction_idx, "moderate")

            # Estimate guests based on level (heuristic for now)
            guests_map = {"slow": 15, "moderate": 45, "peak": 85}

            return {
                "level": level,
                "confidence": 0.85,
                "expected_guests": guests_map.get(level, 40),
                "timestamp": timestamp.isoformat(),
            }
        except Exception as e:
            print(f"Busyness Prediction Error: {e}")
            return {"level": "moderate", "expected_guests": 40}


class ItemSalesPredictor:
    """
    Predicts menu item sales for inventory planning.
    """

    def __init__(self):
        self.model = None
        self.model_path = "models/item_sales_model.pkl"
        self.item_avgs = {}

        self.feature_columns = [
            "day_of_week",
            "month",
            "is_weekend",
            "is_holiday",
            "historical_avg_sales",
            "category_Alcohol",
            "category_Appetizers",
            "category_Beverages",
            "category_Desserts",
            "category_Entrees",
            "category_Salads",
            "category_Sides",
        ]
        self.load_model()

    def load_model(self):
        if os.path.exists(self.model_path):
            with open(self.model_path, "rb") as f:
                data = pickle.load(f)
                self.model = data["model"]
                self.item_avgs = data.get("item_avg_sales", {})
            print(f"✓ Item Sales model loaded")
        else:
            print("⚠ No Item Sales model found.")

    def predict_daily_sales(
        self,
        item_id: int,
        date: datetime,
        item_name: str = "Unknown",
        category: str = "Entrees",
    ) -> Dict:
        if self.model is None:
            return {"predicted_quantity": 50, "confidence": 0.0}

        # 1. Time Features
        day = date.weekday()
        month = date.month
        is_weekend = 1 if day in [5, 6] else 0
        is_holiday = 0

        # 2. Item Features
        # Try to look up historical avg, otherwise default to median (~20)
        hist_avg = self.item_avgs.get(item_name, 20.0)

        # 3. Category One-Hot Encoding
        cat_features = {
            "category_Alcohol": 0,
            "category_Appetizers": 0,
            "category_Beverages": 0,
            "category_Desserts": 0,
            "category_Entrees": 0,
            "category_Salads": 0,
            "category_Sides": 0,
        }

        # Simple mapping or fallback
        cat_key = f"category_{category}"
        if cat_key in cat_features:
            cat_features[cat_key] = 1
        else:
            cat_features["category_Entrees"] = 1  # Fallback

        # 4. Construct Vector
        features_list = [day, month, is_weekend, is_holiday, hist_avg]
        # Add category flags in correct order
        for col in self.feature_columns[5:]:
            features_list.append(cat_features.get(col, 0))

        features = pd.DataFrame([features_list], columns=self.feature_columns)

        try:
            qty = int(self.model.predict(features)[0])
            return {
                "item_id": item_id,
                "predicted_quantity": max(0, qty),
                "confidence": 0.75,
                "date": date.date().isoformat(),
            }
        except Exception as e:
            print(f"Sales Prediction Error: {e}")
            return {"predicted_quantity": 50, "confidence": 0.0}


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
