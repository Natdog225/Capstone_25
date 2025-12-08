"""
Train Item Sales Model from Monthly Folder Structure
Works with: data/real/2025-01/Items.csv, data/real/2025-02/Items.csv, etc.

Usage:
    python train_model_monthly_folders.py data/real/
"""

import pandas as pd
import pickle
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import sys
import os
from datetime import datetime
import glob


def find_monthly_csv_files(base_folder):
    """Find Items.csv files in monthly subdirectories"""
    # Look for patterns like: data/real/2025-01/Items.csv
    pattern1 = os.path.join(base_folder, "*/Items.csv")
    pattern2 = os.path.join(base_folder, "*/*Items.csv")

    files = glob.glob(pattern1) + glob.glob(pattern2)
    return sorted(set(files))


def train_model_from_monthly_folders(base_folder):
    """Train model from monthly folder structure"""

    print("=" * 80)
    print("TRAINING MODEL FROM MONTHLY FOLDERS")
    print("=" * 80)
    print()

    # Find all Items CSV files in monthly folders
    items_files = find_monthly_csv_files(base_folder)

    if not items_files:
        print(f"❌ No Items.csv files found in: {base_folder}")
        print(f"   Looking for structure like:")
        print(f"   {base_folder}/2025-01/Items.csv")
        print(f"   {base_folder}/2025-02/Items.csv")
        print(f"   etc.")
        return False

    print(f"📂 Found {len(items_files)} months of data:")
    for f in items_files:
        # Extract month from path
        folder_name = os.path.basename(os.path.dirname(f))
        print(f"   • {folder_name}/Items.csv")
    print()

    # Load and combine all months
    all_data = []

    for month_num, items_file in enumerate(items_files, 1):
        folder_name = os.path.basename(os.path.dirname(items_file))
        print(f"📥 Loading {folder_name}...")

        try:
            items_df = pd.read_csv(items_file)
            items_clean = items_df[items_df["Item"].notna()].copy()
            items_clean["Qty sold"] = pd.to_numeric(
                items_clean["Qty sold"], errors="coerce"
            )
            items_clean["Avg. price"] = pd.to_numeric(
                items_clean["Avg. price"], errors="coerce"
            )

            month_count = 0

            # Add month information
            for idx, row in items_clean.iterrows():
                item_name = str(row["Item"])
                category = str(row.get("Sales Category", "Unknown"))
                qty_sold = row["Qty sold"]
                price = row["Avg. price"]

                if pd.isna(qty_sold) or qty_sold == 0 or pd.isna(price):
                    continue

                # Create features with month and weather sensitivity
                features = {
                    "item_name": item_name,
                    "category": category,
                    "price": price,
                    "qty_sold": qty_sold,
                    "month": month_num,
                    "month_name": folder_name,
                    # Weather sensitivity flags
                    "is_fried": (
                        1
                        if "fry" in item_name.lower() or "fried" in item_name.lower()
                        else 0
                    ),
                    "is_banh_mi": 1 if "banh mi" in item_name.lower() else 0,
                    "is_bowl": 1 if "bowl" in item_name.lower() else 0,
                    "is_salad": 1 if "salad" in item_name.lower() else 0,
                    "is_beverage": (
                        1 if category == "NA Beverage" or category == "Beer" else 0
                    ),
                    "is_dessert": (
                        1
                        if "cookie" in item_name.lower()
                        or "dessert" in category.lower()
                        else 0
                    ),
                }
                all_data.append(features)
                month_count += 1

            print(f"   ✅ Loaded {month_count} items from {folder_name}")

        except Exception as e:
            print(f"   ⚠️  Error loading {folder_name}: {e}")
            continue

    if not all_data:
        print("❌ No data loaded from any files!")
        return False

    df = pd.DataFrame(all_data)
    print()
    print(f"🎉 Combined {len(df)} data points from {len(items_files)} months!")
    print()

    # Analyze seasonal patterns
    print("=" * 80)
    print("SEASONAL ANALYSIS")
    print("=" * 80)
    print()

    monthly_totals = (
        df.groupby("month_name")
        .agg({"qty_sold": "sum", "price": "mean"})
        .reindex(df.groupby("month_name")["month"].first().sort_values().index)
    )

    print("📊 Sales by Month:")
    max_qty = monthly_totals["qty_sold"].max()
    for month, row in monthly_totals.iterrows():
        qty = int(row["qty_sold"])
        bar_length = int((qty / max_qty) * 40) if max_qty > 0 else 0
        bar = "█" * bar_length
        print(f"  {month:12s}: {bar:40s} {qty:,} items sold")
    print()

    # Find seasonal items
    print("🌡️  Seasonal Patterns:")

    # Group by item and analyze variance
    item_patterns = df.groupby("item_name").agg(
        {"qty_sold": ["sum", "std", "mean"], "month": "count"}
    )
    item_patterns.columns = ["total_qty", "qty_std", "qty_mean", "months_present"]

    # Items present in multiple months with variance
    seasonal_items = item_patterns[
        (item_patterns["months_present"] >= 3)
        & (item_patterns["qty_std"] > item_patterns["qty_mean"] * 0.3)
    ].nlargest(10, "qty_std")

    if len(seasonal_items) > 0:
        print("  Items with strong seasonal variance:")
        for item_name, row in seasonal_items.iterrows():
            print(f"    • {item_name[:40]:40s} (±{row['qty_std']:.0f} items/month)")
    else:
        print("  Not enough data for seasonal variance analysis")
    print()

    # Top sellers across all months
    print("🏆 Top 10 Best Sellers (all months combined):")
    top_sellers = (
        df.groupby("item_name")
        .agg({"qty_sold": "sum", "price": "mean", "category": "first"})
        .nlargest(10, "qty_sold")
    )

    for item_name, row in top_sellers.iterrows():
        qty = int(row["qty_sold"])
        price = row["price"]
        cat = row["category"]
        print(f"  • {item_name[:30]:30s} - {qty:5,} sold @ ${price:.2f} ({cat})")
    print()

    # Encode categorical variables
    print("🔧 Encoding categories...")
    le_category = LabelEncoder()
    le_item = LabelEncoder()

    df["category_encoded"] = le_category.fit_transform(df["category"])
    df["item_encoded"] = le_item.fit_transform(df["item_name"])

    # Prepare features and target
    feature_cols = [
        "price",
        "month",
        "item_encoded",
        "is_fried",
        "is_banh_mi",
        "is_bowl",
        "is_salad",
        "is_beverage",
        "is_dessert",
        "category_encoded",
    ]
    X = df[feature_cols]
    y = df["qty_sold"]

    print(f"✅ Features: {', '.join(feature_cols)}")
    print(f"✅ Training samples: {len(df):,}")
    print()

    # Train model
    print("🎓 Training Random Forest model...")
    model = RandomForestRegressor(
        n_estimators=200, max_depth=15, min_samples_split=10, random_state=42, n_jobs=-1
    )
    model.fit(X, y)
    print("✅ Model trained!")
    print()

    # Feature importance
    print("📈 Feature Importance:")
    importances = model.feature_importances_
    for feature, importance in sorted(
        zip(feature_cols, importances), key=lambda x: x[1], reverse=True
    )[:8]:
        bar = "█" * int(importance * 50)
        print(f"  {feature:20s}: {bar} {importance:.3f}")
    print()

    # Save model
    print("💾 Saving model...")

    model_data = {
        "model": model,
        "label_encoder_category": le_category,
        "label_encoder_item": le_item,
        "feature_cols": feature_cols,
        "trained_date": datetime.now().isoformat(),
        "num_items": len(df["item_name"].unique()),
        "num_samples": len(df),
        "months_trained": len(items_files),
        "categories": list(le_category.classes_),
        "items": list(le_item.classes_),
        "monthly_folders": [os.path.basename(os.path.dirname(f)) for f in items_files],
        "seasonal_patterns": {
            "monthly_totals": {
                str(k): v for k, v in monthly_totals.to_dict()["qty_sold"].items()
            },
            "top_seller": top_sellers.index[0],
            "seasonal_items": (
                seasonal_items.index.tolist() if len(seasonal_items) > 0 else []
            ),
        },
    }

    # Determine output path
    output_path = "item_sales_monthly.pkl"
    if os.path.exists("data/models"):
        output_path = "data/models/item_sales_monthly.pkl"
        print(f"✅ Found data/models directory")

    with open(output_path, "wb") as f:
        pickle.dump(model_data, f)

    file_size = os.path.getsize(output_path) / 1024
    print(f"✅ Model saved to: {output_path} ({file_size:.1f} KB)")
    print()

    # Test predictions
    print("=" * 80)
    print("TESTING PREDICTIONS")
    print("=" * 80)
    print()

    # Test with top seller across different months
    top_seller_name = top_sellers.index[0]
    top_seller_data = df[df["item_name"] == top_seller_name]

    if len(top_seller_data) > 0:
        print(f"Testing: {top_seller_name}")
        print()

        for month_name in top_seller_data.sort_values("month")["month_name"].unique():
            month_data = top_seller_data[
                top_seller_data["month_name"] == month_name
            ].iloc[0]

            test_features = {col: month_data[col] for col in feature_cols}
            X_test = pd.DataFrame([test_features])[feature_cols]
            prediction = model.predict(X_test)[0]
            actual = month_data["qty_sold"]

            accuracy = (
                (1 - abs(prediction - actual) / actual) * 100 if actual > 0 else 0
            )

            print(
                f"  {month_name:12s}: Actual {int(actual):4d} | Predicted {int(prediction):4d} | {accuracy:5.1f}% accurate"
            )

    print()

    # Summary
    print("=" * 80)
    print("✅ SUCCESS!")
    print("=" * 80)
    print(
        f"""
📊 Model Statistics:
   • Training samples: {len(df):,}
   • Unique items: {len(df['item_name'].unique())}
   • Months of data: {len(items_files)}
   • Categories: {len(le_category.classes_)}

🎯 Model Features:
   • Seasonal patterns (month-by-month)
   • Item-specific predictions
   • Weather sensitivity (fried, banh mi, bowls)
   • Category intelligence
   • Price relationships

📁 Model saved to: {output_path}

🚀 Next Steps:
   1. Restart your server:
      uvicorn app.main:app --reload
   
   2. Test predictions:
      curl -X POST "http://localhost:8000/api/predictions/sales" \\
        -H "Content-Type: application/json" \\
        -d '{{"item_id": 1, "item_name": "{top_seller_name}", "category": "Rice Bowls"}}'

💡 Your predictions now understand:
   • Seasonal variations across {len(items_files)} months
   • Item popularity trends
   • Monthly sales patterns
   • Weather + season combinations
"""
    )
    print("=" * 80)

    return True


if __name__ == "__main__":
    if len(sys.argv) > 1:
        base_folder = sys.argv[1]
    else:
        print("Enter the path to your data folder:")
        print("(Should contain monthly folders like 2025-01/, 2025-02/, etc.)")
        base_folder = input("> ").strip()

    if not base_folder or not os.path.exists(base_folder):
        print(f"❌ Folder not found: {base_folder}")
        sys.exit(1)

    success = train_model_from_monthly_folders(base_folder)
    sys.exit(0 if success else 1)
