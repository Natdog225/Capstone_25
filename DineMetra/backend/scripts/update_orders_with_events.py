"""
Update database orders with event features
"""

import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.database.database import SessionLocal
from app.models.database_models import Order
from sqlalchemy import text

def main():
    print("🔄 ADDING EVENT FEATURES TO DATABASE")
    print("=" * 60)
    
    # Load enhanced data
    print("Loading enhanced orders...")
    orders_df = pd.read_csv("data/processed/orders_with_events.csv")
    print(f"  ✓ {len(orders_df):,} orders loaded")
    
    db = SessionLocal()
    
    try:
        # Add columns if they don't exist
        print("\nAdding event columns to database...")
        
        columns_to_add = [
            "ALTER TABLE orders ADD COLUMN IF NOT EXISTS has_event INTEGER DEFAULT 0",
            "ALTER TABLE orders ADD COLUMN IF NOT EXISTS event_count INTEGER DEFAULT 0",
            "ALTER TABLE orders ADD COLUMN IF NOT EXISTS max_event_attendance INTEGER DEFAULT 0",
            "ALTER TABLE orders ADD COLUMN IF NOT EXISTS closest_event_distance FLOAT DEFAULT 99.0"
        ]
        
        for sql in columns_to_add:
            try:
                db.execute(text(sql))
            except Exception as e:
                print(f"  Note: {e}")
        
        db.commit()
        print("  ✓ Columns added")
        
        # Update orders with event data
        print("\nUpdating orders with event data...")
        updated = 0
        
        for idx, row in orders_df.iterrows():
            order_number = str(row['order_id'])
            
            db.execute(
                text("""
                    UPDATE orders 
                    SET has_event = :has_event,
                        event_count = :event_count,
                        max_event_attendance = :attendance,
                        closest_event_distance = :distance
                    WHERE order_number = :order_number
                """),
                {
                    'has_event': int(row['has_event']),
                    'event_count': int(row['event_count']),
                    'attendance': int(row['max_event_attendance']),
                    'distance': float(row['closest_event_distance']),
                    'order_number': order_number
                }
            )
            
            updated += 1
            if updated % 1000 == 0:
                print(f"  Progress: {updated:,}/{len(orders_df):,}")
                db.commit()
        
        db.commit()
        
        print(f"\n✅ Updated {updated:,} orders with event data")
        
        # Verify
        result = db.execute(text("SELECT COUNT(*) FROM orders WHERE has_event = 1")).scalar()
        print(f"✓ Orders with events: {result:,}")
        
    finally:
        db.close()
    
    print("\n✅ Database updated! Models can now train with event features.")
    print("\nNext step:")
    print("  python scripts/train_models_from_db.py")

if __name__ == "__main__":
    main()
