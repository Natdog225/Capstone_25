import requests
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import logging
from math import radians, sin, cos, sqrt, atan2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class EventService:
    """
    Manages fetching and processing event data from external APIs.
    Renamed from EventDataService to match ml_service imports.
    """

    def __init__(self, config_path: str = ".env"):
        # Restaurant location (Tulsa, OK)
        self.restaurant_location = {
            "lat": float(os.getenv("RESTAURANT_LAT", "36.1540")),
            "lng": float(os.getenv("RESTAURANT_LNG", "-95.9928")),
            "city": os.getenv("RESTAURANT_CITY", "Tulsa"),
            "state": os.getenv("RESTAURANT_STATE", "OK"),
        }

        # Search parameters
        self.search_radius_miles = float(os.getenv("EVENT_SEARCH_RADIUS", "5"))

        # API keys
        self.ticketmaster_key = os.getenv("TICKETMASTER_API_KEY")

        # Cache directory
        self.cache_dir = Path("data/events")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        if not self.ticketmaster_key:
            logger.warning(
                "⚠️ No TICKETMASTER_API_KEY found. Event fetching will be disabled."
            )

    # ========================================
    # PUBLIC METHODS (Used by ML Service)
    # ========================================

    def calculate_impact(self, timestamp: datetime) -> float:
        """
        Aggregates impact of ALL events for a specific time.
        This is the method ml_service calls.
        """
        try:
            # 1. Get all events for this date (Fast, from cache)
            events = self.get_events_for_date(timestamp, use_cache_only=True)

            if not events:
                return 0.0

            max_impact = 0.0

            # 2. Calculate impact for each event and find the biggest one
            for event in events:
                impact_data = self._calculate_single_event_impact(event, timestamp)
                if impact_data["impact_minutes"] > max_impact:
                    max_impact = impact_data["impact_minutes"]

            return float(max_impact)

        except Exception as e:
            logger.error(f"Error calculating aggregate impact: {e}")
            return 0.0

    def get_events_for_date(
        self, date_obj: datetime, use_cache_only: bool = False
    ) -> List[Dict]:
        """
        Get events for a specific date.
        """
        # 1. Check Cache
        cache_file = self.cache_dir / f"events_{date_obj.strftime('%Y%m%d')}.json"

        if cache_file.exists():
            try:
                with open(cache_file, "r") as f:
                    data = json.load(f)
                    return data.get("events", [])
            except Exception as e:
                logger.error(f"Cache read error: {e}")

        if use_cache_only:
            return []

        # 2. Fetch from API (If allowed)
        # Note: ticketmaster fetching requires start/end range
        return self.fetch_ticketmaster_events(date_obj, date_obj + timedelta(days=1))

    # ========================================
    # INTERNAL IMPACT LOGIC (Your original code)
    # ========================================

    def _calculate_single_event_impact(
        self, event: Dict, current_time: datetime
    ) -> Dict:
        """
        Your original calculate_event_impact logic.
        """
        try:
            # Parse event time safely
            event_datetime_str = event.get("event_datetime") or event.get("time")
            if not event_datetime_str:
                return {"impact_minutes": 0}

            # Handle 'Z' if present
            if event_datetime_str.endswith("Z"):
                event_datetime_str = event_datetime_str.replace("Z", "+00:00")

            event_datetime = datetime.fromisoformat(event_datetime_str)

            # Time proximity
            hours_until_event = (event_datetime - current_time).total_seconds() / 3600

            if -2 <= hours_until_event <= 2:
                time_factor = 1.0
            elif -3 <= hours_until_event <= 3:
                time_factor = 0.5
            else:
                time_factor = 0.1

            # Distance factor
            distance = event.get("distance_miles", 5)
            if distance < 0.5:
                distance_factor = 1.5
            elif distance < 1:
                distance_factor = 1.2
            elif distance < 3:
                distance_factor = 1.0
            elif distance < 5:
                distance_factor = 0.5
            else:
                distance_factor = 0.2

            # Event type factor
            event_type = event.get("event_type", "other")
            type_impact = {
                "sports": 15,
                "concert": 12,
                "festival": 10,
                "conference": 5,
                "other": 3,
            }.get(event_type, 3)

            # Attendance factor
            attendance = event.get("attendance_estimated", 1000)
            if attendance > 15000:
                attendance_factor = 1.5
            elif attendance > 5000:
                attendance_factor = 1.2
            elif attendance > 1000:
                attendance_factor = 1.0
            else:
                attendance_factor = 0.5

            impact_minutes = (
                type_impact * distance_factor * attendance_factor * time_factor
            )

            return {"impact_minutes": round(impact_minutes, 1)}

        except Exception as e:
            logger.error(f"Impact calc error: {e}")
            return {"impact_minutes": 0}

    # ========================================
    # TICKETMASTER API & HELPERS
    # ========================================

    def fetch_ticketmaster_events(
        self, start_date: datetime, end_date: datetime
    ) -> List[Dict]:
        if not self.ticketmaster_key:
            return []

        try:
            url = "https://app.ticketmaster.com/discovery/v2/events.json"
            params = {
                "apikey": self.ticketmaster_key,
                "latlong": f"{self.restaurant_location['lat']},{self.restaurant_location['lng']}",
                "radius": int(self.search_radius_miles),
                "unit": "miles",
                "startDateTime": start_date.strftime("%Y-%m-%dT00:00:00Z"),
                "endDateTime": end_date.strftime("%Y-%m-%dT23:59:59Z"),
                "size": 200,
                "sort": "date,asc",
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            events = []
            embedded = data.get("_embedded")

            if embedded and "events" in embedded:
                for event in embedded["events"]:
                    processed = self._process_ticketmaster_event(event)
                    if processed:
                        events.append(processed)

            # Cache results
            if events:
                self.save_events_to_cache(events, start_date)

            return events

        except Exception as e:
            logger.error(f"Error fetching Ticketmaster events: {e}")
            return []

    def _process_ticketmaster_event(self, event: Dict) -> Optional[Dict]:
        # Your existing processing logic...
        try:
            name = event.get("name", "Unknown")
            dates = event.get("dates", {})
            start = dates.get("start", {})

            if "localDate" not in start:
                return None

            event_dt_str = f"{start['localDate']} {start.get('localTime', '19:00:00')}"
            event_datetime = datetime.strptime(event_dt_str, "%Y-%m-%d %H:%M:%S")

            # Venue
            venues = event.get("_embedded", {}).get("venues", [])
            if not venues:
                return None
            venue = venues[0]

            # Distance
            v_lat = float(venue.get("location", {}).get("latitude", 0))
            v_lng = float(venue.get("location", {}).get("longitude", 0))
            distance = self._calculate_distance(
                self.restaurant_location["lat"],
                self.restaurant_location["lng"],
                v_lat,
                v_lng,
            )
            if distance > self.search_radius_miles:
                return None

            # Attendance
            attendance = self._estimate_attendance_by_venue(venue.get("name", ""))

            return {
                "event_name": name,
                "event_type": self._classify_event_type(event),
                "event_datetime": event_datetime.isoformat(),
                "event_date": event_datetime.date().isoformat(),
                "distance_miles": distance,
                "attendance_estimated": attendance,
                "venue_name": venue.get("name", "Unknown"),
            }
        except:
            return None

    def save_events_to_cache(self, events: List[Dict], date: datetime):
        cache_file = self.cache_dir / f"events_{date.strftime('%Y%m%d')}.json"
        with open(cache_file, "w") as f:
            json.dump({"events": events}, f, indent=2)

    # --- KEEP YOUR HELPER METHODS ---
    def _calculate_distance(self, lat1, lng1, lat2, lng2):
        R = 3959
        lat1_rad = radians(lat1)
        lng1_rad = radians(lng1)
        lat2_rad = radians(lat2)
        lng2_rad = radians(lng2)
        dlat = lat2_rad - lat1_rad
        dlng = lng2_rad - lng1_rad
        a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlng / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c

    def _estimate_attendance_by_venue(self, venue_name: str) -> int:
        venue_name_lower = venue_name.lower()
        if "bok center" in venue_name_lower:
            return 15000
        elif "cain" in venue_name_lower:
            return 1500
        elif "stadium" in venue_name_lower:
            return 20000
        return 1000

    def _classify_event_type(self, event: Dict) -> str:
        try:
            segment = event["classifications"][0]["segment"]["name"].lower()
            if "sport" in segment:
                return "sports"
            if "music" in segment:
                return "concert"
        except:
            pass
        return "other"


# Standalone run
if __name__ == "__main__":
    svc = EventService()
    print("Fetching...")
    events = svc.fetch_ticketmaster_events(
        datetime.now(), datetime.now() + timedelta(days=7)
    )
    print(f"Found {len(events)} events")
