"""
External Events Data Service
Fetches and processes data about nearby events that impact restaurant traffic
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests
import os


class EventDataService:
    """
    Manages fetching and caching event data from external sources
    """

    def __init__(self):
        self.restaurant_location = {
            "lat": 36.1540,  # Tulsa, OK coordinates
            "lng": -95.9928,
            "city": "Tulsa",
        }
        self.search_radius_miles = 5  # Only care about nearby events

        # API keys (set these in .env)
        self.ticketmaster_key = os.getenv("TICKETMASTER_API_KEY")
        self.sportsdata_key = os.getenv("SPORTSDATA_API_KEY")
        self.weather_key = os.getenv("OPENWEATHER_API_KEY")

    def get_events_for_date(self, date: datetime) -> List[Dict]:
        """
        Get all events happening on a specific date near the restaurant

        Returns list of events with:
        - event_name
        - event_type (sports, concert, festival, etc)
        - event_time
        - event_attendance_estimated
        - event_distance_miles
        """
        events = []

        # Fetch from multiple sources
        events.extend(self._fetch_ticketmaster_events(date))
        events.extend(self._fetch_sports_events(date))
        # Add more sources as needed

        # Filter by distance
        events = [
            e
            for e in events
            if e.get("event_distance_miles", 0) < self.search_radius_miles
        ]

        return events

    def _fetch_ticketmaster_events(self, date: datetime) -> List[Dict]:
        """Fetch concerts/events from Ticketmaster API"""
        if not self.ticketmaster_key:
            return []

        try:
            url = "https://app.ticketmaster.com/discovery/v2/events.json"
            params = {
                "apikey": self.ticketmaster_key,
                "latlong": f"{self.restaurant_location['lat']},{self.restaurant_location['lng']}",
                "radius": self.search_radius_miles,
                "unit": "miles",
                "localStartDateTime": f"{date.date()}T00:00:00",
                "localEndDateTime": f"{date.date()}T23:59:59",
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            events = []
            for event in data.get("_embedded", {}).get("events", []):
                events.append(
                    {
                        "event_name": event.get("name"),
                        "event_type": self._classify_event_type(event),
                        "event_time": datetime.fromisoformat(
                            event["dates"]["start"]["localTime"]
                        ),
                        "event_attendance_estimated": self._estimate_attendance(event),
                        "event_distance_miles": self._calculate_distance(event),
                        "venue_name": event.get("_embedded", {})
                        .get("venues", [{}])[0]
                        .get("name"),
                    }
                )

            return events

        except Exception as e:
            print(f"Error fetching Ticketmaster events: {e}")
            return []

    def _fetch_sports_events(self, date: datetime) -> List[Dict]:
        """Fetch sports games (Thunder, Tulsa FC, college sports)"""
        # Placeholder - implement with SportsData.io or similar
        # For now, return empty list
        return []

    def _classify_event_type(self, event_data: Dict) -> str:
        """Determine if event is sports, concert, festival, etc"""
        classifications = event_data.get("classifications", [{}])[0]
        segment = classifications.get("segment", {}).get("name", "").lower()

        if "sport" in segment:
            return "sports"
        elif "music" in segment or "concert" in segment:
            return "concert"
        elif "arts" in segment or "theatre" in segment:
            return "concert"
        else:
            return "festival"

    def _estimate_attendance(self, event_data: Dict) -> int:
        """Estimate attendance based on venue capacity"""
        venue = event_data.get("_embedded", {}).get("venues", [{}])[0]
        capacity = venue.get("capacity")

        if capacity:
            return int(capacity * 0.8)  # Assume 80% capacity

        # Default estimates by venue type
        venue_name = venue.get("name", "").lower()
        if "bok center" in venue_name:
            return 15000
        elif "arena" in venue_name:
            return 10000
        elif "stadium" in venue_name:
            return 20000
        else:
            return 5000  # Default small venue

    def _calculate_distance(self, event_data: Dict) -> float:
        """Calculate distance from restaurant to event venue"""
        venue = event_data.get("_embedded", {}).get("venues", [{}])[0]
        venue_location = venue.get("location", {})

        venue_lat = float(venue_location.get("latitude", 0))
        venue_lng = float(venue_location.get("longitude", 0))

        # Simple distance calculation (Haversine formula)
        from math import radians, sin, cos, sqrt, atan2

        R = 3959  # Earth's radius in miles

        lat1, lng1 = radians(self.restaurant_location["lat"]), radians(
            self.restaurant_location["lng"]
        )
        lat2, lng2 = radians(venue_lat), radians(venue_lng)

        dlat = lat2 - lat1
        dlng = lng2 - lng1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlng / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return R * c

    def get_weather_for_date(self, date: datetime) -> Dict:
        """Fetch weather forecast for a date"""
        if not self.weather_key:
            return {}

        try:
            url = "https://api.openweathermap.org/data/2.5/forecast"
            params = {
                "lat": self.restaurant_location["lat"],
                "lon": self.restaurant_location["lng"],
                "appid": self.weather_key,
                "units": "imperial",
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Find forecast closest to the requested date
            for forecast in data.get("list", []):
                forecast_time = datetime.fromtimestamp(forecast["dt"])
                if forecast_time.date() == date.date():
                    return {
                        "weather_condition": forecast["weather"][0]["main"].lower(),
                        "temperature_high_f": forecast["main"]["temp_max"],
                        "temperature_low_f": forecast["main"]["temp_min"],
                        "precipitation_inches": forecast.get("rain", {}).get("3h", 0)
                        / 25.4,  # mm to inches
                    }

            return {}

        except Exception as e:
            print(f"Error fetching weather: {e}")
            return {}


# Global instance
event_service = EventDataService()
