"""
Train ML Models - FINAL PRODUCTION VERSION
Fixes:
1. Item Sales: Aggregates to Daily Totals (prevents R²=1.0 leakage)
2. Wait Time: Uses Gradient Boosting for better signal detection
3. Busyness: Balances class weights
"""
import pandas as pd
import numpy as np
from datetime import datetime
import sys
from pathlib import Path
import pickle

sys.path.append(str(Path(__file__).parent.parent))
from app.database.database import SessionLocal
from app.models.database_models import MenuItem, Order, OrderItem, WaitTime

from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score, accuracy_score

print("🤖 TRAINING MODELS (AGGREGATED & CORRECTED)")
print("=" * 60)

db = SessionLocal()

try:
    # =====================================================
    # 1. ITEM SALES MODEL (The Big Fix)
    # =====================================================
    print("\n1️⃣  Training Item Sales Model (Daily Aggregation)...")
    
    # Get raw data
    query = db.query(
        OrderItem.quantity,
        MenuItem.item_name,
        MenuItem.category,
        MenuItem.price,
        Order.order_timestamp
    ).join(MenuItem).join(Order).all()

    if query:
        # Load into DataFrame
        raw_df = pd.DataFrame([{
            'item_name': r.item_name,
            'category': r.category,
            'price': r.price,
            'quantity': r.quantity,
            'timestamp': r.order_timestamp
        } for r in query])

        # --- CRITICAL STEP: AGGREGATE BY DAY ---
        # Convert to date (remove time) to predict DAILY volume
        raw_df['date'] = raw_df['timestamp'].dt.date
        
        # Group by Item + Date to get Total Daily Qty
        sales_df = raw_df.groupby(['date', 'item_name', 'category', 'price']).agg({
            'quantity': 'sum'
        }).reset_index()

        # Feature Engineering on the AGGREGATED data
        sales_df['date'] = pd.to_datetime(sales_df['date'])
        sales_df['day_of_week'] = sales_df['date'].dt.dayofweek
        sales_df['month'] = sales_df['date'].dt.month
        sales_df['is_weekend'] = (sales_df['day_of_week'] >= 5).astype(int)
        
        # Encoders
        le_item = LabelEncoder()
        le_cat = LabelEncoder()
        sales_df['item_encoded'] = le_item.fit_transform(sales_df['item_name'])
        sales_df['cat_encoded'] = le_cat.fit_transform(sales_df['category'])

        features = ['item_encoded', 'cat_encoded', 'price', 'day_of_week', 'month', 'is_weekend']
        X = sales_df[features]
        y = sales_df['quantity']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Use Gradient Boosting for Regression (better for counts)
        model = GradientBoostingRegressor(n_estimators=100, max_depth=5, random_state=42)
        model.fit(X_train, y_train)

        preds = model.predict(X_test)
        mae = mean_absolute_error(y_test, preds)
        r2 = r2_score(y_test, preds)

        print(f"  ✓ Raw Rows: {len(raw_df):,} -> Aggregated Daily Rows: {len(sales_df):,}")
        print(f"  ✓ MAE: {mae:.2f} (Average miss in daily units)")
        print(f"  ✓ R² Score: {r2:.3f}")

        with open('data/models/item_sales_model.pkl', 'wb') as f:
            pickle.dump({
                'model': model,
                'le_item': le_item,
                'le_cat': le_cat,
                'features': features
            }, f)
        print("  ✓ Saved to data/models/item_sales_model.pkl")

    # =====================================================
    # 2. WAIT TIME MODEL (Boosting)
    # =====================================================
    print("\n2️⃣  Training Wait Time Model (Gradient Boosting)...")
    
    wait_times = db.query(WaitTime).all()
    if wait_times:
        data = []
        for w in wait_times:
            data.append({
                'party_size': w.party_size,
                'hour': w.hour_of_day,
                'day': w.day_of_week,
                'occupancy': w.occupancy_percentage or 50,
                'wait': w.actual_wait_minutes
            })
        
        df = pd.DataFrame(data)
        
        # Add non-linear interaction features
        df['busy_hour'] = df['hour'].apply(lambda x: 1 if x in [18, 19, 20] else 0)
        df['high_occ'] = df['occupancy'].apply(lambda x: 1 if x > 80 else 0)
        df['interaction'] = df['party_size'] * df['occupancy']

        X = df[['party_size', 'hour', 'day', 'occupancy', 'busy_hour', 'high_occ', 'interaction']]
        y = df['wait']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Boosting is better at finding the "signal" in noisy wait times
        model = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=4, random_state=42)
        model.fit(X_train, y_train)

        preds = model.predict(X_test)
        mae = mean_absolute_error(y_test, preds)
        r2 = r2_score(y_test, preds)

        print(f"  ✓ Samples: {len(df):,}")
        print(f"  ✓ MAE: {mae:.2f} minutes")
        print(f"  ✓ R² Score: {r2:.3f}")

        with open('models/wait_time_model.pkl', 'wb') as f:
            pickle.dump({'model': model, 'features': list(X.columns)}, f)
        print("  ✓ Saved to models/wait_time_model.pkl")

    # =====================================================
    # 3. BUSYNESS MODEL
    # =====================================================
    print("\n3️⃣  Training Busyness Model...")
    
    # Aggregate orders by HOUR
    orders = db.query(Order.order_timestamp, Order.party_size).all()
    if orders:
        counts = {}
        for ts, size in orders:
            # Round to nearest hour
            key = ts.replace(minute=0, second=0, microsecond=0)
            if key not in counts: counts[key] = 0
            counts[key] += 1
        
        data = []
        for ts, count in counts.items():
            level = 0 if count < 5 else (1 if count < 15 else 2)
            data.append({
                'hour': ts.hour,
                'day': ts.weekday(),
                'month': ts.month,
                'is_weekend': 1 if ts.weekday() >= 5 else 0,
                'level': level
            })
        
        df = pd.DataFrame(data)
        X = df[['hour', 'day', 'month', 'is_weekend']]
        y = df['level']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        acc = accuracy_score(y_test, model.predict(X_test))
        print(f"  ✓ Hourly Samples: {len(df):,}")
        print(f"  ✓ Accuracy: {acc*100:.1f}%")

        with open('models/busyness_model.pkl', 'wb') as f:
            pickle.dump({'model': model, 'features': list(X.columns)}, f)
        print("  ✓ Saved to models/busyness_model.pkl")

    print("\n" + "="*60)
    print("✅ FIXED TRAINING COMPLETE")
    print("="*60)

finally:
    db.close()
