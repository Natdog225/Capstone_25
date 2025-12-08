"""
Merge Historical Events with Sales Data
Adds event features to training data for better predictions
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timedelta

def load_historical_events():
    """Load the backfilled events"""
    events_file = Path("data/events/historical_events_2025_jan_jun.json")
    
    if not events_file.exists():
        print("❌ No historical events found. Run backfill script first.")
        return None
    
    with open(events_file) as f:
        data = json.load(f)
    
    events_df = pd.DataFrame(data['events'])
    events_df['event_date'] = pd.to_datetime(events_df['event_date'])
    
    return events_df


def add_event_features_to_orders(orders_df, events_df):
    """Add event features to order data"""
    
    orders_df['order_date'] = pd.to_datetime(orders_df['order_timestamp']).dt.date
    
    # For each order, find events on that day
    orders_df['has_event'] = 0
    orders_df['event_count'] = 0
    orders_df['max_event_attendance'] = 0
    orders_df['closest_event_distance'] = 99.0
    
    for idx, order in orders_df.iterrows():
        order_date = order['order_date']
        
        # Find events on this date
        same_day_events = events_df[events_df['event_date'].dt.date == order_date]
        
        if len(same_day_events) > 0:
            orders_df.at[idx, 'has_event'] = 1
            orders_df.at[idx, 'event_count'] = len(same_day_events)
            orders_df.at[idx, 'max_event_attendance'] = same_day_events['attendance_estimated'].max()
            orders_df.at[idx, 'closest_event_distance'] = same_day_events['distance_miles'].min()
    
    return orders_df


def main():
    print("🔗 MERGING EVENTS WITH SALES DATA")
    print("=" * 60)
    
    # Load data
    print("Loading sales data...")
    orders_df = pd.read_csv("data/processed/orders_from_real_data.csv")
    print(f"  ✓ {len(orders_df):,} orders loaded")
    
    print("\nLoading historical events...")
    events_df = load_historical_events()
    
    if events_df is None:
        return
    
    print(f"  ✓ {len(events_df):,} events loaded")
    
    print("\nMerging event data with orders...")
    enhanced_orders = add_event_features_to_orders(orders_df, events_df)
    
    # Statistics
    orders_with_events = enhanced_orders[enhanced_orders['has_event'] == 1]
    print(f"\n📊 Statistics:")
    print(f"  Total Orders: {len(enhanced_orders):,}")
    print(f"  Orders with Events: {len(orders_with_events):,} ({len(orders_with_events)/len(enhanced_orders)*100:.1f}%)")
    print(f"  Average Event Attendance: {orders_with_events['max_event_attendance'].mean():,.0f}")
    
    # Save enhanced dataset
    output_file = "data/processed/orders_with_events.csv"
    enhanced_orders.to_csv(output_file, index=False)
    
    print(f"\n💾 Saved enhanced dataset: {output_file}")
    print("\n✅ Complete! Your training data now includes event context.")
    print("\nNext: Retrain models with event features:")
    print("  python scripts/train_models_from_db.py")


if __name__ == "__main__":
    main()
