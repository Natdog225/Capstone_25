#!/usr/bin/env python3
"""
Weather Backfill - Uses Open-Meteo for historical data
Properly updates the weather_condition column in orders_from_real_data.csv
"""

import pandas as pd
import requests
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def backfill_weather():
    """Backfill weather data using Open-Meteo historical API"""

    # Load the data
    logger.info("📊 Loading orders data...")
    df = pd.read_csv("data/processed/orders_from_real_data.csv")

    logger.info(f"Found {len(df)} orders")
    logger.info(f"Columns: {list(df.columns)}")

    # Convert timestamp
    df["order_timestamp"] = pd.to_datetime(df["order_timestamp"])

    # Get date range
    start_date = df["order_timestamp"].min().strftime("%Y-%m-%d")
    end_date = df["order_timestamp"].max().strftime("%Y-%m-%d")

    logger.info(f"Date range: {start_date} to {end_date}")

    # Fetch historical weather from Open-Meteo
    logger.info("🌤️  Fetching historical weather from Open-Meteo...")

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": 36.1540,  # Tulsa
        "longitude": -95.9928,
        "start_date": start_date,
        "end_date": end_date,
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "America/Chicago",
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        weather_data = response.json()

        logger.info(f"✓ Fetched weather for {len(weather_data['daily']['time'])} days")

    except Exception as e:
        logger.error(f"❌ Failed to fetch weather: {e}")
        return

    # Map WMO weather codes to conditions
    def map_weather_code(code):
        """
        Maps WMO weather codes to simple conditions
        https://open-meteo.com/en/docs
        """
        if code is None:
            return "sunny"

        # Clear sky
        if code == 0:
            return "sunny"

        # Mainly clear, partly cloudy
        if code in [1, 2]:
            return "sunny"

        # Overcast
        if code == 3:
            return "cloudy"

        # Fog
        if code in [45, 48]:
            return "cloudy"

        # Drizzle
        if code in [51, 53, 55, 56, 57]:
            return "rainy"

        # Rain
        if code in [61, 63, 65, 66, 67, 80, 81, 82]:
            return "rainy"

        # Snow
        if code in [71, 73, 75, 77, 85, 86]:
            return "snowy"

        # Thunderstorm
        if code in [95, 96, 99]:
            return "stormy"

        # Default
        return "cloudy"

    # Create weather lookup dictionary
    weather_map = {}
    for i, date_str in enumerate(weather_data["daily"]["time"]):
        code = weather_data["daily"]["weather_code"][i]
        temp_max = weather_data["daily"]["temperature_2m_max"][i]
        precip = weather_data["daily"]["precipitation_sum"][i]

        condition = map_weather_code(code)

        weather_map[date_str] = {
            "condition": condition,
            "code": code,
            "temp_max": temp_max,
            "precipitation": precip,
        }

    logger.info(f"✓ Mapped {len(weather_map)} days of weather")

    # Show sample of weather data
    logger.info("\n📋 Sample weather data:")
    for date, weather in list(weather_map.items())[:5]:
        logger.info(
            f"  {date}: {weather['condition']} (code: {weather['code']}, temp: {weather['temp_max']}°C)"
        )

    # Apply weather to each order
    def get_weather_for_date(timestamp):
        date_str = timestamp.strftime("%Y-%m-%d")
        weather = weather_map.get(date_str)
        if weather:
            return weather["condition"]
        return "sunny"  # Default fallback

    logger.info("\n🔄 Applying weather to orders...")
    df["weather_condition"] = df["order_timestamp"].apply(get_weather_for_date)

    # Save back to CSV
    logger.info("💾 Saving updated data...")
    df.to_csv("data/processed/orders_from_real_data.csv", index=False)

    # Show results
    logger.info("\n✅ Weather backfill complete!")
    logger.info(f"Updated {len(df)} orders")
    logger.info("\n📊 Weather distribution:")
    weather_counts = df["weather_condition"].value_counts()
    for condition, count in weather_counts.items():
        percentage = (count / len(df)) * 100
        logger.info(f"  {condition:10s}: {count:6d} ({percentage:5.1f}%)")

    # Show sample of updated data
    logger.info("\n📋 Sample updated rows:")
    sample = df[["order_timestamp", "weather_condition"]].head(10)
    for idx, row in sample.iterrows():
        logger.info(f"  {row['order_timestamp']}: {row['weather_condition']}")

    # Verify variety
    unique_conditions = df["weather_condition"].nunique()
    if unique_conditions == 1:
        logger.warning(
            "⚠️  WARNING: Only one weather condition found! Check API response."
        )
    else:
        logger.info(
            f"\n✓ Found {unique_conditions} different weather conditions - looks good!"
        )


if __name__ == "__main__":
    backfill_weather()
