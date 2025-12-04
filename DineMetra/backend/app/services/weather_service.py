"""
Dinemetra Weather Service
Fetches weather data from weather.gov (National Weather Service)

This service:
1. Gets current weather conditions
2. Fetches 7-day forecast
3. Provides weather impact calculations for predictions

Run: python -m app.services.weather_service
"""

import requests
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, List
import logging
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class WeatherService:
    """
    Fetches weather data from weather.gov API
    """

    def __init__(self, lat: float = 36.1540, lng: float = -95.9928):
        """
        Initialize weather service

        Args:
            lat: Latitude of restaurant
            lng: Longitude of restaurant
        """
        self.lat = lat
        self.lng = lng

        # Weather.gov requires a User-Agent header
        self.headers = {
            "User-Agent": "(Dinemetra Restaurant Analytics, contact@dinemetra.com)",
            "Accept": "application/json",
        }

        # Cache directory
        self.cache_dir = Path("data/weather")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Get grid point info (required for weather.gov API)
        self.grid_info = self._get_grid_info()

        logger.info(f"Weather service initialized for ({lat}, {lng})")

    def _get_grid_info(self) -> Dict:
        """
        Get grid information for location from weather.gov
        This is required to fetch forecasts

        Returns:
            Dictionary with grid office and coordinates
        """
        try:
            url = f"https://api.weather.gov/points/{self.lat},{self.lng}"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            properties = data.get("properties", {})

            grid_info = {
                "office": properties.get("gridId"),
                "grid_x": properties.get("gridX"),
                "grid_y": properties.get("gridY"),
                "forecast_url": properties.get("forecast"),
                "forecast_hourly_url": properties.get("forecastHourly"),
                "observation_stations_url": properties.get("observationStations"),
            }

            logger.info(
                f"✓ Grid info: {grid_info['office']} ({grid_info['grid_x']}, {grid_info['grid_y']})"
            )
            return grid_info

        except Exception as e:
            logger.error(f"Error getting grid info: {e}")
            return {}

    def get_current_weather(self) -> Optional[Dict]:
        """
        Get current weather conditions

        Returns:
            Dictionary with current weather data
        """
        try:
            # Get observation stations
            stations_url = self.grid_info.get("observation_stations_url")
            if not stations_url:
                logger.warning("No observation stations URL available")
                return None

            # Get list of stations
            response = requests.get(stations_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            stations_data = response.json()

            stations = stations_data.get("features", [])
            if not stations:
                logger.warning("No weather stations found")
                return None

            # Try first station (closest one)
            station_url = stations[0]["id"]
            obs_url = f"{station_url}/observations/latest"

            response = requests.get(obs_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            obs_data = response.json()

            properties = obs_data.get("properties", {})

            # Convert to our format
            temp_c = properties.get("temperature", {}).get("value")
            temp_f = (temp_c * 9 / 5) + 32 if temp_c else None

            weather = {
                "timestamp": properties.get("timestamp"),
                "temperature_f": round(temp_f, 1) if temp_f else None,
                "condition": properties.get("textDescription", "Unknown"),
                "humidity": properties.get("relativeHumidity", {}).get("value"),
                "wind_speed": properties.get("windSpeed", {}).get("value"),
                "precipitation_last_hour": properties.get(
                    "precipitationLastHour", {}
                ).get("value", 0),
                "station": station_url.split("/")[-1],
            }

            return weather

        except Exception as e:
            logger.error(f"Error fetching current weather: {e}")
            return None

    def get_forecast(self, days: int = 7) -> List[Dict]:
        """
        Get weather forecast for next N days

        Args:
            days: Number of days to forecast (max 7)

        Returns:
            List of daily forecast dictionaries
        """
        try:
            forecast_url = self.grid_info.get("forecast_url")
            if not forecast_url:
                logger.warning("No forecast URL available")
                return []

            response = requests.get(forecast_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            periods = data.get("properties", {}).get("periods", [])

            # Process forecast periods
            forecasts = []
            current_date = None
            daily_forecast = {}

            for period in periods[: days * 2]:  # Each day has 2 periods (day/night)
                start_time = datetime.fromisoformat(
                    period["startTime"].replace("Z", "+00:00")
                )
                period_date = start_time.date()

                # Start new day
                if period_date != current_date:
                    if daily_forecast:
                        forecasts.append(daily_forecast)

                    current_date = period_date
                    daily_forecast = {
                        "date": period_date.isoformat(),
                        "day_of_week": period_date.weekday(),
                        "temperature_high_f": None,
                        "temperature_low_f": None,
                        "condition": "",
                        "precipitation_chance": 0,
                        "short_forecast": "",
                    }

                # Day period
                if period["isDaytime"]:
                    daily_forecast["temperature_high_f"] = period.get("temperature")
                    daily_forecast["condition"] = self._standardize_condition(
                        period.get("shortForecast", "")
                    )
                    daily_forecast["short_forecast"] = period.get("shortForecast", "")
                    precip_prob = period.get("probabilityOfPrecipitation", {})
                    daily_forecast["precipitation_chance"] = (
                        precip_prob.get("value", 0) if precip_prob else 0
                    )
                # Night period
                else:
                    daily_forecast["temperature_low_f"] = period.get("temperature")

            # Add last day if exists
            if daily_forecast and daily_forecast not in forecasts:
                forecasts.append(daily_forecast)

            logger.info(f"✓ Fetched {len(forecasts)} day forecast")
            return forecasts

        except Exception as e:
            logger.error(f"Error fetching forecast: {e}")
            return []

    def get_hourly_forecast(self, hours: int = 24) -> List[Dict]:
        """
        Get hourly weather forecast

        Args:
            hours: Number of hours to forecast

        Returns:
            List of hourly forecast dictionaries
        """
        try:
            forecast_url = self.grid_info.get("forecast_hourly_url")
            if not forecast_url:
                logger.warning("No hourly forecast URL available")
                return []

            response = requests.get(forecast_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            periods = data.get("properties", {}).get("periods", [])

            hourly_forecasts = []
            for period in periods[:hours]:
                start_time = datetime.fromisoformat(
                    period["startTime"].replace("Z", "+00:00")
                )

                hourly = {
                    "timestamp": start_time.isoformat(),
                    "hour": start_time.hour,
                    "temperature_f": period["temperature"],
                    "condition": self._standardize_condition(period["shortForecast"]),
                    "short_forecast": period["shortForecast"],
                    "precipitation_chance": period.get(
                        "probabilityOfPrecipitation", {}
                    ).get("value", 0)
                    or 0,
                    "wind_speed": period.get("windSpeed", "Unknown"),
                }

                hourly_forecasts.append(hourly)

            logger.info(f"✓ Fetched {len(hourly_forecasts)} hour forecast")
            return hourly_forecasts

        except Exception as e:
            logger.error(f"Error fetching hourly forecast: {e}")
            return []

    def _standardize_condition(self, forecast_text: str) -> str:
        """
        Standardize weather condition text to simple categories

        Args:
            forecast_text: Raw forecast text from weather.gov

        Returns:
            Standardized condition (sunny, cloudy, rainy, snowy, stormy)
        """
        text_lower = forecast_text.lower()

        if any(word in text_lower for word in ["thunder", "storm", "severe"]):
            return "stormy"
        elif any(word in text_lower for word in ["snow", "flurr", "blizzard"]):
            return "snowy"
        elif any(
            word in text_lower
            for word in ["rain", "shower", "drizzle", "precipitation"]
        ):
            return "rainy"
        elif any(word in text_lower for word in ["cloud", "overcast", "gray"]):
            return "cloudy"
        elif any(word in text_lower for word in ["sun", "clear", "fair"]):
            return "sunny"
        else:
            return "cloudy"  # Default

    def get_weather_for_date(self, date: datetime) -> Optional[Dict]:
        """
        Get weather forecast for a specific date

        Args:
            date: Date to get weather for

        Returns:
            Weather dictionary for that date or None
        """
        # If date is today, try to get current weather
        if date.date() == datetime.now().date():
            current = self.get_current_weather()
            if current:
                return {
                    "date": date.date().isoformat(),
                    "day_of_week": date.weekday(),
                    "temperature_high_f": current.get("temperature_f"),
                    "temperature_low_f": current.get("temperature_f"),
                    "condition": self._standardize_condition(
                        current.get("condition", "")
                    ),
                    "precipitation_chance": 0,
                }

        # Get forecast
        forecasts = self.get_forecast(days=7)

        # Find matching date
        for forecast in forecasts:
            if forecast["date"] == date.date().isoformat():
                return forecast

        return None

    def calculate_weather_impact(self, weather: Dict) -> float:
        """
        Calculate how weather affects restaurant traffic

        Args:
            weather: Weather dictionary

        Returns:
            Impact on wait time in minutes (-5 to +10)
        """
        if not weather:
            return 0.0

        impact = 0.0

        condition = weather.get("condition", "sunny").lower()
        temp = weather.get("temperature_high_f")
        precip_chance = weather.get("precipitation_chance", 0)

        # Use default temp if None
        if temp is None:
            temp = 70  # Default moderate temperature

        # Rain/snow drives people indoors (increases wait)
        if condition in ["rainy", "snowy", "stormy"]:
            impact += 5.0
            # More impact if high precipitation chance
            if precip_chance and precip_chance > 70:
                impact += 3.0

        # Extreme temperatures drive people indoors
        if temp < 32:
            impact += 4.0  # Very cold
        elif temp > 95:
            impact += 3.0  # Very hot

        # Nice weather reduces indoor dining (negative impact)
        if condition == "sunny" and 65 <= temp <= 85:
            impact -= 5.0  # People want to be outside

        return round(max(-5, min(10, impact)), 1)

    def save_forecast_to_cache(self, forecasts: List[Dict]):
        """Save forecast to cache file"""
        cache_file = (
            self.cache_dir / f"forecast_{datetime.now().strftime('%Y%m%d')}.json"
        )

        with open(cache_file, "w") as f:
            json.dump(
                {
                    "fetched_at": datetime.now().isoformat(),
                    "location": f"{self.lat},{self.lng}",
                    "forecasts": forecasts,
                },
                f,
                indent=2,
            )

        logger.info(f"✓ Cached forecast to {cache_file}")


# ========================================
# STANDALONE SCRIPT
# ========================================


def main():
    """Test weather service"""
    logger.info("=" * 60)
    logger.info("🌤️  Dinemetra Weather Service Test")
    logger.info("=" * 60)

    # Initialize for Tulsa, OK
    service = WeatherService(lat=36.1540, lng=-95.9928)

    # Get current weather
    logger.info("\n📊 Current Weather:")
    current = service.get_current_weather()
    if current:
        logger.info(f"   Temperature: {current['temperature_f']}°F")
        logger.info(f"   Condition: {current['condition']}")
        logger.info(f"   Humidity: {current['humidity']}%")
    else:
        logger.warning("   Could not fetch current weather")

    # Get 7-day forecast
    logger.info("\n📅 7-Day Forecast:")
    forecasts = service.get_forecast(days=7)
    for forecast in forecasts:
        impact = service.calculate_weather_impact(forecast)
        logger.info(
            f"   {forecast['date']}: {forecast['condition']} | "
            f"High: {forecast['temperature_high_f']}°F | "
            f"Low: {forecast['temperature_low_f']}°F | "
            f"Precip: {forecast['precipitation_chance']}% | "
            f"Impact: {impact:+.1f} min"
        )

    # Save to cache
    if forecasts:
        service.save_forecast_to_cache(forecasts)

    # Get hourly forecast
    logger.info("\n⏰ Next 12 Hours:")
    hourly = service.get_hourly_forecast(hours=12)
    for hour in hourly[:5]:  # Show first 5 hours
        timestamp = datetime.fromisoformat(hour["timestamp"])
        logger.info(
            f"   {timestamp.strftime('%I:%M %p')}: {hour['temperature_f']}°F | "
            f"{hour['condition']} | Precip: {hour['precipitation_chance']}%"
        )

    logger.info("\n" + "=" * 60)
    logger.info("✅ Weather service test complete!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
