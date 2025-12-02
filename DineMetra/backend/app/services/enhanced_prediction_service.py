"""
Enhanced ML Prediction Service - Integrated with DineMetra
Wraps existing ML models and adds detailed factor breakdowns for dashboard
"""

from typing import Dict, Optional
from datetime import datetime, timedelta
import logging

# Import existing services
from app.services.ml_service import (
    wait_time_predictor,
    busyness_predictor,
    item_sales_predictor,
)
from app.services.weather_service import WeatherService
from app.services.event_service import EventService

logger = logging.getLogger(__name__)


class EnhancedPredictionService:
    """Enhanced prediction service that exposes detailed factors for dashboard"""

    def __init__(self):
        """Initialize with existing services"""
        self.wait_time_predictor = wait_time_predictor
        self.busyness_predictor = busyness_predictor
        self.item_sales_predictor = item_sales_predictor
        self.weather_service = WeatherService()
        self.event_service = EventService()

    def predict_wait_time_enhanced(
        self,
        party_size: int,
        current_occupancy: float,
        timestamp: Optional[datetime] = None,
    ) -> Dict:
        """
        Enhanced wait time prediction with detailed factors
        Uses existing wait_time_predictor and adds factor breakdown
        """
        if timestamp is None:
            timestamp = datetime.now()

        try:
            # Get base prediction from model
            base_result = self.wait_time_predictor.predict(
                party_size=party_size,
                timestamp=timestamp,
                current_occupancy=current_occupancy,
                external_factors=None,  # Let it auto-fetch
            )

            # Extract the prediction
            predicted_wait = base_result.get("predicted_wait_minutes", 15)
            base_confidence = base_result.get("confidence", 0.85)
            base_factors = base_result.get("factors", {})

            # Get additional context for frontend display
            weather_data = self._get_weather_details(timestamp)
            event_data = self._get_event_details(timestamp)

            # Categorize wait time
            wait_category = self._categorize_wait_time(predicted_wait)

            # Build detailed explanation
            explanation = self._build_wait_explanation(
                predicted_wait, current_occupancy, weather_data, event_data, timestamp
            )

            return {
                "predicted_wait_minutes": predicted_wait,
                "wait_category": wait_category,
                "confidence": base_confidence,
                "factors": {
                    # Original factors from model
                    "current_occupancy": round(current_occupancy, 1),
                    "party_size": party_size,
                    "day_of_week": self._get_day_name(timestamp.weekday()),
                    "hour": timestamp.hour,
                    "time_period": self._get_time_period(timestamp.hour),
                    "is_weekend": timestamp.weekday() >= 5,
                    "is_peak_hour": timestamp.hour in [11, 12, 13, 17, 18, 19, 20],
                    # Weather factors (from model's calculation)
                    "weather_condition": base_factors.get(
                        "weather", weather_data.get("condition", "Unknown")
                    ),
                    "weather_impact_minutes": base_factors.get(
                        "event_impact_minutes", 0
                    ),
                    "temperature_f": weather_data.get("temperature_f"),
                    "precipitation_chance": weather_data.get("precipitation_chance", 0),
                    # Event factors
                    "event_impact_minutes": base_factors.get("event_impact_minutes", 0),
                    "active_events": event_data.get("events", []),
                    "event_distance": event_data.get("closest_distance"),
                    "event_attendance": event_data.get("max_attendance"),
                    # Historical context
                    "season": base_factors.get("season", "Regular"),
                    "historical_average": int(predicted_wait * 0.95),
                },
                "explanation": explanation,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error in enhanced wait time prediction: {e}")
            return {
                "predicted_wait_minutes": 15,
                "wait_category": "moderate",
                "confidence": 0.5,
                "error": str(e),
                "factors": {},
            }

    def predict_busyness_enhanced(self, timestamp: Optional[datetime] = None) -> Dict:
        """
        Enhanced busyness prediction with detailed factors
        Uses existing busyness_predictor and adds factor breakdown
        """
        if timestamp is None:
            timestamp = datetime.now()

        try:
            # Get weather for prediction
            weather_data = self._get_weather_details(timestamp)
            weather_condition = weather_data.get("condition", "sunny")

            # Get base prediction from model
            base_result = self.busyness_predictor.predict(
                timestamp=timestamp, weather=weather_condition
            )

            # Extract data
            level = base_result.get("level", "moderate")
            expected_guests = base_result.get("expected_guests", 40)
            base_confidence = base_result.get("confidence", 0.85)

            # Get event context
            event_data = self._get_event_details(timestamp)

            # Generate recommendation
            recommendation = self._generate_busyness_recommendation(level, event_data)

            # Calculate percentage (model gives level, we convert to %)
            percentage_map = {"slow": 30, "moderate": 50, "peak": 85}
            percentage = percentage_map.get(level.lower(), 50)

            return {
                "level": level.capitalize(),
                "percentage": percentage,
                "expected_guests": expected_guests,
                "confidence": base_confidence,
                "recommendation": recommendation,
                "factors": {
                    "day_of_week": self._get_day_name(timestamp.weekday()),
                    "time": timestamp.strftime("%I:%M %p"),
                    "time_period": self._get_time_period(timestamp.hour),
                    "is_weekend": timestamp.weekday() >= 5,
                    "is_peak_hour": timestamp.hour in [11, 12, 13, 17, 18, 19, 20],
                    "is_lunch": timestamp.hour in [11, 12, 13],
                    "is_dinner": timestamp.hour in [17, 18, 19, 20],
                    # Weather
                    "weather_condition": weather_condition,
                    "temperature_f": weather_data.get("temperature_f"),
                    "precipitation_chance": weather_data.get("precipitation_chance", 0),
                    # Events
                    "active_events": event_data.get("events", []),
                    "event_impact": (
                        "high" if event_data.get("max_attendance", 0) > 5000 else "low"
                    ),
                    # Historical
                    "historical_average": int(percentage * 0.95),
                    "is_holiday": timestamp.month in [11, 12],
                },
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error in enhanced busyness prediction: {e}")
            return {
                "level": "Moderate",
                "percentage": 50,
                "expected_guests": 40,
                "confidence": 0.5,
                "error": str(e),
                "factors": {},
            }

    def predict_sales_enhanced(
        self,
        item_id: int,
        target_date: Optional[datetime] = None,
        item_name: str = "Unknown",
        category: str = "Entrees",
    ) -> Dict:
        """
        Enhanced sales prediction with detailed factors
        Uses existing item_sales_predictor and adds factor breakdown
        """
        if target_date is None:
            target_date = datetime.now()

        try:
            # Get base prediction from model
            base_result = self.item_sales_predictor.predict_daily_sales(
                item_id=item_id,
                date=target_date,
                item_name=item_name,
                category=category,
            )

            # Extract data
            predicted_quantity = base_result.get("predicted_quantity", 50)
            base_confidence = base_result.get("confidence", 0.75)

            # Get weather context
            weather_data = self._get_weather_details(target_date)

            # Get event context
            event_data = self._get_event_details(target_date)

            # Determine if item is weather sensitive
            weather_sensitive = self._is_weather_sensitive_item(category)

            # Calculate margin of error
            margin_low = int(predicted_quantity * (1 - (1 - base_confidence) * 0.5))
            margin_high = int(predicted_quantity * (1 + (1 - base_confidence) * 0.5))

            # Generate recommendation
            recommendation = self._get_purchasing_recommendation(
                predicted_quantity, margin_high, category
            )

            return {
                "item_id": item_id,
                "item_name": item_name,
                "predicted_quantity": predicted_quantity,
                "confidence": base_confidence,
                "margin": {
                    "low": margin_low,
                    "high": margin_high,
                    "range": f"{margin_low}-{margin_high} units",
                },
                "date": target_date.strftime("%Y-%m-%d"),
                "factors": {
                    "day_of_week": self._get_day_name(target_date.weekday()),
                    "is_weekend": target_date.weekday() >= 5,
                    "is_holiday": target_date.month in [11, 12],
                    "month": target_date.month,
                    "category": category,
                    # Weather
                    "weather_condition": weather_data.get("condition", "Unknown"),
                    "weather_sensitive_item": weather_sensitive,
                    "temperature_f": weather_data.get("temperature_f"),
                    # Events
                    "active_events": event_data.get("events", []),
                    "event_attendance": event_data.get("max_attendance"),
                    # Historical
                    "historical_average": int(predicted_quantity * 0.95),
                    "recent_trend": "stable",
                },
                "recommendation": recommendation,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error in enhanced sales prediction: {e}")
            return {
                "item_id": item_id,
                "item_name": item_name,
                "predicted_quantity": 0,
                "confidence": 0.5,
                "error": str(e),
                "factors": {},
            }

    # Helper methods

    def _get_weather_details(self, timestamp: datetime) -> Dict:
        """
        Get weather details for a timestamp - CONSISTENT VERSION

        Always uses forecast data for consistency across predictions
        """
        try:
            # Get all forecasts
            forecasts = self.weather_service.get_forecast(days=7)

            target_date = timestamp.date().isoformat()

            # Find matching forecast
            for forecast in forecasts:
                if forecast.get("date") == target_date:
                    return {
                        "condition": forecast.get("condition", "Unknown"),
                        "temperature_f": forecast.get("temperature_high_f"),
                        "precipitation_chance": forecast.get("precipitation_chance", 0),
                    }

            # If no forecast match and it's today, use current weather
            if timestamp.date() == datetime.now().date():
                current = self.weather_service.get_current_weather()
                if current:
                    # Standardize the condition text
                    condition_text = current.get("condition", "")
                    # Use weather service's standardization method
                    condition = self._standardize_weather_condition(condition_text)

                    return {
                        "condition": condition,
                        "temperature_f": current.get("temperature_f"),
                        "precipitation_chance": 0,
                    }

            # Fallback to unknown
            return {
                "condition": "Unknown",
                "temperature_f": None,
                "precipitation_chance": 0,
            }

        except Exception as e:
            logger.error(f"Error getting weather details: {e}")
            return {
                "condition": "Unknown",
                "temperature_f": None,
                "precipitation_chance": 0,
            }

    def _standardize_weather_condition(self, condition_text: str) -> str:
        """Standardize weather condition text to match your weather service"""
        text_lower = condition_text.lower()

        if any(word in text_lower for word in ["thunder", "storm", "severe"]):
            return "stormy"
        elif any(word in text_lower for word in ["snow", "flurr", "blizzard"]):
            return "snowy"
        elif any(
            word in text_lower
            for word in ["rain", "shower", "drizzle", "precipitation"]
        ):
            return "rainy"
        elif any(word in text_lower for word in ["cloud", "overcast", "gray", "fog"]):
            return "cloudy"
        elif any(word in text_lower for word in ["sun", "clear", "fair"]):
            return "sunny"
        else:
            return "cloudy"  # Default

    def _get_event_details(self, timestamp: datetime) -> Dict:
        """Get event details for a timestamp"""
        try:
            events = self.event_service.get_events_for_date(
                timestamp, use_cache_only=True
            )

            if not events:
                return {"events": [], "max_attendance": 0, "closest_distance": None}

            event_names = [e.get("event_name", "Unknown") for e in events[:3]]
            max_attendance = max([e.get("attendance_estimated", 0) for e in events])
            closest_distance = min([e.get("distance_miles", 999) for e in events])

            return {
                "events": event_names,
                "max_attendance": max_attendance,
                "closest_distance": closest_distance,
            }
        except Exception as e:
            logger.error(f"Error getting event details: {e}")
            return {"events": [], "max_attendance": 0, "closest_distance": None}

    def _categorize_wait_time(self, minutes: int) -> str:
        """Categorize wait time"""
        if minutes < 10:
            return "minimal"
        elif minutes < 20:
            return "short"
        elif minutes < 30:
            return "moderate"
        elif minutes < 45:
            return "long"
        else:
            return "very_long"

    def _build_wait_explanation(
        self, wait_time, occupancy, weather, events, timestamp
    ) -> str:
        """Build human-readable explanation"""
        parts = []

        # Base explanation
        if occupancy > 80:
            parts.append("high current occupancy")

        # Weather impact
        condition = weather.get("condition", "").lower()
        if condition in ["rainy", "snowy", "stormy"]:
            parts.append(f"{condition} weather driving guests indoors")

        # Event impact
        if events.get("events"):
            num_events = len(events["events"])
            parts.append(f"{num_events} nearby event{'s' if num_events > 1 else ''}")

        # Peak time
        if timestamp.hour in [12, 13, 18, 19, 20]:
            parts.append("peak dining hours")

        if not parts:
            return "Standard wait time for current conditions"

        return f"Extended wait due to {', '.join(parts)}"

    def _generate_busyness_recommendation(self, level: str, event_data: Dict) -> str:
        """Generate staffing recommendation"""
        level_lower = level.lower()

        if level_lower == "slow":
            return "Good time for maintenance or prep work"
        elif level_lower == "moderate":
            return "Standard staffing should be sufficient"
        elif level_lower == "peak":
            if event_data.get("max_attendance", 0) > 5000:
                return "All hands on deck - major event nearby, expect high demand"
            return "All hands on deck - expect wait times"
        else:  # Busy/Very Busy
            return "Ensure all stations are fully staffed"

    def _is_weather_sensitive_item(self, category: str) -> bool:
        """Determine if item category is weather sensitive"""
        sensitive_categories = ["Beverages", "Salads", "Desserts"]
        return category in sensitive_categories

    def _get_purchasing_recommendation(
        self, predicted: int, margin_high: int, category: str
    ) -> str:
        """Generate purchasing recommendation"""
        buffer = margin_high - predicted

        if buffer > 10:
            return f"Order {margin_high} units to account for variability"
        elif buffer > 5:
            return f"Order {predicted + 5} units with small safety margin"
        else:
            return f"Order {predicted} units based on stable prediction"

    @staticmethod
    def _get_day_name(day_index: int) -> str:
        """Convert day index to name"""
        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        return days[day_index % 7]

    @staticmethod
    def _get_time_period(hour: int) -> str:
        """Convert hour to time period"""
        if 6 <= hour < 11:
            return "breakfast"
        elif 11 <= hour < 15:
            return "lunch"
        elif 15 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 22:
            return "dinner"
        else:
            return "late_night"


# Create singleton instance
enhanced_prediction_service = EnhancedPredictionService()
