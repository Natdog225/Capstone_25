"""
Populate external_factors table with event data
Combines Ticketmaster events with existing weather/holiday data
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timedelta
import pandas as pd
import logging

from app.services.event_service import EventDataService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def populate_events_for_date_range(start_date: datetime, end_date: datetime):
    """
    Fetch events and merge with existing external_factors data

    Args:
        start_date: Start of date range
        end_date: End of date range
    """
    logger.info(f"Populating events from {start_date.date()} to {end_date.date()}...")

    # Initialize event service
    service = EventDataService()

    # Fetch all events in date range
    all_events = service.fetch_ticketmaster_events(start_date, end_date)

    if not all_events:
        logger.warning("No events found")
        return

    # Load existing external_factors data
    factors_file = Path("data/external_factors_raw.csv")
    if factors_file.exists():
        df = pd.read_csv(factors_file)
        df["factor_date"] = pd.to_datetime(df["factor_date"]).dt.date
    else:
        # Create new dataframe
        logger.info("Creating new external_factors dataframe...")
        dates = pd.date_range(start_date, end_date, freq="D")
        df = pd.DataFrame(
            {
                "factor_date": [d.date() for d in dates],
                "day_of_week": [d.dayofweek for d in dates],
                "is_holiday": False,
                "holiday_name": None,
                "weather_condition": "sunny",  # Default
                "temperature_high_f": 70.0,
                "temperature_low_f": 50.0,
                "precipitation_inches": 0.0,
            }
        )

    # Add event columns if they don't exist
    if "local_event_name" not in df.columns:
        df["local_event_name"] = None
    if "local_event_type" not in df.columns:
        df["local_event_type"] = None
    if "event_attendance_estimated" not in df.columns:
        df["event_attendance_estimated"] = None
    if "event_distance_miles" not in df.columns:
        df["event_distance_miles"] = None

    # Group events by date and select the biggest event per day
    events_by_date = {}
    for event in all_events:
        event_date = datetime.fromisoformat(event["event_date"]).date()

        if event_date not in events_by_date:
            events_by_date[event_date] = event
        else:
            # Keep the bigger event
            if (
                event["attendance_estimated"]
                > events_by_date[event_date]["attendance_estimated"]
            ):
                events_by_date[event_date] = event

    # Update dataframe with event data
    for event_date, event in events_by_date.items():
        mask = df["factor_date"] == event_date
        df.loc[mask, "local_event_name"] = event["event_name"]
        df.loc[mask, "local_event_type"] = event["event_type"]
        df.loc[mask, "event_attendance_estimated"] = event["attendance_estimated"]
        df.loc[mask, "event_distance_miles"] = event["distance_miles"]

    # Save updated data
    output_file = Path("data/external_factors_with_events.csv")
    df.to_csv(output_file, index=False)

    logger.info(f"\n✅ Event data populated!")
    logger.info(f"   Total days: {len(df)}")
    logger.info(f"   Days with events: {len(events_by_date)}")
    logger.info(f"   Saved to: {output_file}")

    # Show sample events
    logger.info(f"\n📅 Sample Events:")
    events_df = df[df["local_event_name"].notna()].head(10)
    for _, row in events_df.iterrows():
        logger.info(
            f"   {row['factor_date']}: {row['local_event_name']} ({row['event_attendance_estimated']:,} people)"
        )


def main():
    """Populate events for next 60 days"""
    start_date = datetime.now()
    end_date = start_date + timedelta(days=60)

    populate_events_for_date_range(start_date, end_date)


if __name__ == "__main__":
    main()
