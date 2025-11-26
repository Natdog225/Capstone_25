import pandas as pd
from datetime import datetime
from meteostat import Point, Daily
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def backfill_weather():
    logger.info("🌤️ Starting weather backfill...")

    # 1. Load your existing data
    orders_path = "data/processed/orders_from_real_data.csv"
    wait_times_path = "data/processed/wait_times_from_real_data.csv"

    try:
        orders = pd.read_csv(orders_path)
        wait_times = pd.read_csv(wait_times_path)
    except FileNotFoundError:
        logger.error("Could not find data files. Run process_real_data.py first.")
        return

    # 2. Setup Tulsa Location (Lat, Lon, Alt)
    tulsa = Point(36.1540, -95.9928, 200)

    # 3. Define Date Range (From your data)
    # Convert to datetime to find min/max
    orders["order_timestamp"] = pd.to_datetime(orders["order_timestamp"])
    start = orders["order_timestamp"].min().to_pydatetime()
    end = orders["order_timestamp"].max().to_pydatetime()

    logger.info(f"Fetching history from {start.date()} to {end.date()}...")

    # 4. Fetch History
    data = Daily(tulsa, start, end)
    data = data.fetch()

    # 5. Create a Mapper
    # Meteostat codes: coco (Condition Code).
    # 1-6: Clear/Cloudy, 7-9: Rain, 12-16: Snow/Storm
    weather_map = {}

    for index, row in data.iterrows():
        date_str = index.strftime("%Y-%m-%d")
        coco = row.get("coco", 0)

        # Simplify to 4 categories for the model
        condition = "sunny"
        if coco in [7, 8, 9, 10, 11, 17, 18]:
            condition = "rainy"
        elif coco in [12, 13, 14, 15, 16]:
            condition = "snowy"
        elif coco in [3, 4, 5, 6]:
            condition = "cloudy"

        weather_map[date_str] = condition

    logger.info(f"✓ Mapped weather for {len(weather_map)} days")

    # 6. Apply to DataFrames
    def get_weather(timestamp_str):
        # Extract YYYY-MM-DD
        if isinstance(timestamp_str, str):
            date_key = timestamp_str.split(" ")[0]
        else:
            date_key = timestamp_str.strftime("%Y-%m-%d")
        return weather_map.get(date_key, "sunny")

    orders["weather_condition"] = orders["order_timestamp"].apply(get_weather)

    # Save
    orders.to_csv(orders_path, index=False)
    logger.info(f"✓ Enriched {len(orders)} orders with weather")

    # Also update wait times if you use that for training
    if "timestamp_quoted" in wait_times.columns:
        wait_times["weather_condition"] = wait_times["timestamp_quoted"].apply(
            get_weather
        )
        wait_times.to_csv(wait_times_path, index=False)
        logger.info(f"✓ Enriched {len(wait_times)} wait time logs with weather")


if __name__ == "__main__":
    backfill_weather()
