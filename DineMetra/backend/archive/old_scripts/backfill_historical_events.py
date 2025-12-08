"""
Backfill Historical Event Data
Query Ticketmaster for events during our 6-month data period (Jan-Jun 2025)
and save them to match our sales data dates
"""

import requests
import json
from datetime import datetime, timedelta
from pathlib import Path
import os
from dotenv import load_dotenv
import time

load_dotenv()

API_KEY = os.getenv("TICKETMASTER_API_KEY")
RESTAURANT_LAT = float(os.getenv("RESTAURANT_LAT", 36.1583552))
RESTAURANT_LNG = float(os.getenv("RESTAURANT_LNG", -96.0001874))
RADIUS = int(os.getenv("EVENT_SEARCH_RADIUS", 5))

def fetch_events_for_date_range(start_date, end_date):
    """Fetch events from Ticketmaster for a date range"""
    
    url = "https://app.ticketmaster.com/discovery/v2/events.json"
    
    params = {
        'apikey': API_KEY,
        'latlong': f"{RESTAURANT_LAT},{RESTAURANT_LNG}",
        'radius': RADIUS,
        'unit': 'miles',
        'startDateTime': start_date.strftime('%Y-%m-%dT00:00:00Z'),
        'endDateTime': end_date.strftime('%Y-%m-%dT23:59:59Z'),
        'size': 200,  # Max results per request
        'sort': 'date,asc'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        events = []
        if '_embedded' in data and 'events' in data['_embedded']:
            for event in data['_embedded']['events']:
                try:
                    event_date = event['dates']['start'].get('localDate', '')
                    event_time = event['dates']['start'].get('localTime', '19:00:00')
                    
                    # Parse venue
                    venue = event.get('_embedded', {}).get('venues', [{}])[0]
                    venue_name = venue.get('name', 'Unknown Venue')
                    
                    # Estimate attendance based on venue capacity or default
                    capacity = venue.get('capacity', 5000)
                    attendance = int(capacity * 0.8)  # Assume 80% capacity
                    
                    # Calculate distance (simplified - Ticketmaster provides this)
                    distance = venue.get('distance', 1.0)
                    
                    events.append({
                        'event_name': event['name'],
                        'event_date': event_date,
                        'event_time': event_time,
                        'event_datetime': f"{event_date}T{event_time}",
                        'venue_name': venue_name,
                        'venue_capacity': capacity,
                        'attendance_estimated': attendance,
                        'distance_miles': round(float(distance), 2),
                        'category': event.get('classifications', [{}])[0].get('segment', {}).get('name', 'Other')
                    })
                except Exception as e:
                    print(f"  ⚠️ Error parsing event: {e}")
                    continue
        
        return events
        
    except requests.exceptions.RequestException as e:
        print(f"  ❌ API Error: {e}")
        return []


def backfill_events():
    """Backfill events for Jan-Jun 2025"""
    
    print("🔄 BACKFILLING HISTORICAL EVENT DATA")
    print("=" * 60)
    print(f"Location: ({RESTAURANT_LAT}, {RESTAURANT_LNG})")
    print(f"Radius: {RADIUS} miles")
    print(f"Period: January 2025 - June 2025")
    print()
    
    # Define our 6-month period
    months = [
        (datetime(2025, 1, 1), datetime(2025, 1, 31)),   # January
        (datetime(2025, 2, 1), datetime(2025, 2, 28)),   # February
        (datetime(2025, 3, 1), datetime(2025, 3, 31)),   # March
        (datetime(2025, 4, 1), datetime(2025, 4, 30)),   # April
        (datetime(2025, 5, 1), datetime(2025, 5, 31)),   # May
        (datetime(2025, 6, 1), datetime(2025, 6, 30)),   # June
    ]
    
    all_events = []
    
    for start_date, end_date in months:
        month_name = start_date.strftime('%B %Y')
        print(f"📅 Fetching events for {month_name}...")
        
        events = fetch_events_for_date_range(start_date, end_date)
        all_events.extend(events)
        
        print(f"  ✓ Found {len(events)} events")
        
        # Rate limiting - be nice to the API
        time.sleep(1)
    
    print()
    print("=" * 60)
    print(f"✅ Total Events Found: {len(all_events)}")
    print("=" * 60)
    
    # Save to file
    output_dir = Path("data/events")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "historical_events_2025_jan_jun.json"
    
    with open(output_file, 'w') as f:
        json.dump({
            'period': 'January 2025 - June 2025',
            'total_events': len(all_events),
            'events': all_events,
            'generated_at': datetime.now().isoformat()
        }, f, indent=2)
    
    print(f"💾 Saved to: {output_file}")
    print()
    
    # Show summary by month
    print("📊 Events by Month:")
    from collections import defaultdict
    by_month = defaultdict(int)
    
    for event in all_events:
        month = event['event_date'][:7]  # YYYY-MM
        by_month[month] += 1
    
    for month in sorted(by_month.keys()):
        print(f"  {month}: {by_month[month]} events")
    
    print()
    
    # Show top venues
    print("🏟️ Top Venues:")
    from collections import Counter
    venues = Counter(event['venue_name'] for event in all_events)
    
    for venue, count in venues.most_common(5):
        print(f"  {venue}: {count} events")
    
    print()
    print("✅ Backfill complete!")
    print()
    print("Next steps:")
    print("1. Review the generated file")
    print("2. Integrate events into your training data")
    print("3. Retrain models with event features")


if __name__ == "__main__":
    if not API_KEY:
        print("❌ TICKETMASTER_API_KEY not found in .env")
        print("Please add it to continue.")
        exit(1)
    
    backfill_events()
