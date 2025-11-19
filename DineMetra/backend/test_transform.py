"""
Test the ETL transformation process
"""

import sys
from pathlib import Path
import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from etl.extract import DataExtractor
from etl.transform import DataTransformer


def test_transformation():
    """Test the full extraction + transformation pipeline"""
    print("🧪 Testing ETL Transformation...")

    # Step 1: Extract raw data
    print("\n📥 Step 1: Extracting raw data...")
    extractor = DataExtractor(data_dir="data")
    raw_data = extractor.extract_all()

    # Step 2: Transform data
    print("\n🔧 Step 2: Transforming data...")
    transformer = DataTransformer()
    cleaned_data = transformer.transform_all(raw_data)

    # Step 3: Verify transformations
    print("\n✅ Transformation Test Results:")

    # Orders
    print("\n📦 ORDERS:")
    print(f"   Raw: {len(raw_data['orders'])} → Clean: {len(cleaned_data['orders'])}")
    print(
        f"   Missing timestamps: {raw_data['orders']['order_timestamp'].isna().sum()} → {cleaned_data['orders']['order_timestamp'].isna().sum()}"
    )
    print(
        f"   Negative tips: {(raw_data['orders']['tip_amount'] < 0).sum()} → {(cleaned_data['orders']['tip_amount'] < 0).sum()}"
    )
    print(f"   Unique order_types: {cleaned_data['orders']['order_type'].unique()}")

    # Order Items
    print("\n📦 ORDER ITEMS:")
    print(
        f"   Raw: {len(raw_data['order_items'])} → Clean: {len(cleaned_data['order_items'])}"
    )
    print(
        f"   Negative quantities: {(raw_data['order_items']['quantity'] <= 0).sum()} → {(cleaned_data['order_items']['quantity'] <= 0).sum()}"
    )

    # Menu Items
    print("\n🍔 MENU ITEMS:")
    print(
        f"   Raw: {len(raw_data['menu_items'])} → Clean: {len(cleaned_data['menu_items'])}"
    )
    print(
        f"   Duplicates removed: {len(raw_data['menu_items']) - len(cleaned_data['menu_items'])}"
    )
    print(f"   Unique items: {cleaned_data['menu_items']['item_name'].nunique()}")
    print(f"   Sample items: {list(cleaned_data['menu_items']['item_name'].head(5))}")

    # Wait Times
    print("\n⏱️  WAIT TIMES:")
    print(
        f"   Raw: {len(raw_data['wait_times'])} → Clean: {len(cleaned_data['wait_times'])}"
    )
    print(
        f"   Negative wait times: {(raw_data['wait_times']['quoted_wait_minutes'] < 0).sum()} → {(cleaned_data['wait_times']['quoted_wait_minutes'] < 0).sum()}"
    )

    # External Factors
    print("\n🌤️  EXTERNAL FACTORS:")
    print(
        f"   Raw: {len(raw_data['external_factors'])} → Clean: {len(cleaned_data['external_factors'])}"
    )
    print(
        f"   Date range: {cleaned_data['external_factors']['factor_date'].min()} to {cleaned_data['external_factors']['factor_date'].max()}"
    )
    print(
        f"   Weather conditions: {cleaned_data['external_factors']['weather_condition'].unique()}"
    )

    # Step 4: Sample cleaned data
    print("\n📊 Sample Cleaned Data:")
    print("\nOrders (first 3):")
    print(
        cleaned_data["orders"][
            ["order_id", "order_timestamp", "party_size", "order_type", "order_total"]
        ].head(3)
    )

    print("\nMenu Items (first 5):")
    print(cleaned_data["menu_items"][["item_name", "category", "price"]].head(5))

    print("\n🎉 Transformation test complete!")
    print("\n📈 Overall Data Quality:")
    total_raw = sum(len(df) for df in raw_data.values())
    total_clean = sum(len(df) for df in cleaned_data.values())
    retention = total_clean / total_raw * 100
    print(f"   Total records: {total_raw:,} → {total_clean:,}")
    print(f"   Retention rate: {retention:.1f}%")
    print(f"   Records removed: {total_raw - total_clean:,}")

    return cleaned_data


if __name__ == "__main__":
    cleaned_data = test_transformation()
