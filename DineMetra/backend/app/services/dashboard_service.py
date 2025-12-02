"""
Dashboard Service - Integrated with DineMetra
Aggregates data from all your existing services for dashboard display
"""
from typing import Dict, List
from datetime import datetime, timedelta
import logging

from app.services.enhanced_prediction_service import enhanced_prediction_service
from app.services.weather_service import WeatherService
from app.services.event_service import EventService

logger = logging.getLogger(__name__)


class DashboardService:
    """Service to aggregate dashboard data from all sources"""
    
    def __init__(self):
        self.prediction_service = enhanced_prediction_service
        self.weather_service = WeatherService()
        self.event_service = EventService()
    
    def get_highlights(self) -> List[Dict]:
        """Get this week's highlights for dashboard cards"""
        highlights = []
        
        try:
            today = datetime.now()
            
            # Get major events this week from event service
            events = self.event_service.fetch_ticketmaster_events(
                today, 
                today + timedelta(days=7)
            )
            
            if events:
                # Top 2 events
                for i, event in enumerate(events[:2]):
                    attendance = event.get('attendance_estimated', 0)
                    distance = event.get('distance_miles', 0)
                    
                    highlights.append({
                        'id': f"event_{i}",
                        'title': 'Big Event',
                        'icon': 'Calendar',
                        'color': 'red' if attendance > 10000 else 'blue',
                        'details': event.get('event_name', 'Upcoming Event'),
                        'subDetails': f"{event.get('venue_name')} - {distance:.1f}mi | Est. {attendance:,} attendees",
                        'importance': 'high' if attendance > 5000 else 'medium',
                        'date': event.get('event_date')
                    })
            
            # Check for weather alerts from YOUR weather service
            forecast = self.weather_service.get_forecast(days=7)
            if forecast:
                for day_forecast in forecast[:3]:  # Next 3 days
                    condition = day_forecast.get('condition', '').lower()
                    precip = day_forecast.get('precipitation_chance', 0)
                    temp_high = day_forecast.get('temperature_high_f')
                    
                    # Alert for severe weather
                    if condition in ['rainy', 'snowy', 'stormy'] and precip > 60:
                        highlights.append({
                            'id': f"weather_{day_forecast['date']}",
                            'title': 'Weather Alert',
                            'icon': 'Cloud',
                            'color': 'orange',
                            'details': f"{condition.title()} expected - {precip}% precipitation",
                            'subDetails': f"High: {temp_high}°F - Monitor patio seating",
                            'importance': 'high',
                            'date': day_forecast['date']
                        })
                        break  # Only show first alert
                    
                    # Alert for extreme temperatures
                    if temp_high and (temp_high > 95 or temp_high < 32):
                        highlights.append({
                            'id': f"temp_{day_forecast['date']}",
                            'title': 'Temperature Alert',
                            'icon': 'Thermometer',
                            'color': 'yellow',
                            'details': f"Extreme temperature: {temp_high}°F",
                            'subDetails': "Consider patio availability",
                            'importance': 'medium',
                            'date': day_forecast['date']
                        })
                        break
            
            # Check for peak business days
            for i in range(7):
                check_date = today + timedelta(days=i)
                if check_date.weekday() in [4, 5]:  # Friday or Saturday
                    busyness = self.prediction_service.predict_busyness_enhanced(
                        check_date.replace(hour=19)
                    )
                    if busyness.get('percentage', 0) > 75:
                        highlights.append({
                            'id': f'peak_{check_date.strftime("%Y%m%d")}',
                            'title': 'Peak Business',
                            'icon': 'TrendingUp',
                            'color': 'green',
                            'details': f"{check_date.strftime('%A')} Evening",
                            'subDetails': f"Expected: {busyness.get('level')} - {busyness.get('expected_guests')} guests",
                            'importance': 'high',
                            'date': check_date.strftime('%Y-%m-%d')
                        })
                        break
            
            # Default if no highlights
            if not highlights:
                highlights.append({
                    'id': 'steady_week',
                    'title': 'Steady Week',
                    'icon': 'Check',
                    'color': 'blue',
                    'details': 'No major events or alerts',
                    'subDetails': 'Business as usual expected',
                    'importance': 'low'
                })
            
            return highlights[:3]  # Max 3 highlights
            
        except Exception as e:
            logger.error(f"Error getting highlights: {e}")
            return [{
                'id': 'error',
                'title': 'Dashboard Update',
                'icon': 'Info',
                'color': 'gray',
                'details': 'Unable to load highlights',
                'subDetails': 'Please refresh',
                'importance': 'low'
            }]
    
    def get_sales_chart_data(self, period: str = 'this-week') -> List[Dict]:
        """Get sales chart data for visualization"""
        try:
            today = datetime.now()
            chart_data = []
            
            # Get date range
            if period == 'this-week':
                start_date = today - timedelta(days=today.weekday())
            elif period == 'last-week':
                start_date = today - timedelta(days=today.weekday() + 7)
            else:
                start_date = today - timedelta(days=7)
            
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            
            for i in range(7):
                current_day = start_date + timedelta(days=i)
                is_past = current_day.date() <= today.date()
                
                # Simplified - connect this to actual sales database
                base_sales = 145
                if current_day.weekday() in [4, 5]:  # Weekend boost
                    base_sales = 195
                elif current_day.weekday() == 6:  # Sunday
                    base_sales = 175
                
                chart_data.append({
                    'day': days[i],
                    'date': current_day.strftime('%Y-%m-%d'),
                    'thisWeek': base_sales if not is_past else base_sales + 10,
                    'pastData': int(base_sales * 0.9),  # Last week comparison
                    'actual': base_sales + 10 if is_past else None,
                    'isPrediction': not is_past
                })
            
            return chart_data
            
        except Exception as e:
            logger.error(f"Error getting sales chart data: {e}")
            return []
    
    def get_metrics(self) -> Dict:
        """Get all metrics for dashboard"""
        try:
            return {
                'categories': self._get_metric_categories(),
                'summaries': self._get_metric_summaries(),
                'purchasing': self._get_purchasing_estimates()
            }
        except Exception as e:
            logger.error(f"Error getting metrics: {e}")
            return {'categories': [], 'summaries': [], 'purchasing': []}
    
    def _get_metric_categories(self) -> List[Dict]:
        """Get categorized metrics"""
        # connect this to actual database
        categories = []
        
        # Best Sellers (from database)
        categories.append({
            'id': 1,
            'title': 'Best Sellers',
            'icon': 'ShoppingCart',
            'items': [
                {'name': 'Burger Special', 'value': '156', 'trend': 'up', 'change': '+12%'},
                {'name': 'Caesar Salad', 'value': '142', 'trend': 'up', 'change': '+8%'},
                {'name': 'Pasta Primavera', 'value': '128', 'trend': 'stable', 'change': '0%'}
            ]
        })
        
        # Peak Hours
        categories.append({
            'id': 2,
            'title': 'Peak Hours',
            'icon': 'Clock',
            'items': [
                {'name': '12:00 PM - 1:00 PM', 'value': '92%', 'trend': 'up'},
                {'name': '6:00 PM - 7:00 PM', 'value': '96%', 'trend': 'stable'},
                {'name': '7:00 PM - 8:00 PM', 'value': '94%', 'trend': 'down'}
            ]
        })
        
        return categories
    
    def _get_metric_summaries(self) -> List[Dict]:
        """Get summary metrics"""
        # calculate these from actual data
        return [
            {
                'id': 1,
                'title': 'Labor Cost',
                'percentage': '28.5%',
                'target': '30%',
                'status': 'good',
                'trend': 'down',
                'change': '-1.2%'
            },
            {
                'id': 2,
                'title': 'Food Cost',
                'percentage': '32.8%',
                'target': '32%',
                'status': 'warning',
                'trend': 'up',
                'change': '+0.8%'
            },
            {
                'id': 3,
                'title': 'Table Turnover',
                'percentage': '2.8x',
                'target': '2.5x',
                'status': 'excellent',
                'trend': 'up',
                'change': '+0.3'
            }
        ]
    
    def _get_purchasing_estimates(self) -> List[Dict]:
        """Get purchasing estimates using item_sales_predictor"""
        purchasing = []
        
        try:
            # Sample items - can loop through actual menu
            items = [
                (1, 'Produce', 'Salads'),
                (2, 'Meat', 'Entrees'),
                (3, 'Dairy', 'Desserts'),
                (4, 'Beverages', 'Beverages')
            ]
            
            target_date = datetime.now() + timedelta(days=3)
            
            for item_id, item_name, category in items:
                # Use sales predictor
                prediction = self.prediction_service.predict_sales_enhanced(
                    item_id=item_id,
                    target_date=target_date,
                    item_name=item_name,
                    category=category
                )
                
                quantity = prediction.get('predicted_quantity', 50)
                confidence = prediction.get('confidence', 0.75)
                
                # Estimate cost (you can use real costs from DB)
                unit_cost = {'Produce': 3.5, 'Meat': 8.2, 'Dairy': 2.8, 'Beverages': 2.2}.get(item_name, 5.0)
                total_cost = quantity * unit_cost
                
                # Determine urgency
                days_until = 3
                if days_until <= 1:
                    status = 'Order Today'
                    urgency = 'high'
                elif days_until <= 3:
                    status = f'Order in {days_until} days'
                    urgency = 'medium'
                else:
                    status = 'On Schedule'
                    urgency = 'low'
                
                purchasing.append({
                    'item': item_name,
                    'estimate': f'${total_cost:,.0f}',
                    'quantity': quantity,
                    'status': status,
                    'urgency': urgency,
                    'confidence': confidence
                })
            
            return purchasing
            
        except Exception as e:
            logger.error(f"Error getting purchasing estimates: {e}")
            return []
    
    def get_info_sections(self) -> Dict:
        """Get information sections for dashboard"""
        try:
            return {
                'events': self._get_event_info(),
                'weather': self._get_weather_info(),
                'labor': self._get_labor_info(),
                'historical': self._get_historical_info()
            }
        except Exception as e:
            logger.error(f"Error getting info sections: {e}")
            return {'events': [], 'weather': {}, 'labor': {}, 'historical': {}}
    
    def _get_event_info(self) -> List[Dict]:
        """Get upcoming events from YOUR event service"""
        try:
            today = datetime.now()
            events = self.event_service.fetch_ticketmaster_events(
                today,
                today + timedelta(days=14)
            )
            
            event_info = []
            for event in events[:5]:  # Top 5
                event_date = datetime.fromisoformat(event['event_datetime'])
                attendance = event.get('attendance_estimated', 0)
                
                # Estimate booking impact
                if attendance > 5000:
                    booking_impact = '90%'
                elif attendance > 1000:
                    booking_impact = '75%'
                else:
                    booking_impact = '50%'
                
                event_info.append({
                    'date': event_date.strftime('%b %d'),
                    'event': event.get('event_name', 'Event'),
                    'bookings': booking_impact,
                    'distance': f"{event.get('distance_miles', 0):.1f} mi",
                    'attendance': attendance
                })
            
            return event_info if event_info else [
                {'date': 'This Week', 'event': 'No major events', 'bookings': 'Standard'}
            ]
            
        except Exception as e:
            logger.error(f"Error getting event info: {e}")
            return []
    
    def _get_weather_info(self) -> Dict:
        """Get weather info from YOUR weather service"""
        try:
            current = self.weather_service.get_current_weather()
            forecast = self.weather_service.get_forecast(days=3)
            
            current_str = "Unknown"
            if current:
                temp = current.get('temperature_f', 'Unknown')
                condition = current.get('condition', 'Unknown')
                current_str = f"{condition}, {temp}°F"
            
            forecast_str = "No forecast available"
            impact_str = "Unknown"
            
            if forecast and len(forecast) > 0:
                upcoming = forecast[0]
                forecast_str = f"{upcoming['short_forecast']}"
                precip = upcoming.get('precipitation_chance', 0)
                
                if precip > 30:
                    forecast_str += f" ({precip}% rain)"
                
                # Calculate impact
                temp_high = upcoming.get('temperature_high_f', 70)
                condition = upcoming.get('condition', 'sunny')
                
                if condition in ['rainy', 'snowy'] or precip > 60:
                    impact_str = "High - Patio affected"
                elif temp_high and (temp_high < 45 or temp_high > 90):
                    impact_str = "Moderate - Temperature impact"
                else:
                    impact_str = "Low - Favorable conditions"
            
            return {
                'current': current_str,
                'forecast': forecast_str,
                'impact': impact_str
            }
            
        except Exception as e:
            logger.error(f"Error getting weather info: {e}")
            return {
                'current': 'Error fetching weather',
                'forecast': 'Unable to load',
                'impact': 'Unknown'
            }
    
    def _get_labor_info(self) -> Dict:
        """Get labor scheduling info using busyness predictions"""
        try:
            # Get predicted busyness for tomorrow evening
            tomorrow = datetime.now() + timedelta(days=1)
            tomorrow_evening = tomorrow.replace(hour=19)
            
            busyness = self.prediction_service.predict_busyness_enhanced(tomorrow_evening)
            
            expected_guests = busyness.get('expected_guests', 40)
            
            # Simple labor calculation (0.5 staff per 10 guests)
            predicted_staff = int(expected_guests * 0.5)
            planned_staff = 30  # This could come from scheduling system
            
            variance = predicted_staff - planned_staff
            
            if variance > 2:
                recommendation = f"Add {variance} staff members for {tomorrow.strftime('%A')}"
                status = 'understaffed'
            elif variance < -2:
                recommendation = f"Consider reducing {abs(variance)} staff members"
                status = 'overstaffed'
            else:
                recommendation = "Current staffing is adequate"
                status = 'optimal'
            
            return {
                'predicted': predicted_staff,
                'planned': planned_staff,
                'variance': f"{'+' if variance > 0 else ''}{variance}",
                'recommendation': recommendation,
                'status': status,
                'target_day': tomorrow.strftime('%A'),
                'busyness_level': busyness.get('level')
            }
            
        except Exception as e:
            logger.error(f"Error getting labor info: {e}")
            return {
                'predicted': 30,
                'planned': 30,
                'variance': '0',
                'recommendation': 'Standard staffing'
            }
    
    def _get_historical_info(self) -> Dict:
        """Get historical comparison data"""
        # connect this to actual sales database
        try:
            # Mock data - replace with actual DB queries
            this_week_so_far = 25000.0
            days_elapsed = datetime.now().weekday() + 1
            days_remaining = 7 - days_elapsed
            
            avg_per_day = this_week_so_far / max(days_elapsed, 1)
            this_week_projection = this_week_so_far + (avg_per_day * days_remaining)
            
            return {
                'lastYear': '$42,500',
                'lastYearValue': 42500,
                'average': '$38,750',
                'averageValue': 38750,
                'projection': f'${this_week_projection:,.0f}',
                'projectionValue': this_week_projection,
                'trend': 'up' if this_week_projection > 38750 else 'down',
                'change': f"{((this_week_projection - 38750) / 38750 * 100):+.1f}%"
            }
            
        except Exception as e:
            logger.error(f"Error getting historical info: {e}")
            return {
                'lastYear': '$42,500',
                'average': '$38,750',
                'projection': '$41,200'
            }


# Create singleton instance
dashboard_service = DashboardService()

def get_dashboard_service() -> DashboardService:  #
    """Get the singleton dashboard service instance"""
    return dashboard_service