"""
Update external_factors with both events and weather data
Run this daily to keep data fresh
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timedelta
import pandas as pd
import logging

from app.services.event_service import EventService
from app.services.weather_service import WeatherService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def update_external_factors(days_ahead: int = 7):
    """
    Update external_factors with latest events and weather
    
    Args:
        days_ahead: Number of days ahead to fetch data for
    """
    logger.info("="*60)
    logger.info("🔄 Updating External Factors")
    logger.info("="*60)
    
    start_date = datetime.now()
    end_date = start_date + timedelta(days=days_ahead)
    
    # Initialize services
    event_service = EventService()
    weather_service = WeatherService()
    
    # Fetch events
    logger.info(f"\n🎫 Fetching events ({start_date.date()} to {end_date.date()})...")
    events = event_service.fetch_ticketmaster_events(start_date, end_date)
    logger.info(f"   ✓ Found {len(events)} events")
    
    # Fetch weather
    logger.info(f"\n🌤️  Fetching weather forecast...")
    weather_forecasts = weather_service.get_forecast(days=days_ahead)
    logger.info(f"   ✓ Got {len(weather_forecasts)} day forecast")
    
    # Create date range
    date_range = pd.date_range(start_date, end_date, freq='D')
    
    # Build external factors dataframe
    data = []
    for date in date_range:
        date_obj = date.date()
        
        # Base data
        row = {
            'factor_date': date_obj,
            'day_of_week': date.dayofweek,
            'is_holiday': False,  # TODO: Add holiday detection
            'holiday_name': None
        }
        
        # Find weather for this date
        weather_for_date = next(
            (w for w in weather_forecasts if w['date'] == date_obj.isoformat()),
            None
        )
        
        if weather_for_date:
            row['weather_condition'] = weather_for_date['condition']
            row['temperature_high_f'] = weather_for_date['temperature_high_f']
            row['temperature_low_f'] = weather_for_date['temperature_low_f']
            row['precipitation_inches'] = weather_for_date['precipitation_chance'] / 100 * 0.5  # Estimate
        else:
            # Defaults
            row['weather_condition'] = 'unknown'
            row['temperature_high_f'] = 70.0
            row['temperature_low_f'] = 50.0
            row['precipitation_inches'] = 0.0
        
        # Find biggest event for this date
        events_for_date = [e for e in events if e['event_date'] == date_obj.isoformat()]
        
        if events_for_date:
            # Get biggest event
            biggest_event = max(events_for_date, key=lambda e: e['attendance_estimated'])
            row['local_event_name'] = biggest_event['event_name']
            row['local_event_type'] = biggest_event['event_type']
            row['event_attendance_estimated'] = biggest_event['attendance_estimated']
            row['event_distance_miles'] = biggest_event['distance_miles']
        else:
            row['local_event_name'] = None
            row['local_event_type'] = None
            row['event_attendance_estimated'] = None
            row['event_distance_miles'] = None
        
        data.append(row)
    
    # Create dataframe
    df = pd.DataFrame(data)
    
    # Load existing data if it exists
    existing_file = Path("data/external_factors_with_events.csv")
    if existing_file.exists():
        existing_df = pd.read_csv(existing_file)
        existing_df['factor_date'] = pd.to_datetime(existing_df['factor_date']).dt.date
        
        # Remove dates that we're updating
        existing_df = existing_df[~existing_df['factor_date'].isin(df['factor_date'])]
        
        # Combine
        df = pd.concat([existing_df, df], ignore_index=True)
        df = df.sort_values('factor_date').reset_index(drop=True)
    
    # Save
    output_file = Path("data/external_factors_current.csv")
    df.to_csv(output_file, index=False)
    
    logger.info(f"\n✅ External factors updated!")
    logger.info(f"   Total days in dataset: {len(df)}")
    logger.info(f"   Updated days: {days_ahead}")
    logger.info(f"   Days with events: {df['local_event_name'].notna().sum()}")
    logger.info(f"   Saved to: {output_file}")
    
    # Show sample
    logger.info(f"\n📋 Sample Data (Next 7 Days):")
    sample = df[df['factor_date'] >= start_date.date()].head(7)
    for _, row in sample.iterrows():
        event_info = f" | {row['local_event_name']}" if pd.notna(row['local_event_name']) else ""
        logger.info(f"   {row['factor_date']}: {row['weather_condition']}, "
                   f"{row['temperature_high_f']:.0f}°F{event_info}")


def main():
    """Update external factors for next 7 days"""
    update_external_factors(days_ahead=7)


if __name__ == "__main__":
    main()