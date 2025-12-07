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
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === External Service Imports ===
try:
    from app.services.event_service import EventService
    from app.services.weather_service import WeatherService
except ImportError:
    logger.warning("⚠️ Could not import external services. Running in offline mode.")
    EventService = None
    WeatherService = None


class WaitTimePredictor:
    def __init__(self):
        self.model = None
        self.feature_names = []
        # Try both paths
        paths = ["models/wait_time_model.pkl", "data/models/wait_time_model.pkl"]
        for p in paths:
            if os.path.exists(p):
                self.load_model(p)
                break

        self.event_service = EventService() if EventService else None

    def load_model(self, path):
        try:
            with open(path, "rb") as f:
                data = pickle.load(f)
                if isinstance(data, dict):
                    self.model = data.get("model")
                    self.feature_names = data.get("features", [])
                else:
                    self.model = data
            logger.info(f"✓ Wait time model loaded from {path}")
        except Exception as e:
            logger.error(f"Failed to load wait time model: {e}")

    def predict(
        self,
        party_size: int,
        timestamp: datetime,
        current_occupancy: float,
        external_factors: Optional[Dict] = None,
    ) -> Dict:
        """
        Predict wait time using the Gradient Boosting model.
        """
        # 1. Base Logic (Heuristic) fallback if model fails or is missing
        base_heuristic = (
            5 + (max(0, party_size - 4) * 2) + (max(0, current_occupancy - 70) / 2)
        )

        if not self.model:
            return {
                "predicted_wait_minutes": int(base_heuristic),
                "confidence": 0.5,
                "factors": {"note": "Using baseline logic (model missing)"},
            }

        try:
            # 2. Prepare Features (Must match train_models_final.py exactly)
            # Features: ['party_size', 'hour', 'day', 'occupancy', 'busy_hour', 'high_occ', 'interaction']

            hour = timestamp.hour
            day = timestamp.weekday()

            # Interaction features
            busy_hour = 1 if hour in [18, 19, 20] else 0
            high_occ = 1 if current_occupancy > 80 else 0
            interaction = party_size * current_occupancy

            features = pd.DataFrame(
                [
                    [
                        party_size,
                        hour,
                        day,
                        current_occupancy,
                        busy_hour,
                        high_occ,
                        interaction,
                    ]
                ],
                columns=[
                    "party_size",
                    "hour",
                    "day",
                    "occupancy",
                    "busy_hour",
                    "high_occ",
                    "interaction",
                ],
            )

            # 3. Predict
            pred = self.model.predict(features)[0]

            # Clamp to realistic values (never negative)
            final_wait = max(0, int(pred))

            # Get event impact (heuristic addition)
            event_impact = 0
            if self.event_service:
                event_impact = self.event_service.calculate_impact(timestamp)

            return {
                "predicted_wait_minutes": final_wait + event_impact,
                "confidence": 0.85,  # Gradient boosting is usually confident
                "factors": {
                    "party_size": party_size,
                    "occupancy": current_occupancy,
                    "model_base": final_wait,
                    "event_add": event_impact,
                },
            }

        except Exception as e:
            logger.error(f"Wait prediction error: {e}")
            return {"predicted_wait_minutes": int(base_heuristic), "confidence": 0.5}


class BusynessPredictor:
    def __init__(self):
        self.model = None
        self.label_mapping = {0: "Slow", 1: "Moderate", 2: "Peak"}

        paths = ["models/busyness_model.pkl", "data/models/busyness_model.pkl"]
        for p in paths:
            if os.path.exists(p):
                self.load_model(p)
                break

    def load_model(self, path):
        try:
            with open(path, "rb") as f:
                data = pickle.load(f)
                if isinstance(data, dict):
                    self.model = data.get("model")
                else:
                    self.model = data
            logger.info(f"✓ Busyness model loaded from {path}")
        except Exception as e:
            logger.error(f"Failed to load busyness model: {e}")

    def predict(self, timestamp: datetime, weather: Optional[str] = None) -> Dict:
        if not self.model:
            return {"level": "Moderate", "confidence": 0.0, "note": "Model missing"}

        try:
            # Features: ['hour', 'day', 'month', 'is_weekend']
            features = pd.DataFrame(
                [
                    {
                        "hour": timestamp.hour,
                        "day": timestamp.weekday(),
                        "month": timestamp.month,
                        "is_weekend": 1 if timestamp.weekday() >= 5 else 0,
                    }
                ]
            )

            # Predict
            pred_idx = self.model.predict(features)[0]
            level = self.label_mapping.get(pred_idx, "Moderate")

            # Estimate guests based on level
            guests_map = {"Slow": 15, "Moderate": 45, "Peak": 85}

            return {
                "level": level,
                "expected_guests": guests_map.get(level, 40),
                "confidence": 0.90,
            }
        except Exception as e:
            logger.error(f"Busyness prediction error: {e}")
            return {"level": "Moderate", "confidence": 0.0}


class ItemSalesPredictor:
    def __init__(self):
        self.model = None
        self.le_item = None
        self.le_cat = None

        # Note: Training script saved to data/models/item_sales_model.pkl
        paths = ["data/models/item_sales_model.pkl", "models/item_sales_model.pkl"]
        for p in paths:
            if os.path.exists(p):
                self.load_model(p)
                break

    def load_model(self, path):
        try:
            with open(path, "rb") as f:
                data = pickle.load(f)
                self.model = data["model"]
                self.le_item = data.get("le_item")  # Changed from label_encoder_item
                self.le_cat = data.get("le_cat")  # Changed from label_encoder_category
            logger.info(f"✓ Item Sales model loaded from {path}")
        except Exception as e:
            logger.error(f"Failed to load item sales model: {e}")

    def predict_daily_sales(
        self,
        item_id: int,
        date: datetime,
        item_name: str = "Unknown",
        category: str = "Food",
    ) -> Dict:
        if not self.model:
            return {"predicted_quantity": 25, "confidence": 0.0}

        try:
            # 1. Encode Item
            try:
                item_encoded = self.le_item.transform([item_name])[0]
            except:
                # Unknown item fallback (use 0 or median)
                item_encoded = 0

            # 2. Encode Category
            try:
                cat_encoded = self.le_cat.transform([category])[0]
            except:
                cat_encoded = 0

            # 3. Features: ['item_encoded', 'cat_encoded', 'price', 'day_of_week', 'month', 'is_weekend']
            features = pd.DataFrame(
                [
                    {
                        "item_encoded": item_encoded,
                        "cat_encoded": cat_encoded,
                        "price": 12.0,  # Default price since we don't pass it in API
                        "day_of_week": date.weekday(),
                        "month": date.month,
                        "is_weekend": 1 if date.weekday() >= 5 else 0,
                    }
                ]
            )

            # 4. Predict
            pred = self.model.predict(features)[0]
            qty = max(0, int(pred))

            return {
                "item_id": item_id,
                "item_name": item_name,
                "predicted_quantity": qty,
                "confidence": 0.85,
                "date": date.strftime("%Y-%m-%d"),
            }

        except Exception as e:
            logger.error(f"Sales prediction error: {e}")
            return {"predicted_quantity": 20, "confidence": 0.0}


# Global Instances
wait_time_predictor = WaitTimePredictor()
busyness_predictor = BusynessPredictor()
item_sales_predictor = ItemSalesPredictor()


def initialize_models():
    """Called by main.py on startup"""
    pass  # Models load on init now


# Convenience Wrappers for API
def predict_wait_time(party_size, timestamp, current_occupancy, external_factors=None):
    return wait_time_predictor.predict(
        party_size, timestamp, current_occupancy, external_factors
    )


def predict_busyness(timestamp, weather=None):
    return busyness_predictor.predict(timestamp, weather)


def predict_item_sales(item_id, date, item_name="Unknown", category="Food"):
    return item_sales_predictor.predict_daily_sales(item_id, date, item_name, category)
