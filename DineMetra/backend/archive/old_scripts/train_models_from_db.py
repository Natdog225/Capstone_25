"""
Train ML Models from Neon PostgreSQL Database (FIXED)
Production-ready training pipeline with proper feature engineering
"""

import pandas as pd
import numpy as np
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.database.database import SessionLocal
from app.models.database_models import MenuItem, Order, OrderItem, WaitTime
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import pickle

print("🤖 TRAINING MODELS FROM DATABASE")
print("=" * 60)

db = SessionLocal()

try:
    # =====================================================
    # 1. WAIT TIME MODEL
    # =====================================================
    print("\n1️⃣  Training Wait Time Model...")
    
    wait_times = db.query(WaitTime).all()
    
    if wait_times:
        wait_data = []
        for wt in wait_times:
            wait_data.append({
                'party_size': wt.party_size,
                'hour_of_day': wt.hour_of_day,
                'day_of_week': wt.day_of_week,
                'month': wt.timestamp.month,
                'current_table_occupancy_pct': wt.occupancy_percentage or 50,
                'current_party_count': int((wt.occupancy_percentage or 50) / 3.33),
                'is_weekend': 1 if wt.day_of_week in [5, 6] else 0,
                'is_peak_hour': 1 if wt.hour_of_day in [11, 12, 13, 17, 18, 19, 20] else 0,
                'is_lunch': 1 if wt.hour_of_day in [11, 12, 13] else 0,
                'is_dinner': 1 if wt.hour_of_day in [17, 18, 19, 20] else 0,
                'occupancy_low': 1 if (wt.occupancy_percentage or 50) < 50 else 0,
                'occupancy_high': 1 if (wt.occupancy_percentage or 50) >= 75 else 0,
                'party_small': 1 if wt.party_size <= 2 else 0,
                'party_large': 1 if wt.party_size >= 6 else 0,
                'actual_wait_minutes': wt.actual_wait_minutes
            })
        
        wait_df = pd.DataFrame(wait_data)
        
        features = [
            'party_size', 'hour_of_day', 'day_of_week', 'month',
            'current_table_occupancy_pct', 'current_party_count',
            'is_weekend', 'is_peak_hour', 'is_lunch', 'is_dinner',
            'occupancy_low', 'occupancy_high', 'party_small', 'party_large'
        ]
        
        X = wait_df[features]
        y = wait_df['actual_wait_minutes']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Use more conservative parameters to avoid overfitting
        wait_model = RandomForestRegressor(
            n_estimators=50,
            max_depth=10,
            min_samples_split=20,
            min_samples_leaf=10,
            random_state=42
        )
        wait_model.fit(X_train, y_train)
        
        test_score = wait_model.score(X_test, y_test)
        predictions = wait_model.predict(X_test)
        mae = np.mean(np.abs(predictions - y_test))
        
        print(f"  ✓ Samples: {len(wait_df):,}")
        print(f"  ✓ Features: {len(features)}")
        print(f"  ✓ MAE: {mae:.2f} minutes")
        print(f"  ✓ R² Score: {test_score:.3f}")
        
        # Save model
        with open('models/wait_time_model.pkl', 'wb') as f:
            pickle.dump({'model': wait_model, 'features': features}, f)
        print(f"  ✓ Saved to models/wait_time_model.pkl")
    else:
        print("  ⚠️ No wait time data found")
    
    # =====================================================
    # 2. BUSYNESS MODEL
    # =====================================================
    print("\n2️⃣  Training Busyness Model...")
    
    # Get all orders
    orders_query = db.query(
        Order.order_timestamp,
        Order.party_size
    ).all()
    
    if orders_query:
        # Create hourly aggregations properly
        hourly_counts = {}
        for timestamp, party_size in orders_query:
            hour_key = timestamp.replace(minute=0, second=0, microsecond=0)
            if hour_key not in hourly_counts:
                hourly_counts[hour_key] = {'count': 0, 'total_party': 0}
            hourly_counts[hour_key]['count'] += 1
            hourly_counts[hour_key]['total_party'] += party_size
        
        busyness_data = []
        for hour, data in hourly_counts.items():
            order_count = data['count']
            avg_party = data['total_party'] / data['count']
            
            # Classify busyness based on orders per hour
            if order_count <= 5:
                level = 0  # slow
            elif order_count <= 12:
                level = 1  # moderate  
            else:
                level = 2  # peak
            
            busyness_data.append({
                'hour': hour.hour,
                'day_of_week': hour.weekday(),
                'month': hour.month,
                'avg_party_size': avg_party,
                'is_weekend': 1 if hour.weekday() in [5, 6] else 0,
                'is_lunch': 1 if hour.hour in [11, 12, 13] else 0,
                'is_dinner': 1 if hour.hour in [17, 18, 19, 20] else 0,
                'is_peak_hour': 1 if hour.hour in [11, 12, 13, 17, 18, 19, 20] else 0,
                'busyness_level': level
            })
        
        busyness_df = pd.DataFrame(busyness_data)
        
        features = ['hour', 'day_of_week', 'month', 'avg_party_size',
                   'is_weekend', 'is_lunch', 'is_dinner', 'is_peak_hour']
        
        X = busyness_df[features]
        y = busyness_df['busyness_level']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        busyness_model = RandomForestClassifier(
            n_estimators=50,
            max_depth=8,
            min_samples_split=10,
            random_state=42
        )
        busyness_model.fit(X_train, y_train)
        
        test_acc = busyness_model.score(X_test, y_test)
        
        print(f"  ✓ Samples: {len(busyness_df):,}")
        print(f"  ✓ Features: {len(features)}")
        print(f"  ✓ Accuracy: {test_acc*100:.1f}%")
        
        # Save model
        label_mapping = {0: "slow", 1: "moderate", 2: "peak"}
        with open('models/busyness_model.pkl', 'wb') as f:
            pickle.dump({
                'model': busyness_model,
                'label_mapping': label_mapping,
                'features': features
            }, f)
        print(f"  ✓ Saved to models/busyness_model.pkl")
    else:
        print("  ⚠️ No order data found")
    
    # =====================================================
    # 3. ITEM SALES MODEL  
    # =====================================================
    print("\n3️⃣  Training Item Sales Model...")
    
    # Query individual order items (not aggregated)
    items_query = db.query(
        OrderItem.quantity,
        MenuItem.item_name,
        MenuItem.category,
        MenuItem.price,
        Order.order_timestamp
    ).join(MenuItem).join(Order).all()
    
    if items_query:
        sales_data = []
        for qty, item_name, category, price, timestamp in items_query:
            sales_data.append({
                'item_name': item_name,
                'category': category,
                'price': price,
                'quantity': qty,
                'day_of_week': timestamp.weekday(),
                'month': timestamp.month,
                'hour': timestamp.hour
            })
        
        sales_df = pd.DataFrame(sales_data)
        
        # Encode categorical variables
        le_item = LabelEncoder()
        le_category = LabelEncoder()
        
        sales_df['item_encoded'] = le_item.fit_transform(sales_df['item_name'])
        sales_df['category_encoded'] = le_category.fit_transform(sales_df['category'])
        
        # Feature engineering
        sales_df['is_weekend'] = (sales_df['day_of_week'] >= 5).astype(int)
        sales_df['is_lunch'] = sales_df['hour'].apply(lambda x: 1 if 11 <= x <= 13 else 0)
        sales_df['is_dinner'] = sales_df['hour'].apply(lambda x: 1 if 17 <= x <= 20 else 0)
        
        # Item type flags
        sales_df['is_fried'] = sales_df['item_name'].str.lower().str.contains('fry|fried', na=False).astype(int)
        sales_df['is_banh_mi'] = sales_df['item_name'].str.lower().str.contains('banh mi', na=False).astype(int)
        sales_df['is_bowl'] = sales_df['item_name'].str.lower().str.contains('bowl', na=False).astype(int)
        sales_df['is_beverage'] = sales_df['item_name'].str.lower().str.contains('soda|water|tea|coffee', na=False).astype(int)
        
        # Features
        feature_cols = ['item_encoded', 'category_encoded', 'price', 'day_of_week', 
                       'month', 'is_weekend', 'is_lunch', 'is_dinner', 'is_fried',
                       'is_banh_mi', 'is_bowl', 'is_beverage']
        
        X = sales_df[feature_cols]
        y = sales_df['quantity']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Conservative parameters
        sales_model = RandomForestRegressor(
            n_estimators=50,
            max_depth=15,
            min_samples_split=50,
            min_samples_leaf=20,
            random_state=42
        )
        sales_model.fit(X_train, y_train)
        
        test_score = sales_model.score(X_test, y_test)
        predictions = sales_model.predict(X_test)
        mae = np.mean(np.abs(predictions - y_test))
        
        print(f"  ✓ Samples: {len(sales_df):,}")
        print(f"  ✓ Items: {len(sales_df['item_name'].unique())}")
        print(f"  ✓ Features: {len(feature_cols)}")
        print(f"  ✓ MAE: {mae:.2f} units")
        print(f"  ✓ R² Score: {test_score:.3f}")
        
        # Save model with encoders
        with open('data/models/item_sales_model.pkl', 'wb') as f:
            pickle.dump({
                'model': sales_model,
                'label_encoder_item': le_item,
                'label_encoder_category': le_category,
                'feature_cols': feature_cols
            }, f)
        print(f"  ✓ Saved to data/models/item_sales_model.pkl")
    else:
        print("  ⚠️ No sales data found")
    
    print("\n" + "=" * 60)
    print("✅ TRAINING COMPLETE!")
    print("=" * 60)
    print("\nDatabase Statistics:")
    print(f"  • Wait Times: {db.query(WaitTime).count():,} records")
    print(f"  • Orders: {db.query(Order).count():,} records")
    print(f"  • Order Items: {db.query(OrderItem).count():,} records")
    print(f"  • Menu Items: {db.query(MenuItem).count():,} items")
    print("\n🎯 All models ready for predictions!")
    
finally:
    db.close()
