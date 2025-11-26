"""
Test Ticketmaster API connection
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from datetime import datetime, timedelta
from app.services.event_service import EventService

def test_api_connection():
    """Test basic API connectivity"""
    print("🧪 Testing Ticketmaster API Connection\n")
    
    service = EventService()
    
    # Check if API key is set
    if not service.ticketmaster_key:
        print("❌ TICKETMASTER_API_KEY not found in .env file")
        print("\nPlease add your API key to backend/.env:")
        print("TICKETMASTER_API_KEY=your_key_here")
        return False
    
    print(f"✓ API key found: {service.ticketmaster_key[:10]}...")
    print(f"✓ Restaurant location: {service.restaurant_location['city']}, {service.restaurant_location['state']}")
    print(f"✓ Search radius: {service.search_radius_miles} miles\n")
    
    # Test fetching events for next week
    start_date = datetime.now()
    end_date = start_date + timedelta(days=7)
    
    print(f"Fetching events from {start_date.date()} to {end_date.date()}...")
    events = service.fetch_ticketmaster_events(start_date, end_date)
    
    if not events:
        print("\n⚠️  No events found (this might be normal if there are no events in the next week)")
        print("Try increasing the date range or search radius")
        return True
    
    print(f"\n✅ Successfully fetched {len(events)} events!\n")
    
    # Show details of first event
    print("📋 Sample Event Details:")
    event = events[0]
    print(f"   Name: {event['event_name']}")
    print(f"   Type: {event['event_type']}")
    print(f"   Date: {event['event_date']} at {event['event_time']}")
    print(f"   Venue: {event['venue_name']}")
    print(f"   Distance: {event['distance_miles']} miles")
    print(f"   Est. Attendance: {event['attendance_estimated']:,} people")
    print(f"   URL: {event['event_url'][:50]}...")
    
    # Test impact calculation
    print("\n📊 Testing Impact Calculation:")
    current_time = datetime.fromisoformat(event['event_datetime']) - timedelta(hours=1)
    impact = service.calculate_event_impact(event, current_time)
    print(f"   Impact (1 hour before event): +{impact['impact_minutes']} minutes wait time")
    print(f"   Impact Level: {impact['impact_level']}")
    
    print("\n✅ All tests passed!")
    return True

if __name__ == "__main__":
    test_api_connection()