"""
Dinemetra Dummy Data Generator
Generates realistic (and messy) restaurant POS data for testing ETL pipeline

Run: python generate_dummy_data.py
Output: Creates CSV files in data/ directory
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import json

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# ============================================
# CONFIGURATION
# ============================================

# Date range for data generation
START_DATE = datetime(2024, 10, 1)
END_DATE = datetime(2025, 11, 17)
NUM_DAYS = (END_DATE - START_DATE).days

# Restaurant operating hours
OPEN_HOUR = 10  # 10 AM
CLOSE_HOUR = 22  # 10 PM

# Menu items (with intentional inconsistencies in naming)
MENU_ITEMS = {
    # Appetizers
    "Wings": {"price": 12.99, "category": "Appetizers", "prep_time": 15},
    "Buffalo Wings": {
        "price": 12.99,
        "category": "Apps",
        "prep_time": 15,
    },  # Duplicate!
    "Mozzarella Sticks": {"price": 9.99, "category": "Appetizers", "prep_time": 10},
    "Mozz Sticks": {"price": 9.99, "category": "Apps", "prep_time": 10},  # Duplicate!
    "Loaded Nachos": {"price": 11.99, "category": "Appetizers", "prep_time": 12},
    "Spinach Artichoke Dip": {"price": 10.99, "category": "Appetizers", "prep_time": 8},
    # Entrees
    "Classic Burger": {"price": 14.99, "category": "Entrees", "prep_time": 18},
    "Cheeseburger": {"price": 15.99, "category": "Entrees", "prep_time": 18},
    "Bacon Burger": {"price": 16.99, "category": "Entrees", "prep_time": 20},
    "Grilled Chicken Sandwich": {
        "price": 13.99,
        "category": "Entrees",
        "prep_time": 15,
    },
    "BBQ Chicken Pizza": {"price": 17.99, "category": "Entrees", "prep_time": 25},
    "Margherita Pizza": {"price": 15.99, "category": "Entrees", "prep_time": 25},
    "Pepperoni Pizza": {"price": 16.99, "category": "Entrees", "prep_time": 25},
    "Caesar Salad": {"price": 11.99, "category": "Salads", "prep_time": 8},
    "House Salad": {"price": 9.99, "category": "Salads", "prep_time": 8},
    "Ribeye Steak": {"price": 28.99, "category": "Entrees", "prep_time": 30},
    "Salmon Fillet": {"price": 22.99, "category": "Entrees", "prep_time": 20},
    "Pasta Carbonara": {"price": 16.99, "category": "Entrees", "prep_time": 18},
    "Chicken Alfredo": {"price": 17.99, "category": "Entrees", "prep_time": 18},
    # Sides
    "French Fries": {"price": 4.99, "category": "Sides", "prep_time": 8},
    "Fries": {"price": 4.99, "category": "Sides", "prep_time": 8},  # Duplicate!
    "Sweet Potato Fries": {"price": 5.99, "category": "Sides", "prep_time": 10},
    "Onion Rings": {"price": 5.99, "category": "Sides", "prep_time": 10},
    "Cole Slaw": {"price": 3.99, "category": "Sides", "prep_time": 2},
    "Steamed Vegetables": {"price": 4.99, "category": "Sides", "prep_time": 8},
    # Desserts
    "Chocolate Cake": {"price": 7.99, "category": "Desserts", "prep_time": 5},
    "Cheesecake": {"price": 8.99, "category": "Desserts", "prep_time": 5},
    "Ice Cream": {"price": 5.99, "category": "Desserts", "prep_time": 3},
    "Brownie Sundae": {"price": 8.99, "category": "Desserts", "prep_time": 5},
    # Beverages
    "Coke": {"price": 2.99, "category": "Beverages", "prep_time": 1},
    "Diet Coke": {"price": 2.99, "category": "Beverages", "prep_time": 1},
    "Sprite": {"price": 2.99, "category": "Beverages", "prep_time": 1},
    "Iced Tea": {"price": 2.99, "category": "Beverages", "prep_time": 1},
    "Coffee": {"price": 2.49, "category": "Beverages", "prep_time": 2},
    "Beer": {"price": 5.99, "category": "Alcohol", "prep_time": 1},
    "Wine": {"price": 8.99, "category": "Alcohol", "prep_time": 1},
}


# ============================================
# HELPER FUNCTIONS
# ============================================


def get_hourly_traffic_multiplier(hour, day_of_week):
    """Simulate realistic traffic patterns"""
    # Base multiplier
    multiplier = 0.3

    # Lunch rush (11am-2pm)
    if 11 <= hour <= 13:
        multiplier = 1.5

    # Dinner rush (5pm-8pm)
    elif 17 <= hour <= 20:
        multiplier = 2.0

    # Off-peak hours
    elif hour == 10 or hour == 14 or hour == 15:
        multiplier = 0.7
    elif hour == 21:
        multiplier = 0.5

    # Weekend boost
    if day_of_week >= 5:  # Saturday, Sunday
        multiplier *= 1.3

    # Friday night boost
    if day_of_week == 4 and hour >= 17:
        multiplier *= 1.4

    return multiplier


def generate_party_size():
    """Realistic party size distribution"""
    return np.random.choice(
        [1, 2, 3, 4, 5, 6, 7, 8], p=[0.15, 0.35, 0.15, 0.20, 0.08, 0.04, 0.02, 0.01]
    )


def generate_order_items(party_size):
    """Generate realistic items for an order"""
    items = []

    # Each person orders 1-2 items on average
    num_items = int(party_size * np.random.uniform(0.8, 1.5))
    num_items = max(1, num_items)

    # Higher chance of popular items
    item_names = list(MENU_ITEMS.keys())
    weights = [1.0] * len(item_names)

    # Boost popular items
    popular = ["Classic Burger", "Wings", "French Fries", "Coke", "Pizza"]
    for i, name in enumerate(item_names):
        if any(p in name for p in popular):
            weights[i] = 2.0

    # Normalize weights
    total = sum(weights)
    weights = [w / total for w in weights]

    selected_items = np.random.choice(
        item_names, size=num_items, p=weights, replace=True
    )

    for item_name in selected_items:
        quantity = 1 if np.random.random() > 0.1 else 2  # 10% chance of ordering 2
        items.append(
            {
                "item_name": item_name,
                "quantity": quantity,
                "unit_price": MENU_ITEMS[item_name]["price"],
            }
        )

    # 70% chance of beverages
    if np.random.random() < 0.7:
        num_drinks = np.random.randint(1, party_size + 1)
        for _ in range(num_drinks):
            drink = np.random.choice(
                ["Coke", "Diet Coke", "Sprite", "Iced Tea", "Coffee", "Beer", "Wine"]
            )
            items.append(
                {
                    "item_name": drink,
                    "quantity": 1,
                    "unit_price": MENU_ITEMS[drink]["price"],
                }
            )

    return items


def add_data_quality_issues(df):
    """Introduce realistic data quality issues"""
    df = df.copy()

    # 1. Missing values (5% of timestamps)
    missing_indices = np.random.choice(
        df.index, size=int(len(df) * 0.05), replace=False
    )
    df.loc[missing_indices, "order_timestamp"] = None

    # 2. Inconsistent formatting in order_type
    df["order_type"] = df["order_type"].replace(
        {"dine_in": np.random.choice(["dine_in", "Dine In", "DINE_IN", "dinein"])}
    )

    # 3. Some negative values (data entry errors)
    error_indices = np.random.choice(df.index, size=int(len(df) * 0.02), replace=False)
    df.loc[error_indices, "tip_amount"] = df.loc[error_indices, "tip_amount"] * -1

    # 4. Duplicate order IDs (1% of orders)
    dup_indices = np.random.choice(
        df.index[:-1], size=int(len(df) * 0.01), replace=False
    )
    for idx in dup_indices:
        df.loc[idx + 1, "order_id"] = df.loc[idx, "order_id"]

    # 5. Outlier party sizes
    outlier_indices = np.random.choice(
        df.index, size=int(len(df) * 0.01), replace=False
    )
    df.loc[outlier_indices, "party_size"] = np.random.choice([15, 20, 25, 0, -1])

    return df


# ============================================
# GENERATE ORDERS DATA
# ============================================


def generate_orders_data():
    """Generate main orders table"""
    orders = []
    order_id = 1000  # Start from 1000

    for day_offset in range(NUM_DAYS):
        current_date = START_DATE + timedelta(days=day_offset)
        day_of_week = current_date.weekday()

        # Generate orders throughout the day
        for hour in range(OPEN_HOUR, CLOSE_HOUR + 1):
            # Number of orders this hour
            base_orders = 8
            multiplier = get_hourly_traffic_multiplier(hour, day_of_week)
            num_orders = int(base_orders * multiplier)
            num_orders = max(1, num_orders)  # At least 1 order

            for _ in range(num_orders):
                # Random minute within the hour
                minute = np.random.randint(0, 60)
                order_timestamp = current_date.replace(hour=hour, minute=minute)

                party_size = generate_party_size()
                order_type = np.random.choice(
                    ["dine_in", "takeout", "delivery"], p=[0.70, 0.20, 0.10]
                )

                # Generate order items
                items = generate_order_items(party_size)

                # Calculate totals
                subtotal = sum(item["unit_price"] * item["quantity"] for item in items)
                tax_amount = subtotal * 0.0895  # 8.95% tax (Tulsa rate)

                # Tip (only for dine_in, 15-25% average)
                if order_type == "dine_in":
                    tip_pct = np.random.uniform(0.10, 0.25)
                    tip_amount = subtotal * tip_pct
                else:
                    tip_amount = 0

                order_total = subtotal + tax_amount + tip_amount

                # Duration (time from order to completion)
                avg_prep_time = np.mean(
                    [MENU_ITEMS[item["item_name"]]["prep_time"] for item in items]
                )
                duration = int(
                    avg_prep_time + np.random.uniform(-5, 10)
                )  # Add variance
                duration = max(5, duration)

                # Order status (95% completed, 5% cancelled)
                order_status = "completed" if np.random.random() < 0.95 else "cancelled"

                # Table number (only for dine_in)
                table_number = (
                    f"T{np.random.randint(1, 31)}" if order_type == "dine_in" else None
                )

                # Server ID (only for dine_in)
                server_id = (
                    np.random.randint(100, 115) if order_type == "dine_in" else None
                )

                orders.append(
                    {
                        "order_id": order_id,
                        "order_timestamp": order_timestamp,
                        "party_size": party_size,
                        "order_total": round(order_total, 2),
                        "subtotal": round(subtotal, 2),
                        "tax_amount": round(tax_amount, 2),
                        "tip_amount": round(tip_amount, 2),
                        "order_type": order_type,
                        "table_number": table_number,
                        "server_id": server_id,
                        "order_status": order_status,
                        "duration_minutes": duration,
                        "items": items,  # Keep for order_items generation
                    }
                )

                order_id += 1

    return pd.DataFrame(orders)


def generate_order_items_data(orders_df):
    """Generate order_items junction table"""
    order_items = []
    order_item_id = 1

    for _, order in orders_df.iterrows():
        for item in order["items"]:
            item_total = item["unit_price"] * item["quantity"]

            order_items.append(
                {
                    "order_item_id": order_item_id,
                    "order_id": order["order_id"],
                    "item_name": item["item_name"],
                    "quantity": item["quantity"],
                    "unit_price": item["unit_price"],
                    "item_total": round(item_total, 2),
                    "special_instructions": None,  # Could add random special requests
                }
            )

            order_item_id += 1

    return pd.DataFrame(order_items)


def generate_wait_times_data():
    """Generate wait times log"""
    wait_times = []
    wait_time_id = 1

    for day_offset in range(NUM_DAYS):
        current_date = START_DATE + timedelta(days=day_offset)
        day_of_week = current_date.weekday()

        # Generate wait time logs throughout the day
        for hour in range(OPEN_HOUR, CLOSE_HOUR + 1):
            multiplier = get_hourly_traffic_multiplier(hour, day_of_week)

            # More wait time logs during busy hours
            num_logs = int(5 * multiplier)
            num_logs = max(1, num_logs)

            for _ in range(num_logs):
                minute = np.random.randint(0, 60)
                log_timestamp = current_date.replace(hour=hour, minute=minute)

                party_size = generate_party_size()

                # Current occupancy (higher during peak hours)
                base_occupancy = 40
                occupancy_boost = multiplier * 20
                current_occupancy = (
                    base_occupancy + occupancy_boost + np.random.uniform(-10, 10)
                )
                current_occupancy = np.clip(current_occupancy, 0, 100)

                # Current party count (estimate)
                current_party_count = int(
                    current_occupancy / 100 * 30
                )  # Assume 30 tables

                # Quoted wait time (staff estimate)
                if current_occupancy < 50:
                    quoted_wait = np.random.randint(5, 15)
                elif current_occupancy < 75:
                    quoted_wait = np.random.randint(15, 30)
                else:
                    quoted_wait = np.random.randint(25, 45)

                # Actual wait time (add variance, staff aren't perfect)
                actual_variance = np.random.uniform(-0.3, 0.5)  # -30% to +50% error
                actual_wait = int(quoted_wait * (1 + actual_variance))
                actual_wait = max(0, actual_wait)

                # Seated timestamp
                seated_timestamp = log_timestamp + timedelta(minutes=actual_wait)

                wait_times.append(
                    {
                        "wait_time_id": wait_time_id,
                        "log_timestamp": log_timestamp,
                        "party_size": party_size,
                        "quoted_wait_minutes": quoted_wait,
                        "actual_wait_minutes": actual_wait,
                        "seated_timestamp": seated_timestamp,
                        "day_of_week": day_of_week,
                        "hour_of_day": hour,
                        "current_party_count": current_party_count,
                        "current_table_occupancy_pct": round(current_occupancy, 2),
                        "wait_type": "walk_in",  # Could add 'reservation', 'call_ahead'
                    }
                )

                wait_time_id += 1

    return pd.DataFrame(wait_times)


def generate_external_factors_data():
    """Generate external factors (weather, events, holidays)"""
    external_factors = []

    # Tulsa holidays in the date range
    holidays = {
        datetime(2024, 11, 28): "Thanksgiving",
        datetime(2024, 12, 25): "Christmas",
        datetime(2025, 1, 1): "New Year's Day",
        datetime(2025, 7, 4): "Independence Day",
        datetime(2025, 9, 1): "Labor Day",
        datetime(2025, 11, 27): "Thanksgiving",
    }

    # Sample events
    events = [
        {
            "date": datetime(2024, 10, 15),
            "name": "Thunder vs Lakers",
            "type": "sports",
            "attendance": 18000,
            "distance": 0.8,
        },
        {
            "date": datetime(2024, 11, 2),
            "name": "Country Music Festival",
            "type": "concert",
            "attendance": 15000,
            "distance": 1.2,
        },
        {
            "date": datetime(2025, 1, 20),
            "name": "Thunder vs Warriors",
            "type": "sports",
            "attendance": 18500,
            "distance": 0.8,
        },
        {
            "date": datetime(2025, 3, 15),
            "name": "Food Truck Festival",
            "type": "festival",
            "attendance": 8000,
            "distance": 2.0,
        },
    ]

    for day_offset in range(NUM_DAYS):
        current_date = START_DATE + timedelta(days=day_offset)
        day_of_week = current_date.weekday()

        # Check if holiday
        is_holiday = current_date in holidays
        holiday_name = holidays.get(current_date)

        # Weather (simplified, seasonal patterns)
        month = current_date.month
        if month in [12, 1, 2]:  # Winter
            weather_options = ["cloudy", "rainy", "snowy"]
            temp_high = np.random.uniform(30, 50)
            temp_low = np.random.uniform(20, 40)
            precip = np.random.uniform(0, 0.5) if np.random.random() < 0.4 else 0
        elif month in [3, 4, 5]:  # Spring
            weather_options = ["sunny", "cloudy", "rainy"]
            temp_high = np.random.uniform(55, 75)
            temp_low = np.random.uniform(45, 60)
            precip = np.random.uniform(0, 1.0) if np.random.random() < 0.5 else 0
        elif month in [6, 7, 8]:  # Summer
            weather_options = ["sunny", "sunny", "cloudy"]
            temp_high = np.random.uniform(80, 100)
            temp_low = np.random.uniform(65, 80)
            precip = np.random.uniform(0, 0.3) if np.random.random() < 0.2 else 0
        else:  # Fall
            weather_options = ["sunny", "cloudy", "rainy"]
            temp_high = np.random.uniform(60, 80)
            temp_low = np.random.uniform(50, 65)
            precip = np.random.uniform(0, 0.8) if np.random.random() < 0.3 else 0

        weather_condition = np.random.choice(weather_options)

        # Check for events
        event_info = next(
            (e for e in events if e["date"].date() == current_date.date()), None
        )

        external_factors.append(
            {
                "factor_date": current_date.date(),
                "day_of_week": day_of_week,
                "is_holiday": is_holiday,
                "holiday_name": holiday_name,
                "weather_condition": weather_condition,
                "temperature_high_f": round(temp_high, 1),
                "temperature_low_f": round(temp_low, 1),
                "precipitation_inches": round(precip, 2),
                "local_event_name": event_info["name"] if event_info else None,
                "local_event_type": event_info["type"] if event_info else None,
                "event_attendance_estimated": (
                    event_info["attendance"] if event_info else None
                ),
                "event_distance_miles": event_info["distance"] if event_info else None,
            }
        )

    return pd.DataFrame(external_factors)


# ============================================
# MAIN EXECUTION
# ============================================

if __name__ == "__main__":
    print("🍽️  Generating Dinemetra dummy data...")
    print(f"📅 Date range: {START_DATE.date()} to {END_DATE.date()}")

    # Create data directory
    import os

    os.makedirs("data", exist_ok=True)

    # Generate orders
    print("\n📊 Generating orders data...")
    orders_df = generate_orders_data()
    print(f"   ✓ Generated {len(orders_df)} orders")

    # Introduce data quality issues
    print("🔧 Adding realistic data quality issues...")
    orders_df_dirty = add_data_quality_issues(orders_df)

    # Generate order items
    print("📦 Generating order items...")
    order_items_df = generate_order_items_data(orders_df)
    print(f"   ✓ Generated {len(order_items_df)} order items")

    # Generate wait times
    print("⏱️  Generating wait times...")
    wait_times_df = generate_wait_times_data()
    print(f"   ✓ Generated {len(wait_times_df)} wait time logs")

    # Generate external factors
    print("🌤️  Generating external factors...")
    external_factors_df = generate_external_factors_data()
    print(f"   ✓ Generated {len(external_factors_df)} daily records")

    # Save to CSV
    print("\n💾 Saving CSV files...")
    orders_df_dirty.drop("items", axis=1).to_csv("data/orders_raw.csv", index=False)
    order_items_df.to_csv("data/order_items_raw.csv", index=False)
    wait_times_df.to_csv("data/wait_times_raw.csv", index=False)
    external_factors_df.to_csv("data/external_factors_raw.csv", index=False)

    # Save menu items as reference
    menu_df = pd.DataFrame(
        [
            {
                "item_name": name,
                "price": info["price"],
                "category": info["category"],
                "prep_time_minutes": info["prep_time"],
            }
            for name, info in MENU_ITEMS.items()
        ]
    )
    menu_df.to_csv("data/menu_items_reference.csv", index=False)

    print("\n✅ Data generation complete!")
    print("\n📁 Generated files:")
    print("   - data/orders_raw.csv")
    print("   - data/order_items_raw.csv")
    print("   - data/wait_times_raw.csv")
    print("   - data/external_factors_raw.csv")
    print("   - data/menu_items_reference.csv")

    print("\n📈 Data Summary:")
    print(f"   Orders: {len(orders_df_dirty)}")
    print(f"   Order Items: {len(order_items_df)}")
    print(f"   Wait Times: {len(wait_times_df)}")
    print(f"   External Factors: {len(external_factors_df)}")
    print(f"   Menu Items: {len(menu_df)}")

    print("\n⚠️  Data Quality Issues (intentional for ETL testing):")
    print(
        f"   - Missing timestamps: ~{orders_df_dirty['order_timestamp'].isna().sum()}"
    )
    print(f"   - Inconsistent order_type formatting: Yes")
    print(
        f"   - Duplicate order IDs: ~{len(orders_df_dirty) - len(orders_df_dirty['order_id'].unique())}"
    )
    print(
        f"   - Menu item name duplicates: Yes (Wings/Buffalo Wings, Fries/French Fries)"
    )
    print(f"   - Outlier party sizes: Yes")

    print("\n🎉 Ready for ETL pipeline testing!")
