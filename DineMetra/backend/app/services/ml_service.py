"""
Dinemetra ML Service (Hybrid Production Version)
Combines High-Accuracy Baseline Models with Event-Aware Heuristics.
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
        # 1. Base Logic Fallback
        base_heuristic = (
            5 + (max(0, party_size - 4) * 2) + (max(0, current_occupancy - 70) / 2)
        )

        if not self.model:
            return {"predicted_wait_minutes": int(base_heuristic), "confidence": 0.5}

        try:
            # 2. ML Prediction (Baseline)
            hour = timestamp.hour
            day = timestamp.weekday()
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

            pred = self.model.predict(features)[0]
            final_wait = max(0, int(pred))

            # 3. Event Impact (Heuristic)
            event_impact = 0
            if self.event_service:
                try:
                    event_impact = self.event_service.calculate_impact(timestamp)
                except:
                    event_impact = 0

            return {
                "predicted_wait_minutes": final_wait + event_impact,
                "confidence": 0.85,
                "factors": {
                    "party_size": party_size,
                    "occupancy": current_occupancy,
                    "base_wait": final_wait,
                    "event_impact": event_impact,
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
            return {"level": "Moderate", "confidence": 0.0}

        try:
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

            pred_idx = self.model.predict(features)[0]
            level = self.label_mapping.get(pred_idx, "Moderate")
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
        self.feature_names = []

        paths = ["data/models/item_sales_model.pkl", "models/item_sales_model.pkl"]
        for p in paths:
            if os.path.exists(p):
                self.load_model(p)
                break

        # Connect to Event Service for the Bonus Logic
        self.event_service = EventService() if EventService else None

    def load_model(self, path):
        try:
            with open(path, "rb") as f:
                data = pickle.load(f)
                self.model = data["model"]
                self.le_item = data.get("le_item") or data.get("label_encoder_item")
                self.le_cat = data.get("le_cat") or data.get("label_encoder_category")
                self.feature_names = data.get("features", []) or data.get(
                    "feature_cols", []
                )
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
            # 1. Encode Inputs
            try:
                item_encoded = self.le_item.transform([item_name])[0]
            except:
                item_encoded = 0
            try:
                cat_encoded = self.le_cat.transform([category])[0]
            except:
                cat_encoded = 0

            # 2. Build Features (Standard 6-feature set from train_models_final.py)
            input_data = {
                "item_encoded": item_encoded,
                "cat_encoded": cat_encoded,
                "price": 12.0,
                "day_of_week": date.weekday(),
                "month": date.month,
                "is_weekend": 1 if date.weekday() >= 5 else 0,
            }

            # Map to feature names expected by the model
            ordered_features = [input_data.get(f, 0) for f in self.feature_names]
            features_df = pd.DataFrame([ordered_features], columns=self.feature_names)

            # 3. Base Prediction (Historical Trend)
            pred = self.model.predict(features_df)[0]
            qty = max(0, int(pred))

            # 4. === EVENT BONUS LOGIC ===
            # Since our historical data didn't capture events, we add the impact here.
            event_multiplier = 1.0
            event_name = None

            if self.event_service:
                try:
                    events = self.event_service.get_events_for_date(
                        date, use_cache_only=True
                    )
                    if events:
                        # Find biggest event
                        top_event = max(
                            events, key=lambda x: x.get("attendance_estimated", 0)
                        )
                        attendance = top_event.get("attendance_estimated", 0)

                        if attendance > 10000:
                            event_multiplier = 1.25  # +25% for huge events
                            event_name = "Huge Event"
                        elif attendance > 5000:
                            event_multiplier = 1.15  # +15% for big events
                            event_name = "Big Event"
                        elif attendance > 1000:
                            event_multiplier = 1.05  # +5% for local events
                            event_name = "Local Event"
                except Exception as e:
                    logger.warning(f"Event check failed: {e}")

            # Apply Bonus
            adjusted_qty = int(qty * event_multiplier)

            return {
                "item_id": item_id,
                "item_name": item_name,
                "predicted_quantity": adjusted_qty,
                "confidence": 0.85,
                "date": date.strftime("%Y-%m-%d"),
                "factors": {
                    "base_prediction": qty,
                    "event_multiplier": event_multiplier,
                    "event_impact": "Positive" if event_multiplier > 1.0 else "Neutral",
                },
            }

        except Exception as e:
            logger.error(f"Sales prediction error: {e}")
            return {"predicted_quantity": 20, "confidence": 0.0}


# Global Instances
wait_time_predictor = WaitTimePredictor()
busyness_predictor = BusynessPredictor()
item_sales_predictor = ItemSalesPredictor()


def initialize_models():
    pass


# API Wrappers
def predict_wait_time(party_size, timestamp, current_occupancy, external_factors=None):
    return wait_time_predictor.predict(
        party_size, timestamp, current_occupancy, external_factors
    )


def predict_busyness(timestamp, weather=None):
    return busyness_predictor.predict(timestamp, weather)


def predict_item_sales(item_id, date, item_name="Unknown", category="Food"):
    return item_sales_predictor.predict_daily_sales(item_id, date, item_name, category)
