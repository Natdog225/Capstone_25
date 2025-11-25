"""
Test weather.gov integration
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.weather_service import WeatherService

def test_weather():
    """Test weather service"""
    print("🧪 Testing Weather.gov Integration\n")
    
    service = WeatherService(lat=36.1540, lng=-95.9928)
    
    # Test current weather
    print("📊 Current Weather:")
    current = service.get_current_weather()
    if current:
        temp = current.get('temperature_f')
        print(f"   Temperature: {temp}°F" if temp else "   Temperature: N/A")
        print(f"   Condition: {current.get('condition', 'Unknown')}")
        print(f"   Humidity: {current.get('humidity', 'N/A')}%")
        print(f"   Station: {current.get('station', 'N/A')}")
    else:
        print("   ⚠️  Could not fetch current weather")
    
    # Test forecast
    print("\n📅 7-Day Forecast:")
    forecasts = service.get_forecast(days=7)
    
    if forecasts:
        for forecast in forecasts:
            impact = service.calculate_weather_impact(forecast)
            high = forecast.get('temperature_high_f', 'N/A')
            low = forecast.get('temperature_low_f', 'N/A')
            short = forecast.get('short_forecast', 'No description')
            
            print(f"   {forecast['date']}: {short}")
            print(f"      High: {high}°F / Low: {low}°F" if high != 'N/A' else f"      Temp: N/A")
            print(f"      Condition: {forecast.get('condition', 'unknown')}")
            print(f"      Impact: {impact:+.1f} minutes")
            print()
    else:
        print("   ⚠️  Could not fetch forecast")
    
    print("✅ Weather service test complete!")

if __name__ == "__main__":
    test_weather()