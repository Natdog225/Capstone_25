"""
Show upcoming events for the next 7 days
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timedelta
from app.services.event_service import EventService

def show_upcoming_events(days=7):
    """Display upcoming events"""
    service = EventService()
    
    print(f"\n🎫 Upcoming Events (Next {days} Days)\n")
    print("=" * 80)
    
    start_date = datetime.now()
    
    for day in range(days):
        date = start_date + timedelta(days=day)
        events = service.get_events_for_date(date)
        
        if events:
            print(f"\n📅 {date.strftime('%A, %B %d, %Y')}")
            print("-" * 80)
            for event in events:
                impact = service.calculate_event_impact(event, date.replace(hour=18))  # Check 6pm impact
                print(f"   🎪 {event['event_name']}")
                print(f"      Time: {event['event_time']}")
                print(f"      Venue: {event['venue_name']} ({event['distance_miles']} mi)")
                print(f"      Type: {event['event_type']} | Attendance: {event['attendance_estimated']:,}")
                print(f"      Impact at 6pm: +{impact['impact_minutes']} min ({impact['impact_level']})")
                print()
        else:
            print(f"\n📅 {date.strftime('%A, %B %d, %Y')}: No events")
    
    print("=" * 80)

if __name__ == "__main__":
    show_upcoming_events(7)