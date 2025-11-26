from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Import your existing services
from app.services.event_service import EventService
from app.services.weather_service import WeatherService
from app.services.ml_service import predict_item_sales

router = APIRouter()

# Initialize services
event_service = EventService()
weather_service = WeatherService()

# --- 1. Dashboard Highlights ---
@router.get("/highlights")
async def get_dashboard_highlights():
    """
    Returns key events for the week (Powered by Ticketmaster)
    """
    today = datetime.now()
    
    # Get real events for the next 7 days
    events = event_service.fetch_ticketmaster_events(today, today + timedelta(days=7))
    
    highlights = []
    
    # Transform real events into UI cards
    for i, event in enumerate(events[:3]): # Top 3 only
        impact = event.get('attendance_estimated', 0)
        color = "red" if impact > 10000 else "blue"
        
        highlights.append({
            "id": i + 1,
            "title": event.get('event_name'),
            "icon": "Calendar",
            "color": color,
            "details": f"{event.get('venue_name')} - {event.get('distance_miles')}mi",
            "subDetails": f"Est. Attendance: {impact:,}",
            "importance": "high" if impact > 5000 else "medium"
        })
    
    # If no events, show a default card
    if not highlights:
        highlights.append({
            "id": 1,
            "title": "Quiet Week",
            "icon": "Sun",
            "color": "green",
            "details": "No major events nearby",
            "subDetails": "Standard prep levels",
            "importance": "low"
        })
        
    return highlights

# --- 2. Sales Chart Data ---
@router.get("/sales-chart")
async def get_sales_chart(week: str = "this-week"):
    """
    Returns simulated sales data enriched with ML predictions for future days
    """
    
    # Mocking the structure for now, but using realistic day names
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    chart_data = []
    
    for day in days:
        chart_data.append({
            "day": day,
            "thisWeek": 145 + (10 if day in ["Fri", "Sat"] else 0), # Simple logic
            "pastData": 120,
            "actual": 138 if day in ["Mon", "Tue"] else None # Only show actual for passed days
        })
        
    return chart_data

# --- 3. Metrics Grid ---
@router.get("/metrics")
async def get_metrics_grid():
    """
    Returns top sellers and KPI summaries
    """
    # connect this to your OrderItems table DB query
    return {
      "categories": [{
        "id": 1,
        "title": "Best Sellers",
        "icon": "ShoppingCart",
        "items": [{"name": "Burger Special", "value": "156", "trend": "up"}]
      }],
      "summaries": [{
        "id": 4,
        "title": "Labor Cost", 
        "percentage": "28.5%",
        "target": "30%",
        "status": "good"
      }],
      "purchasing": [{
        "item": "Produce",
        "estimate": "$1,850",
        "status": "Order Today"
      }]
    }

# --- 4. Info Sections (Weather/Events) ---
@router.get("/info-sections")
async def get_info_sections():
    """
    Aggregates Weather, Events, and Labor info
    """
    today = datetime.now()
    
    # 1. Get Real Weather
    weather_summary = {"current": "Unknown", "forecast": "Unknown", "impact": "Low"}
    try:
        forecast = weather_service.get_forecast(today)
        if forecast:
            condition = forecast.get('shortForecast', 'Clear')
            temp = forecast.get('temperature', 70)
            weather_summary = {
                "current": f"{condition}, {temp}°F",
                "forecast": "Clear week ahead", # Placeholder for full forecast logic
                "impact": "High Patio Impact" if temp > 60 and 'Rain' not in condition else "Low"
            }
    except:
        pass

    # 2. Get Real Events Summary
    events_list = []
    events = event_service.get_events_for_date(today)
    if events:
        top_event = events[0] # Closest/Biggest
        events_list.append({
            "date": "Today",
            "event": top_event.get('event_name'),
            "bookings": "High Demand" if top_event.get('attendance_estimated', 0) > 5000 else "Normal"
        })
    else:
        events_list.append({"date": "Today", "event": "No major events", "bookings": "Standard"})

    return {
      "events": events_list,
      "weather": weather_summary,
      "labor": {
        "predicted": 32,
        "planned": 30,
        "variance": "+2",
        "recommendation": "Add 1 server Saturday"
      },
      "historical": {
        "lastYear": "$42,500",
        "average": "$38,750", 
        "projection": "$41,200"
      }
    }

# --- 5. User Profile ---
@router.get("/user-profile")
async def get_user_profile():
    # Mock for now until Auth is built
    return {
      "name": "Manager",
      "restaurant": "Tulsa Capstone Grill"
    }