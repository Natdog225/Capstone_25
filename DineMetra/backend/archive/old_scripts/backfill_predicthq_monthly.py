"""
Backfill PredictHQ Events Month-by-Month
Easier to debug and handles rate limits better
"""

import requests
import json
from datetime import datetime
from pathlib import Path
import os
from dotenv import load_dotenv
import time

load_dotenv()

API_TOKEN = os.getenv("PREDICTHQ_API_TOKEN")
RESTAURANT_LAT = float(os.getenv("RESTAURANT_LAT", 36.1583552))
RESTAURANT_LNG = float(os.getenv("RESTAURANT_LNG", -96.0001874))

def fetch_month_events(year, month):
    """Fetch events for a specific month"""
    
    # Calculate date range for this month
    if month == 12:
        start_date = datetime(year, month, 1)
        end_date = datetime(year + 1, 1, 1)
    else:
        start_date = datetime(year, month, 1)
        end_date = datetime(year, month + 1, 1)
    
    url = "https://api.predicthq.com/v1/events/"
    
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Accept': 'application/json'
    }
    
    params = {
        'within': f'25km@{RESTAURANT_LAT},{RESTAURANT_LNG}',
        'active.gte': start_date.strftime('%Y-%m-%d'),
        'active.lt': end_date.strftime('%Y-%m-%d'),
        'limit': 100
    }
    
    month_name = start_date.strftime('%B %Y')
    
    try:
        print(f"\n📅 {month_name}:")
        print(f"   Date range: {start_date.date()} to {end_date.date()}")
        
        response = requests.get(url, headers=headers, params=params, timeout=15)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 401:
            print("   ❌ Auth failed - check API token")
            return None, month_name
        elif response.status_code == 429:
            print("   ⚠️  Rate limited - waiting 60s...")
            time.sleep(60)
            return None, month_name
        elif response.status_code != 200:
            print(f"   ❌ Error: {response.text[:200]}")
            return None, month_name
        
        data = response.json()
        
        total = data.get('count', 0)
        results = data.get('results', [])
        
        print(f"   ✓ Found {len(results)} events")
        
        events = []
        for event in results:
            try:
                start = event.get('start', '')
                location = event.get('location', [RESTAURANT_LAT, RESTAURANT_LNG])
                
                # Distance calc
                lat_diff = abs(location[0] - RESTAURANT_LAT)
                lng_diff = abs(location[1] - RESTAURANT_LNG)
                distance_km = ((lat_diff ** 2 + lng_diff ** 2) ** 0.5) * 111
                distance_miles = distance_km * 0.621371
                
                # Venue info
                entities = event.get('entities', [])
                venue_name = entities[0].get('name', 'Unknown') if entities else 'Unknown'
                venue_capacity = entities[0].get('capacity', 5000) if entities else 5000
                
                events.append({
                    'event_name': event.get('title', 'Unknown'),
                    'event_date': start[:10] if len(start) >= 10 else start_date.strftime('%Y-%m-%d'),
                    'event_time': start[11:19] if len(start) > 11 else '19:00:00',
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
                print(f"   ⚠️  Parse error: {e}")
        
        # Rate limit protection
        time.sleep(1)
        
        return events, month_name
        
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
        return None, month_name


def main():
    print("🔄 PREDICTHQ MONTHLY BACKFILL")
    print("=" * 60)
    
    if not API_TOKEN:
        print("❌ No PREDICTHQ_API_TOKEN in .env")
        return
    
    print(f"✓ API Token: {API_TOKEN[:15]}...\n")
    
    # Define months to backfill
    months = [
        (2025, 1),   # January
        (2025, 2),   # February
        (2025, 3),   # March
        (2025, 4),   # April
        (2025, 5),   # May
        (2025, 6),   # June
    ]
    
    all_events = []
    successful_months = []
    failed_months = []
    
    for year, month in months:
        events, month_name = fetch_month_events(year, month)
        
        if events is None:
            failed_months.append(month_name)
            print(f"   ⚠️  Skipping {month_name}")
        else:
            all_events.extend(events)
            successful_months.append(month_name)
    
    print("\n" + "=" * 60)
    print(f"✅ Completed: {len(successful_months)}/6 months")
    print(f"📊 Total events: {len(all_events)}")
    print("=" * 60)
    
    if failed_months:
        print(f"\n⚠️  Failed months: {', '.join(failed_months)}")
    
    if not all_events:
        print("\n❌ No events retrieved from any month")
        print("\nPossible issues:")
        print("1. Free tier may not have historical data access")
        print("2. API token might be invalid")
        print("3. Location might be outside coverage area")
        print("\n💡 Recommendation: Use synthetic data generator")
        print("   python scripts/generate_synthetic_historical_events.py")
        return
    
    # Save
    output_dir = Path("data/events")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "historical_events_2025_jan_jun.json"
    
    with open(output_file, 'w') as f:
        json.dump({
            'period': 'January 2025 - June 2025',
            'source': 'PredictHQ',
            'successful_months': successful_months,
            'failed_months': failed_months,
            'total_events': len(all_events),
            'events': all_events,
            'generated_at': datetime.now().isoformat()
        }, f, indent=2)
    
    print(f"\n💾 Saved: {output_file}")
    
    # Stats
    from collections import Counter
    
    print("\n📊 Events by Month:")
    by_month = Counter(e['event_date'][:7] for e in all_events)
    for month in sorted(by_month.keys()):
        print(f"   {month}: {by_month[month]} events")
    
    print("\n📊 Events by Category:")
    categories = Counter(e['category'] for e in all_events)
    for cat, count in categories.most_common(5):
        print(f"   {cat}: {count}")
    
    print("\n📍 Events by Distance:")
    close = len([e for e in all_events if e['distance_miles'] < 2])
    nearby = len([e for e in all_events if 2 <= e['distance_miles'] < 10])
    far = len([e for e in all_events if e['distance_miles'] >= 10])
    print(f"   < 2 miles: {close}")
    print(f"   2-10 miles: {nearby}")
    print(f"   10+ miles: {far}")
    
    # Show sample events
    if all_events:
        print("\n🎯 Sample Events:")
        sample = sorted(all_events, key=lambda x: x['attendance_estimated'], reverse=True)[:5]
        for e in sample:
            print(f"   • {e['event_name'][:50]}")
            print(f"     {e['event_date']} | {e['attendance_estimated']:,} attendees | {e['distance_miles']}mi")
    
    print("\n✅ Backfill complete!")
    
    if len(successful_months) < 6:
        print("\n💡 Note: Some months failed. Consider using synthetic data:")
        print("   python scripts/generate_synthetic_historical_events.py")


if __name__ == "__main__":
    main()
