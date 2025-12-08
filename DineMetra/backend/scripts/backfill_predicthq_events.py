"""
Backfill Historical Events Using PredictHQ (FIXED)
"""

import requests
import json
from datetime import datetime
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("PREDICTHQ_API_TOKEN")
RESTAURANT_LAT = float(os.getenv("RESTAURANT_LAT", 36.1583552))
RESTAURANT_LNG = float(os.getenv("RESTAURANT_LNG", -96.0001874))

def fetch_predicthq_events(start_date, end_date):
    """Fetch events from PredictHQ with correct parameters"""
    
    url = "https://api.predicthq.com/v1/events/"
    
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Accept': 'application/json'
    }
    
    # Simplified params - PredictHQ is picky!
    params = {
        'within': f'25km@{RESTAURANT_LAT},{RESTAURANT_LNG}',  # Correct format
        'active.gte': start_date.strftime('%Y-%m-%d'),
        'active.lte': end_date.strftime('%Y-%m-%d'),
        'limit': 500
    }
    
    try:
        print(f"  Querying PredictHQ...")
        print(f"  Center: {RESTAURANT_LAT}, {RESTAURANT_LNG}")
        print(f"  Radius: 25km (~15 miles)")
        print(f"  Dates: {start_date.date()} to {end_date.date()}")
        
        response = requests.get(url, headers=headers, params=params, timeout=15)
        
        print(f"  Status Code: {response.status_code}")
        
        if response.status_code == 401:
            print("  ❌ Authentication failed")
            print(f"  Token starts with: {API_TOKEN[:10]}...")
            return []
        elif response.status_code == 429:
            print("  ❌ Rate limit exceeded")
            return []
        elif response.status_code != 200:
            print(f"  ❌ Error: {response.text[:300]}")
            return []
        
        data = response.json()
        
        total = data.get('count', 0)
        results = data.get('results', [])
        print(f"  ✓ Found {total} events, retrieved {len(results)}")
        
        events = []
        for event in results:
            try:
                # Parse start date/time
                start = event.get('start', '')
                event_date = start[:10] if len(start) >= 10 else '2025-01-01'
                event_time = start[11:19] if len(start) > 11 else '19:00:00'
                
                # Get location
                location = event.get('location', [RESTAURANT_LAT, RESTAURANT_LNG])
                
                # Calculate rough distance
                lat_diff = abs(location[0] - RESTAURANT_LAT)
                lng_diff = abs(location[1] - RESTAURANT_LNG)
                distance_km = ((lat_diff ** 2 + lng_diff ** 2) ** 0.5) * 111
                distance_miles = distance_km * 0.621371
                
                # Get venue
                venue_name = 'Unknown Venue'
                venue_capacity = 5000
                
                entities = event.get('entities', [])
                if entities and len(entities) > 0:
                    venue_name = entities[0].get('name', 'Unknown Venue')
                    venue_capacity = entities[0].get('capacity', 5000)
                
                # Build event object
                events.append({
                    'event_name': event.get('title', 'Unknown Event'),
                    'event_date': event_date,
                    'event_time': event_time,
                    'event_datetime': start,
                    'venue_name': venue_name,
                    'venue_capacity': venue_capacity,
                    'attendance_estimated': event.get('phq_attendance', 1000),
                    'phq_rank': event.get('rank', 50),
                    'category': event.get('category', 'other'),
                    'labels': event.get('labels', []),
                    'distance_miles': round(distance_miles, 2)
                })
            except Exception as e:
                print(f"  ⚠️ Parse error: {e}")
                continue
        
        return events
        
    except Exception as e:
        print(f"  ❌ Request failed: {e}")
        return []


def main():
    print("🔄 PREDICTHQ EVENT BACKFILL")
    print("=" * 60)
    
    if not API_TOKEN:
        print("❌ No PREDICTHQ_API_TOKEN in .env")
        print("\nGet one at: https://www.predicthq.com/")
        return
    
    print(f"✓ API Token found (starts with: {API_TOKEN[:15]}...)")
    print()
    
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 6, 30)
    
    events = fetch_predicthq_events(start_date, end_date)
    
    if not events:
        print("\n❌ No events retrieved")
        print("\nTroubleshooting:")
        print("1. Verify API token at: https://control.predicthq.com/")
        print("2. Check API usage/limits in dashboard")
        print("3. Try a smaller date range first")
        print("\nAlternative: Use synthetic data:")
        print("  python scripts/generate_synthetic_historical_events.py")
        return
    
    print()
    print("=" * 60)
    print(f"✅ Retrieved {len(events)} events!")
    print("=" * 60)
    
    # Save
    output_dir = Path("data/events")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "historical_events_2025_jan_jun.json"
    
    with open(output_file, 'w') as f:
        json.dump({
            'period': 'January 2025 - June 2025',
            'source': 'PredictHQ',
            'total_events': len(events),
            'events': events,
            'generated_at': datetime.now().isoformat()
        }, f, indent=2)
    
    print(f"💾 Saved: {output_file}")
    
    # Stats
    from collections import Counter
    
    categories = Counter(e['category'] for e in events)
    print("\n📊 By Category:")
    for cat, count in categories.most_common(10):
        print(f"  {cat}: {count}")
    
    by_distance = Counter()
    for e in events:
        dist = e['distance_miles']
        if dist < 2:
            by_distance['< 2 mi'] += 1
        elif dist < 10:
            by_distance['2-10 mi'] += 1
        else:
            by_distance['10+ mi'] += 1
    
    print("\n📍 By Distance:")
    for dist, count in by_distance.most_common():
        print(f"  {dist}: {count}")
    
    # Top events
    top = sorted(events, key=lambda x: x.get('attendance_estimated', 0), reverse=True)[:10]
    print("\n🎯 Top 10 by Attendance:")
    for e in top:
        print(f"  • {e['event_name'][:40]} - {e['attendance_estimated']:,} people")
    
    print("\n✅ Done!")


if __name__ == "__main__":
    main()
