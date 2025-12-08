"""
Train ML Models WITH EVENT FEATURES
Now includes event impact on predictions!
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

from sklearn.ensemble import GradientBoostingRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score, accuracy_score

print("🤖 TRAINING MODELS WITH EVENT FEATURES")
print("=" * 60)

db = SessionLocal()

try:
    # =====================================================
    # 1. ITEM SALES MODEL (with events!)
    # =====================================================
    print("\n1️⃣  Training Item Sales Model (Daily + Events)...")

    # Get raw data WITH event features
    query = (
        db.query(
            OrderItem.quantity,
            MenuItem.item_name,
            MenuItem.category,
            MenuItem.price,
            Order.order_timestamp,
            Order.has_event,
            Order.event_count,
            Order.max_event_attendance,
            Order.closest_event_distance,
        )
        .join(MenuItem)
        .join(Order)
        .all()
    )

    if query:
        raw_df = pd.DataFrame(
            [
                {
                    "item_name": r.item_name,
                    "category": r.category,
                    "price": r.price,
                    "quantity": r.quantity,
                    "timestamp": r.order_timestamp,
                    "has_event": r.has_event or 0,
                    "event_count": r.event_count or 0,
                    "max_event_attendance": r.max_event_attendance or 0,
                    "closest_event_distance": r.closest_event_distance or 99.0,
                }
                for r in query
            ]
        )

        # Aggregate by day
        raw_df["date"] = raw_df["timestamp"].dt.date

        # For event features, take max values per day
        sales_df = (
            raw_df.groupby(["date", "item_name", "category", "price"])
            .agg(
                {
                    "quantity": "sum",
                    "has_event": "max",
                    "event_count": "max",
                    "max_event_attendance": "max",
                    "closest_event_distance": "min",
                }
            )
            .reset_index()
        )

        # Feature engineering
        sales_df["date"] = pd.to_datetime(sales_df["date"])
        sales_df["day_of_week"] = sales_df["date"].dt.dayofweek
        sales_df["month"] = sales_df["date"].dt.month
        sales_df["is_weekend"] = (sales_df["day_of_week"] >= 5).astype(int)

        # Encoders
        le_item = LabelEncoder()
        le_cat = LabelEncoder()
        sales_df["item_encoded"] = le_item.fit_transform(sales_df["item_name"])
        sales_df["cat_encoded"] = le_cat.fit_transform(sales_df["category"])

        # NEW: Event features!
        sales_df["event_nearby"] = (sales_df["closest_event_distance"] < 2).astype(int)
        sales_df["large_event"] = (sales_df["max_event_attendance"] > 10000).astype(int)

        features = [
            "item_encoded",
            "cat_encoded",
            "price",
            "day_of_week",
            "month",
            "is_weekend",
            "has_event",
            "event_count",
            "event_nearby",
            "large_event",
        ]

        X = sales_df[features]
        y = sales_df["quantity"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        model = GradientBoostingRegressor(
            n_estimators=100, max_depth=5, random_state=42
        )
        model.fit(X_train, y_train)

        preds = model.predict(X_test)
        mae = mean_absolute_error(y_test, preds)
        r2 = r2_score(y_test, preds)

        print(f"  ✓ Raw Rows: {len(raw_df):,} -> Aggregated: {len(sales_df):,}")
        print(
            f"  ✓ Days with events: {sales_df['has_event'].sum():,} ({sales_df['has_event'].sum()/len(sales_df)*100:.1f}%)"
        )
        print(f"  ✓ MAE: {mae:.2f} units")
        print(f"  ✓ R² Score: {r2:.3f}")

        with open("data/models/item_sales_model.pkl", "wb") as f:
            pickle.dump(
                {
                    "model": model,
                    "le_item": le_item,
                    "le_cat": le_cat,
                    "features": features,
                },
                f,
            )
        print("  ✓ Saved with EVENT features!")

    # =====================================================
    # 2. BUSYNESS MODEL (with events!)
    # =====================================================
    print("\n2️⃣  Training Busyness Model (with Events)...")

    orders = db.query(
        Order.order_timestamp, Order.has_event, Order.max_event_attendance
    ).all()

    if orders:
        counts = {}
        event_info = {}

        for ts, has_event, attendance in orders:
            key = ts.replace(minute=0, second=0, microsecond=0)
            if key not in counts:
                counts[key] = 0
                event_info[key] = {"has_event": 0, "attendance": 0}
            counts[key] += 1

            if has_event:
                event_info[key]["has_event"] = 1
                event_info[key]["attendance"] = max(
                    event_info[key]["attendance"], attendance or 0
                )

        data = []
        for ts, count in counts.items():
            level = 0 if count < 5 else (1 if count < 15 else 2)

            data.append(
                {
                    "hour": ts.hour,
                    "day": ts.weekday(),
                    "month": ts.month,
                    "is_weekend": 1 if ts.weekday() >= 5 else 0,
                    "has_event": event_info[ts]["has_event"],
                    "event_attendance": event_info[ts]["attendance"],
                    "level": level,
                }
            )

        df = pd.DataFrame(data)

        # Event features
        df["large_event"] = (df["event_attendance"] > 10000).astype(int)

        X = df[["hour", "day", "month", "is_weekend", "has_event", "large_event"]]
        y = df["level"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        acc = accuracy_score(y_test, model.predict(X_test))

        print(f"  ✓ Hourly Samples: {len(df):,}")
        print(f"  ✓ Hours with events: {df['has_event'].sum():,}")
        print(f"  ✓ Accuracy: {acc*100:.1f}%")

        with open("models/busyness_model.pkl", "wb") as f:
            pickle.dump({"model": model, "features": list(X.columns)}, f)
        print("  ✓ Saved with EVENT features!")

    # =====================================================
    # 3. WAIT TIME MODEL (unchanged)
    # =====================================================
    print("\n3️⃣  Training Wait Time Model...")

    wait_times = db.query(WaitTime).all()
    if wait_times:
        data = []
        for w in wait_times:
            data.append(
                {
                    "party_size": w.party_size,
                    "hour": w.hour_of_day,
                    "day": w.day_of_week,
                    "occupancy": w.occupancy_percentage or 50,
                    "wait": w.actual_wait_minutes,
                }
            )

        df = pd.DataFrame(data)
        df["busy_hour"] = df["hour"].apply(lambda x: 1 if x in [18, 19, 20] else 0)
        df["high_occ"] = df["occupancy"].apply(lambda x: 1 if x > 80 else 0)
        df["interaction"] = df["party_size"] * df["occupancy"]

        X = df[
            [
                "party_size",
                "hour",
                "day",
                "occupancy",
                "busy_hour",
                "high_occ",
                "interaction",
            ]
        ]
        y = df["wait"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        model = GradientBoostingRegressor(
            n_estimators=100, learning_rate=0.1, max_depth=4, random_state=42
        )
        model.fit(X_train, y_train)

        preds = model.predict(X_test)
        mae = mean_absolute_error(y_test, preds)
        r2 = r2_score(y_test, preds)

        print(f"  ✓ Samples: {len(df):,}")
        print(f"  ✓ MAE: {mae:.2f} minutes")
        print(f"  ✓ R² Score: {r2:.3f}")

        with open("models/wait_time_model.pkl", "wb") as f:
            pickle.dump({"model": model, "features": list(X.columns)}, f)
        print("  ✓ Saved to models/wait_time_model.pkl")

    print("\n" + "=" * 60)
    print("✅ TRAINING COMPLETE WITH EVENT FEATURES!")
    print("=" * 60)
    print("\nYour models now understand event impact!")
    print("- Item sales predictions account for nearby events")
    print("- Busyness predictions factor in event attendance")


finally:
    db.close()
