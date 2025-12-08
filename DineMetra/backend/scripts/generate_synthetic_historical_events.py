"""
Generate Synthetic Historical Events for Jan-Jun 2025
Based on typical BOK Center event patterns
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
import random

# Typical BOK Center event types and patterns
EVENT_TEMPLATES = {
    'Tulsa Oilers Hockey': {
        'venue': 'BOK Center',
        'attendance': 7500,
        'distance': 0.4,
        'category': 'Sports',
        'frequency': 'weekly',  # Typically 2-3 games per week during season
        'season_months': [1, 2, 3, 4]  # Jan-Apr hockey season
    },
    'Concert': {
        'venue': 'BOK Center',
        'attendance': 12000,
        'distance': 0.4,
        'category': 'Music',
        'frequency': 'monthly',
        'artists': [
            'Luke Bryan', 'Carrie Underwood', 'Morgan Wallen',
            'George Strait', 'Kane Brown', 'Chris Stapleton',
            'Blake Shelton', 'Thomas Rhett', 'Jason Aldean'
        ]
    },
    'Family Show': {
        'venue': 'BOK Center',
        'attendance': 8000,
        'distance': 0.4,
        'category': 'Family',
        'shows': [
            'Disney On Ice', 'Monster Jam', 'Harlem Globetrotters',
            'WWE Live', 'Cirque du Soleil'
        ]
    },
    'Comedy Show': {
        'venue': 'Cains Ballroom',
        'attendance': 1200,
        'distance': 1.2,
        'category': 'Comedy',
        'comedians': [
            'Bill Burr', 'Jim Gaffigan', 'Sebastian Maniscalco',
            'Trevor Noah', 'Jo Koy'
        ]
    },
    'Local Concert': {
        'venue': 'Cains Ballroom',
        'attendance': 800,
        'distance': 1.2,
        'category': 'Music',
        'frequency': 'weekly'
    }
}


def generate_hockey_games(start_date, end_date):
    """Generate Tulsa Oilers hockey games (home games)"""
    events = []
    
    current = start_date
    game_number = 1
    
    # Hockey season: Jan-Apr, typically Tue/Thu/Sat games
    while current <= end_date:
        if current.month in [1, 2, 3, 4]:
            # Schedule home games on Tue, Thu, Sat
            if current.weekday() in [1, 3, 5]:  # Tue=1, Thu=3, Sat=5
                # Not every week, about 70% of the time
                if random.random() < 0.7:
                    opponent = random.choice([
                        'Kansas City Mavericks', 'Wichita Thunder',
                        'Allen Americans', 'Idaho Steelheads',
                        'Utah Grizzlies', 'Rapid City Rush'
                    ])
                    
                    events.append({
                        'event_name': f'Tulsa Oilers vs {opponent} - Game {game_number}',
                        'event_date': current.strftime('%Y-%m-%d'),
                        'event_time': '19:00:00',
                        'event_datetime': f"{current.strftime('%Y-%m-%d')}T19:00:00",
                        'venue_name': 'BOK Center',
                        'venue_capacity': 9000,
                        'attendance_estimated': random.randint(6000, 8500),
                        'distance_miles': 0.4,
                        'category': 'Sports'
                    })
                    game_number += 1
        
        current += timedelta(days=1)
    
    return events


def generate_concerts(start_date, end_date):
    """Generate concert events"""
    events = []
    
    artists = EVENT_TEMPLATES['Concert']['artists']
    
    # 1-2 major concerts per month
    current = start_date
    while current <= end_date:
        # Generate 1-2 concerts per month
        for _ in range(random.randint(1, 2)):
            # Random day in the month, prefer Fri/Sat
            day = random.randint(1, 28)
            concert_date = current.replace(day=day)
            
            if concert_date <= end_date:
                artist = random.choice(artists)
                
                events.append({
                    'event_name': f'{artist}',
                    'event_date': concert_date.strftime('%Y-%m-%d'),
                    'event_time': '19:30:00',
                    'event_datetime': f"{concert_date.strftime('%Y-%m-%d')}T19:30:00",
                    'venue_name': 'BOK Center',
                    'venue_capacity': 18000,
                    'attendance_estimated': random.randint(10000, 15000),
                    'distance_miles': 0.4,
                    'category': 'Music'
                })
        
        # Move to next month
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1, day=1)
        else:
            current = current.replace(month=current.month + 1, day=1)
    
    return events


def generate_family_shows(start_date, end_date):
    """Generate family shows"""
    events = []
    
    shows = EVENT_TEMPLATES['Family Show']['shows']
    
    # Distribute across months
    months = []
    current = start_date
    while current <= end_date:
        months.append(current)
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1, day=1)
        else:
            current = current.replace(month=current.month + 1, day=1)
    
    # 1 family show every 2 months
    for i, month in enumerate(months):
        if i % 2 == 0 and i < len(shows):
            show_date = month.replace(day=random.randint(10, 20))
            
            if show_date <= end_date:
                events.append({
                    'event_name': shows[i // 2],
                    'event_date': show_date.strftime('%Y-%m-%d'),
                    'event_time': '14:00:00',
                    'event_datetime': f"{show_date.strftime('%Y-%m-%d')}T14:00:00",
                    'venue_name': 'BOK Center',
                    'venue_capacity': 12000,
                    'attendance_estimated': random.randint(7000, 10000),
                    'distance_miles': 0.4,
                    'category': 'Family'
                })
    
    return events


def generate_local_events(start_date, end_date):
    """Generate smaller local venue events"""
    events = []
    
    current = start_date
    
    # Local shows at Cain's Ballroom - about once a week
    while current <= end_date:
        if current.weekday() in [4, 5]:  # Fri/Sat
            if random.random() < 0.5:  # 50% chance
                band_types = [
                    'Indie Rock Band', 'Country Artist', 'Blues Band',
                    'Jazz Ensemble', 'Local Artist Showcase'
                ]
                
                events.append({
                    'event_name': random.choice(band_types),
                    'event_date': current.strftime('%Y-%m-%d'),
                    'event_time': '20:00:00',
                    'event_datetime': f"{current.strftime('%Y-%m-%d')}T20:00:00",
                    'venue_name': 'Cains Ballroom',
                    'venue_capacity': 1300,
                    'attendance_estimated': random.randint(600, 1100),
                    'distance_miles': 1.2,
                    'category': 'Music'
                })
        
        current += timedelta(days=1)
    
    return events


def main():
    print("🎭 GENERATING SYNTHETIC HISTORICAL EVENTS")
    print("=" * 60)
    print("Period: January 2025 - June 2025")
    print("Based on typical Tulsa event patterns")
    print()
    
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 6, 30)
    
    all_events = []
    
    print("Generating hockey games...")
    hockey = generate_hockey_games(start_date, end_date)
    all_events.extend(hockey)
    print(f"  ✓ {len(hockey)} games")
    
    print("Generating concerts...")
    concerts = generate_concerts(start_date, end_date)
    all_events.extend(concerts)
    print(f"  ✓ {len(concerts)} concerts")
    
    print("Generating family shows...")
    family = generate_family_shows(start_date, end_date)
    all_events.extend(family)
    print(f"  ✓ {len(family)} family shows")
    
    print("Generating local events...")
    local = generate_local_events(start_date, end_date)
    all_events.extend(local)
    print(f"  ✓ {len(local)} local events")
    
    # Sort by date
    all_events.sort(key=lambda x: x['event_date'])
    
    print()
    print("=" * 60)
    print(f"✅ Total Events Generated: {len(all_events)}")
    print("=" * 60)
    
    # Save
    output_dir = Path("data/events")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "historical_events_2025_jan_jun.json"
    
    with open(output_file, 'w') as f:
        json.dump({
            'period': 'January 2025 - June 2025',
            'total_events': len(all_events),
            'source': 'synthetic_based_on_typical_patterns',
            'events': all_events,
            'generated_at': datetime.now().isoformat()
        }, f, indent=2)
    
    print(f"💾 Saved to: {output_file}")
    print()
    
    # Statistics
    from collections import defaultdict, Counter
    
    by_month = defaultdict(int)
    by_category = Counter()
    by_venue = Counter()
    
    for event in all_events:
        month = event['event_date'][:7]
        by_month[month] += 1
        by_category[event['category']] += 1
        by_venue[event['venue_name']] += 1
    
    print("📊 Events by Month:")
    for month in sorted(by_month.keys()):
        print(f"  {month}: {by_month[month]} events")
    
    print("\n📊 Events by Category:")
    for category, count in by_category.most_common():
        print(f"  {category}: {count} events")
    
    print("\n��️ Events by Venue:")
    for venue, count in by_venue.most_common():
        print(f"  {venue}: {count} events")
    
    print()
    print("✅ Synthetic events generated!")
    print("\nThese events are realistic based on:")
    print("  • Tulsa Oilers hockey schedule patterns")
    print("  • BOK Center typical booking frequency")
    print("  • Cain's Ballroom local show patterns")
    print("\nNext: Merge with sales data")
    print("  python scripts/merge_events_with_sales.py")


if __name__ == "__main__":
    main()
