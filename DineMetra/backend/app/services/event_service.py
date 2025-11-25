"""
Dinemetra Event Data Service
Fetches events from Ticketmaster and other sources

This script:
1. Fetches events near restaurant location
2. Categorizes and scores events by impact
3. Stores event data for predictions
4. Provides event data to ML models

Run: python scripts/fetch_events.py
"""

import requests
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import logging
from math import radians, sin, cos, sqrt, atan2

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class EventDataService:
    """
    Manages fetching and processing event data from external APIs
    """

    def __init__(self, config_path: str = ".env"):
        """
        Initialize event service

        Args:
            config_path: Path to .env file with API keys
        """
        # Load environment variables
        from dotenv import load_dotenv

        load_dotenv(config_path)

        # Restaurant location (Tulsa, OK - adjust to your actual location)
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
        self.weather_key = os.getenv("OPENWEATHER_API_KEY")

        # Cache directory
        self.cache_dir = Path("data/events")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        logger.info(
            f"Event service initialized for {self.restaurant_location['city']}, {self.restaurant_location['state']}"
        )
        logger.info(f"Search radius: {self.search_radius_miles} miles")

    # ========================================
    # TICKETMASTER API
    # ========================================

    def fetch_ticketmaster_events(
        self, start_date: datetime, end_date: datetime
    ) -> List[Dict]:
        """
        Fetch events from Ticketmaster API

        Args:
            start_date: Start of date range
            end_date: End of date range

        Returns:
            List of event dictionaries
        """
        if not self.ticketmaster_key:
            logger.warning("Ticketmaster API key not found in environment variables")
            return []

        logger.info(
            f"Fetching Ticketmaster events from {start_date.date()} to {end_date.date()}..."
        )

        try:
            url = "https://app.ticketmaster.com/discovery/v2/events.json"

            params = {
                "apikey": self.ticketmaster_key,
                "latlong": f"{self.restaurant_location['lat']},{self.restaurant_location['lng']}",
                "radius": int(self.search_radius_miles),
                "unit": "miles",
                "startDateTime": start_date.strftime("%Y-%m-%dT00:00:00Z"),
                "endDateTime": end_date.strftime("%Y-%m-%dT23:59:59Z"),
                "size": 200,  # Max events per request
                "sort": "date,asc",
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            events = []
            embedded = data.get("_embedded")

            if not embedded or "events" not in embedded:
                logger.info("No events found in date range")
                return []

            for event in embedded["events"]:
                processed_event = self._process_ticketmaster_event(event)
                if processed_event:
                    events.append(processed_event)

            logger.info(f"✓ Found {len(events)} events")
            return events

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching Ticketmaster events: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error processing Ticketmaster data: {e}")
            return []

    def _process_ticketmaster_event(self, event: Dict) -> Optional[Dict]:
        """
        Process a single Ticketmaster event into our format

        Args:
            event: Raw event data from Ticketmaster API

        Returns:
            Processed event dictionary or None if invalid
        """
        try:
            # Extract basic info
            event_name = event.get("name", "Unknown Event")

            # Get dates - Ticketmaster can have complex date structures
            dates = event.get("dates", {})
            start = dates.get("start", {})

            # Try to get local date/time
            if "localDate" in start:
                event_date = start["localDate"]
                event_time = start.get("localTime", "19:00:00")  # Default to 7pm
                event_datetime = datetime.strptime(
                    f"{event_date} {event_time}", "%Y-%m-%d %H:%M:%S"
                )
            else:
                logger.warning(f"No date found for event: {event_name}")
                return None

            # Get venue info
            venues = event.get("_embedded", {}).get("venues", [])
            if not venues:
                logger.warning(f"No venue found for event: {event_name}")
                return None

            venue = venues[0]
            venue_name = venue.get("name", "Unknown Venue")

            # Get venue location
            venue_location = venue.get("location", {})
            venue_lat = float(venue_location.get("latitude", 0))
            venue_lng = float(venue_location.get("longitude", 0))

            if venue_lat == 0 or venue_lng == 0:
                logger.warning(f"No valid coordinates for venue: {venue_name}")
                return None

            # Calculate distance from restaurant
            distance_miles = self._calculate_distance(
                self.restaurant_location["lat"],
                self.restaurant_location["lng"],
                venue_lat,
                venue_lng,
            )

            # Skip if too far
            if distance_miles > self.search_radius_miles:
                return None

            # Get venue capacity (estimate attendance)
            capacity = venue.get("capacity")
            if capacity:
                try:
                    attendance_estimated = int(capacity) * 0.8  # Assume 80% capacity
                except:
                    attendance_estimated = self._estimate_attendance_by_venue(
                        venue_name
                    )
            else:
                attendance_estimated = self._estimate_attendance_by_venue(venue_name)

            # Classify event type
            event_type = self._classify_event_type(event)

            # Get price range (optional, for context)
            price_ranges = event.get("priceRanges", [])
            price_min = price_ranges[0].get("min", 0) if price_ranges else 0
            price_max = price_ranges[0].get("max", 0) if price_ranges else 0

            # Get event URL
            event_url = event.get("url", "")

            # Get images
            images = event.get("images", [])
            image_url = images[0].get("url", "") if images else ""

            processed = {
                "event_name": event_name,
                "event_type": event_type,
                "event_date": event_datetime.date().isoformat(),
                "event_time": event_datetime.time().isoformat(),
                "event_datetime": event_datetime.isoformat(),
                "venue_name": venue_name,
                "venue_lat": venue_lat,
                "venue_lng": venue_lng,
                "distance_miles": round(distance_miles, 2),
                "attendance_estimated": int(attendance_estimated),
                "price_min": price_min,
                "price_max": price_max,
                "event_url": event_url,
                "image_url": image_url,
                "source": "ticketmaster",
                "fetched_at": datetime.now().isoformat(),
            }

            return processed

        except Exception as e:
            logger.error(f"Error processing event: {e}")
            return None

    def _classify_event_type(self, event: Dict) -> str:
        """
        Classify event type from Ticketmaster classifications

        Args:
            event: Raw event data

        Returns:
            Event type string (sports, concert, festival, etc.)
        """
        classifications = event.get("classifications", [])
        if not classifications:
            return "other"

        classification = classifications[0]

        # Check segment (broadest category)
        segment = classification.get("segment", {}).get("name", "").lower()
        if "sport" in segment:
            return "sports"
        elif "music" in segment:
            return "concert"
        elif "arts" in segment or "theatre" in segment:
            return "concert"  # Treat theatre like concerts for impact
        elif "family" in segment:
            return "festival"

        # Check genre (more specific)
        genre = classification.get("genre", {}).get("name", "").lower()
        if "basketball" in genre or "football" in genre or "hockey" in genre:
            return "sports"
        elif "rock" in genre or "pop" in genre or "country" in genre:
            return "concert"

        return "other"

    def _estimate_attendance_by_venue(self, venue_name: str) -> int:
        """
        Estimate attendance based on known venue capacities

        Args:
            venue_name: Name of venue

        Returns:
            Estimated attendance
        """
        venue_name_lower = venue_name.lower()

        # Tulsa-specific venues (adjust for your city)
        if "bok center" in venue_name_lower or "paycom" in venue_name_lower:
            return 15000  # Large arena
        elif "cain" in venue_name_lower:
            return 1500  # Cain's Ballroom
        elif "brady" in venue_name_lower:
            return 3000  # Brady Theater
        elif "stadium" in venue_name_lower:
            return 20000  # Stadium
        elif "amphitheater" in venue_name_lower or "amphitheatre" in venue_name_lower:
            return 8000
        elif "convention center" in venue_name_lower:
            return 5000
        elif "arena" in venue_name_lower:
            return 10000
        elif "theater" in venue_name_lower or "theatre" in venue_name_lower:
            return 2000
        else:
            return 1000  # Small venue default

    def _calculate_distance(
        self, lat1: float, lng1: float, lat2: float, lng2: float
    ) -> float:
        """
        Calculate distance between two coordinates using Haversine formula

        Args:
            lat1, lng1: First coordinate
            lat2, lng2: Second coordinate

        Returns:
            Distance in miles
        """
        R = 3959  # Earth's radius in miles

        lat1_rad = radians(lat1)
        lng1_rad = radians(lng1)
        lat2_rad = radians(lat2)
        lng2_rad = radians(lng2)

        dlat = lat2_rad - lat1_rad
        dlng = lng2_rad - lng1_rad

        a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlng / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return R * c

    # ========================================
    # EVENT SCORING & IMPACT
    # ========================================

    def calculate_event_impact(self, event: Dict, current_time: datetime) -> Dict:
        """
        Calculate the impact score of an event on restaurant traffic

        Args:
            event: Event dictionary
            current_time: Current datetime for time-based calculations

        Returns:
            Dictionary with impact scores and factors
        """
        event_datetime = datetime.fromisoformat(event["event_datetime"])

        # Time proximity (events impact 2 hours before and after)
        hours_until_event = (event_datetime - current_time).total_seconds() / 3600

        if -2 <= hours_until_event <= 2:
            time_factor = 1.0  # Peak impact
        elif -3 <= hours_until_event <= 3:
            time_factor = 0.5  # Moderate impact
        else:
            time_factor = 0.1  # Minimal impact

        # Distance factor
        distance = event["distance_miles"]
        if distance < 0.5:
            distance_factor = 1.5  # Right next door - huge impact
        elif distance < 1:
            distance_factor = 1.2  # Walking distance
        elif distance < 3:
            distance_factor = 1.0  # Short drive
        elif distance < 5:
            distance_factor = 0.5  # Nearby
        else:
            distance_factor = 0.2  # Far away

        # Event type factor
        event_type = event["event_type"]
        type_impact = {
            "sports": 15,  # Sports events = big restaurant traffic
            "concert": 12,  # Concerts = moderate-high traffic
            "festival": 10,  # Festivals = moderate traffic
            "conference": 5,  # Conferences = low-moderate traffic
            "other": 3,  # Other events = minimal traffic
        }.get(event_type, 3)

        # Attendance factor
        attendance = event["attendance_estimated"]
        if attendance > 15000:
            attendance_factor = 1.5
        elif attendance > 5000:
            attendance_factor = 1.2
        elif attendance > 1000:
            attendance_factor = 1.0
        else:
            attendance_factor = 0.5

        # Calculate total impact (in additional wait time minutes)
        impact_minutes = type_impact * distance_factor * attendance_factor * time_factor

        return {
            "impact_minutes": round(impact_minutes, 1),
            "impact_level": (
                "high"
                if impact_minutes > 10
                else "medium" if impact_minutes > 5 else "low"
            ),
            "time_factor": time_factor,
            "distance_factor": distance_factor,
            "attendance_factor": attendance_factor,
            "hours_until_event": round(hours_until_event, 1),
        }

    # ========================================
    # DATA MANAGEMENT
    # ========================================

    def save_events_to_cache(self, events: List[Dict], date: datetime):
        """
        Save fetched events to cache file

        Args:
            events: List of event dictionaries
            date: Date for cache file naming
        """
        cache_file = self.cache_dir / f"events_{date.strftime('%Y%m%d')}.json"

        with open(cache_file, "w") as f:
            json.dump(
                {
                    "date": date.isoformat(),
                    "event_count": len(events),
                    "events": events,
                },
                f,
                indent=2,
            )

        logger.info(f"✓ Cached {len(events)} events to {cache_file}")

    def load_events_from_cache(self, date: datetime) -> List[Dict]:
        """
        Load events from cache file

        Args:
            date: Date to load events for

        Returns:
            List of events or empty list if not cached
        """
        cache_file = self.cache_dir / f"events_{date.strftime('%Y%m%d')}.json"

        if not cache_file.exists():
            return []

        try:
            with open(cache_file, "r") as f:
                data = json.load(f)
                return data.get("events", [])
        except Exception as e:
            logger.error(f"Error loading cache: {e}")
            return []

    def get_events_for_date(self, date: datetime, use_cache: bool = True) -> List[Dict]:
        """
        Get events for a specific date (from cache or API)

        Args:
            date: Date to get events for
            use_cache: Whether to use cached data if available

        Returns:
            List of events
        """
        # Check cache first
        if use_cache:
            cached_events = self.load_events_from_cache(date)
            if cached_events:
                logger.info(f"Loaded {len(cached_events)} events from cache")
                return cached_events

        # Fetch from API
        events = self.fetch_ticketmaster_events(date, date + timedelta(days=1))

        # Cache for future use
        if events:
            self.save_events_to_cache(events, date)

        return events

    def get_relevant_event_for_time(self, timestamp: datetime) -> Optional[Dict]:
        """
        Get the most relevant event for a given timestamp

        Args:
            timestamp: Time to check for events

        Returns:
            Most impactful event or None
        """
        # Get events for that date
        events = self.get_events_for_date(timestamp)

        if not events:
            return None

        # Calculate impact for each event
        scored_events = []
        for event in events:
            impact = self.calculate_event_impact(event, timestamp)
            if impact["impact_minutes"] > 1:  # Only consider events with >1 min impact
                scored_events.append({**event, "impact": impact})

        # Return highest impact event
        if scored_events:
            return max(scored_events, key=lambda e: e["impact"]["impact_minutes"])

        return None


# ========================================
# STANDALONE SCRIPT
# ========================================


def main():
    """
    Fetch events for the next 30 days
    """
    logger.info("=" * 60)
    logger.info("🎫 Dinemetra Event Data Fetcher")
    logger.info("=" * 60)

    service = EventDataService()

    # Fetch events for next 30 days
    start_date = datetime.now()
    end_date = start_date + timedelta(days=30)

    logger.info(f"\nFetching events from {start_date.date()} to {end_date.date()}...")
    events = service.fetch_ticketmaster_events(start_date, end_date)

    if events:
        # Save to cache
        service.save_events_to_cache(events, start_date)

        # Display summary
        logger.info(f"\n📊 Event Summary:")
        logger.info(f"   Total events: {len(events)}")

        by_type = {}
        for event in events:
            event_type = event["event_type"]
            by_type[event_type] = by_type.get(event_type, 0) + 1

        logger.info(f"\n   By Type:")
        for event_type, count in sorted(
            by_type.items(), key=lambda x: x[1], reverse=True
        ):
            logger.info(f"      {event_type.capitalize()}: {count}")

        # Show top 5 closest events
        logger.info(f"\n   📍 Top 5 Closest Events:")
        sorted_events = sorted(events, key=lambda e: e["distance_miles"])[:5]
        for event in sorted_events:
            logger.info(
                f"      {event['event_name']} - {event['distance_miles']}mi - {event['event_date']}"
            )

        # Show top 5 biggest events
        logger.info(f"\n   🎪 Top 5 Largest Events:")
        sorted_events = sorted(
            events, key=lambda e: e["attendance_estimated"], reverse=True
        )[:5]
        for event in sorted_events:
            logger.info(
                f"      {event['event_name']} - {event['attendance_estimated']:,} people - {event['event_date']}"
            )
    else:
        logger.warning("\n⚠️  No events found")

    logger.info("\n" + "=" * 60)
    logger.info("✅ Event fetch complete!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
