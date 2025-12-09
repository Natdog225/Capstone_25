"""
Historical Data API - Detailed Trends and Analytics
FIXED: Uses actual data date range, not current date
"""

from fastapi import APIRouter, Query
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy import func, and_
import logging

from app.database.database import SessionLocal
from app.models.database_models import Order, OrderItem, WaitTime

router = APIRouter()
logger = logging.getLogger(__name__)


def get_data_date_range(db):
    """Get the actual date range of data in the database"""
    min_date = db.query(func.min(Order.order_timestamp)).scalar()
    max_date = db.query(func.max(Order.order_timestamp)).scalar()
    
    if not min_date or not max_date:
        # Fallback to current date if no data
        return datetime.now() - timedelta(days=30), datetime.now()
    
    return min_date, max_date


@router.get("/date-range")
async def get_available_date_range() -> Dict:
    """Get the date range of available historical data"""
    db = SessionLocal()
    try:
        min_date, max_date = get_data_date_range(db)
        
        return {
            'earliest_date': min_date.strftime('%Y-%m-%d'),
            'latest_date': max_date.strftime('%Y-%m-%d'),
            'total_days': (max_date - min_date).days,
            'has_data': True
        }
    finally:
        db.close()


@router.get("/trends/daily")
async def get_daily_trends(
    days: int = Query(default=30, ge=1, le=180, description="Number of days to fetch"),
    end_date: Optional[str] = Query(default=None, description="End date (YYYY-MM-DD), defaults to latest data")
) -> Dict:
    """
    Get detailed daily trends with sales, orders, wait times
    Perfect for smooth trend charts
    """
    
    db = SessionLocal()
    
    try:
        # Use actual data range instead of current date
        if end_date:
            end = datetime.strptime(end_date, '%Y-%m-%d')
        else:
            # Get the latest date in our data
            _, end = get_data_date_range(db)
        
        start = end - timedelta(days=days)
        
        logger.info(f"Fetching daily trends from {start.date()} to {end.date()}")
        
        # ================================================
        # DAILY SALES & ORDER COUNT
        # ================================================
        daily_sales = db.query(
            func.date(Order.order_timestamp).label('date'),
            func.sum(Order.order_total).label('total_sales'),
            func.count(Order.id).label('order_count')
        ).filter(
            and_(
                Order.order_timestamp >= start,
                Order.order_timestamp <= end
            )
        ).group_by(func.date(Order.order_timestamp)).all()
        
        # ================================================
        # DAILY AVERAGE WAIT TIME
        # ================================================
        daily_waits = db.query(
            func.date(WaitTime.timestamp).label('date'),
            func.avg(WaitTime.actual_wait_minutes).label('avg_wait')
        ).filter(
            and_(
                WaitTime.timestamp >= start,
                WaitTime.timestamp <= end
            )
        ).group_by(func.date(WaitTime.timestamp)).all()
        
        # Convert to dict for easy lookup
        wait_dict = {str(w.date): float(w.avg_wait) for w in daily_waits}
        
        # ================================================
        # BUILD DAILY DATA ARRAY
        # ================================================
        daily_data = []
        
        for record in daily_sales:
            date_str = str(record.date)
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            
            daily_data.append({
                'date': date_str,
                'sales': round(float(record.total_sales or 0), 2),
                'order_count': int(record.order_count or 0),
                'wait_time': round(wait_dict.get(date_str, 0), 1),
                'day_of_week': date_obj.weekday(),
                'day_name': date_obj.strftime('%A'),
                'is_weekend': date_obj.weekday() >= 5
            })
        
        # Sort by date
        daily_data.sort(key=lambda x: x['date'])
        
        # ================================================
        # CALCULATE SUMMARY STATS
        # ================================================
        if daily_data:
            sales_values = [d['sales'] for d in daily_data]
            wait_values = [d['wait_time'] for d in daily_data if d['wait_time'] > 0]
            
            # Peak wait time
            peak_wait = max(wait_values) if wait_values else 0
            
            # Average daily sales
            avg_sales = sum(sales_values) / len(sales_values)
            
            # Busiest day of week
            day_totals = {}
            for d in daily_data:
                day_name = d['day_name']
                if day_name not in day_totals:
                    day_totals[day_name] = {'sales': 0, 'count': 0}
                day_totals[day_name]['sales'] += d['sales']
                day_totals[day_name]['count'] += 1
            
            busiest_day = max(day_totals.items(), 
                            key=lambda x: x[1]['sales'] / x[1]['count'])[0] if day_totals else 'Unknown'
            
            # Trend calculation (simple linear regression)
            if len(sales_values) >= 7:
                # Compare first week vs last week
                first_week = sum(sales_values[:7]) / 7
                last_week = sum(sales_values[-7:]) / 7
                
                change = (last_week - first_week) / first_week if first_week > 0 else 0
                
                if change > 0.05:
                    trend_direction = "up"
                    trend_strength = min(abs(change), 1.0)
                elif change < -0.05:
                    trend_direction = "down"
                    trend_strength = min(abs(change), 1.0)
                else:
                    trend_direction = "stable"
                    trend_strength = 0.5
            else:
                trend_direction = "stable"
                trend_strength = 0.5
            
            summary_stats = {
                'peak_wait_time': round(peak_wait, 1),
                'avg_wait_time': round(sum(wait_values) / len(wait_values), 1) if wait_values else 0,
                'avg_daily_sales': round(avg_sales, 2),
                'total_sales': round(sum(sales_values), 2),
                'total_orders': sum(d['order_count'] for d in daily_data),
                'busiest_day_of_week': busiest_day,
                'trend_direction': trend_direction,
                'trend_strength': round(trend_strength, 2),
                'days_analyzed': len(daily_data)
            }
        else:
            summary_stats = {
                'peak_wait_time': 0,
                'avg_wait_time': 0,
                'avg_daily_sales': 0,
                'total_sales': 0,
                'total_orders': 0,
                'busiest_day_of_week': 'Unknown',
                'trend_direction': 'stable',
                'trend_strength': 0,
                'days_analyzed': 0
            }
        
        return {
            'daily_data': daily_data,
            'summary_stats': summary_stats,
            'period': {
                'start_date': start.strftime('%Y-%m-%d'),
                'end_date': end.strftime('%Y-%m-%d'),
                'days': days
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching daily trends: {e}", exc_info=True)
        raise
    finally:
        db.close()


@router.get("/trends/weekly")
async def get_weekly_trends(
    weeks: int = Query(default=12, ge=1, le=52, description="Number of weeks to fetch"),
    group_by: str = Query(default='week', regex='^(day|week)$', description="Group by day or week")
) -> Dict:
    """
    Get weekly aggregated trends
    Can also return daily if group_by=day
    """
    
    if group_by == 'day':
        # Redirect to daily endpoint
        return await get_daily_trends(days=weeks * 7)
    
    db = SessionLocal()
    
    try:
        # Use actual data range
        _, end_date = get_data_date_range(db)
        start_date = end_date - timedelta(weeks=weeks)
        
        # Get daily data first
        daily_sales = db.query(
            func.date(Order.order_timestamp).label('date'),
            func.sum(Order.order_total).label('total_sales'),
            func.count(Order.id).label('order_count')
        ).filter(
            and_(
                Order.order_timestamp >= start_date,
                Order.order_timestamp <= end_date
            )
        ).group_by(func.date(Order.order_timestamp)).all()
        
        # Group into weeks
        weekly_data = {}
        
        for record in daily_sales:
            date_obj = datetime.strptime(str(record.date), '%Y-%m-%d')
            # Get week start (Monday)
            week_start = date_obj - timedelta(days=date_obj.weekday())
            week_key = week_start.strftime('%Y-%m-%d')
            
            if week_key not in weekly_data:
                weekly_data[week_key] = {
                    'week_start': week_key,
                    'sales': 0,
                    'order_count': 0,
                    'days': []
                }
            
            weekly_data[week_key]['sales'] += float(record.total_sales or 0)
            weekly_data[week_key]['order_count'] += int(record.order_count or 0)
            weekly_data[week_key]['days'].append(str(record.date))
        
        # Convert to list and sort
        weekly_list = list(weekly_data.values())
        weekly_list.sort(key=lambda x: x['week_start'])
        
        # Calculate week-over-week change
        for i in range(1, len(weekly_list)):
            prev = weekly_list[i-1]['sales']
            curr = weekly_list[i]['sales']
            change = ((curr - prev) / prev * 100) if prev > 0 else 0
            weekly_list[i]['change_percent'] = round(change, 1)
        
        if weekly_list:
            weekly_list[0]['change_percent'] = 0
        
        return {
            'weekly_data': weekly_list,
            'summary': {
                'weeks_analyzed': len(weekly_list),
                'total_sales': round(sum(w['sales'] for w in weekly_list), 2),
                'total_orders': sum(w['order_count'] for w in weekly_list),
                'avg_weekly_sales': round(sum(w['sales'] for w in weekly_list) / len(weekly_list), 2) if weekly_list else 0
            },
            'period': {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'weeks': weeks
            }
        }
        
    finally:
        db.close()
