"""
Dinemetra ETL - Transform Phase
Cleans and normalizes raw POS data for database loading

This script:
1. Fixes data quality issues identified in extraction
2. Standardizes formats and values
3. Deduplicates records
4. Validates data integrity
5. Prepares clean DataFrames for loading

Run: python -m etl.transform
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import json
from pathlib import Path
from typing import Dict, List, Tuple

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DataTransformer:
    """
    Handles transformation and cleaning of raw POS data
    """

    def __init__(self):
        """Initialize transformer with transformation rules"""
        self.transformation_report = {
            "timestamp": datetime.now().isoformat(),
            "transformations_applied": {},
            "records_cleaned": 0,
            "records_removed": 0,
            "records_final": 0,
        }

        # Standardization mappings
        self.order_type_mapping = {
            "dine_in": "dine_in",
            "dinein": "dine_in",
            "dine in": "dine_in",
            "DINE_IN": "dine_in",
            "Dine In": "dine_in",
            "takeout": "takeout",
            "take out": "takeout",
            "TAKEOUT": "takeout",
            "delivery": "delivery",
            "DELIVERY": "delivery",
        }

        # Menu item deduplication mapping
        self.menu_item_mapping = {
            "buffalo wings": "Wings",
            "wings": "Wings",
            "mozz sticks": "Mozzarella Sticks",
            "mozzarella sticks": "Mozzarella Sticks",
            "fries": "French Fries",
            "french fries": "French Fries",
        }

    def transform_all(
        self, raw_data: Dict[str, pd.DataFrame]
    ) -> Dict[str, pd.DataFrame]:
        """
        Transform all datasets

        Args:
            raw_data: Dictionary of raw DataFrames from extraction

        Returns:
            Dictionary of cleaned DataFrames ready for loading
        """
        logger.info("🔧 Starting data transformation process...")

        cleaned_data = {}

        # Transform each dataset (order matters due to dependencies)
        cleaned_data["menu_items"] = self.transform_menu_items(raw_data["menu_items"])
        cleaned_data["orders"] = self.transform_orders(raw_data["orders"])
        cleaned_data["order_items"] = self.transform_order_items(
            raw_data["order_items"], cleaned_data["orders"], cleaned_data["menu_items"]
        )
        cleaned_data["wait_times"] = self.transform_wait_times(raw_data["wait_times"])
        cleaned_data["external_factors"] = self.transform_external_factors(
            raw_data["external_factors"]
        )

        # Calculate summary stats
        self._calculate_transformation_summary(raw_data, cleaned_data)

        # Log summary
        self._log_transformation_summary()

        # Save transformation report
        self._save_transformation_report()

        return cleaned_data

    # ========================================
    # MENU ITEMS TRANSFORMATION
    # ========================================

    def transform_menu_items(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and deduplicate menu items

        Transformations:
        - Remove duplicates (case-insensitive)
        - Standardize item names
        - Ensure positive prices
        - Fill missing categories
        """
        logger.info("🍔 Transforming menu items...")

        df = df.copy()
        initial_count = len(df)
        transformations = []

        # 1. Standardize item names (trim whitespace, title case)
        df["item_name"] = df["item_name"].str.strip().str.title()
        transformations.append("Standardized item names")

        # 2. Apply deduplication mapping
        df["item_name_lower"] = df["item_name"].str.lower()
        df["item_name"] = (
            df["item_name_lower"].map(self.menu_item_mapping).fillna(df["item_name"])
        )
        df = df.drop("item_name_lower", axis=1)
        transformations.append("Applied item name deduplication mapping")

        # 3. Remove exact duplicates (keep first occurrence)
        duplicates_removed = df.duplicated(subset=["item_name"], keep="first").sum()
        df = df.drop_duplicates(subset=["item_name"], keep="first")
        if duplicates_removed > 0:
            transformations.append(f"Removed {duplicates_removed} duplicate menu items")

        # 4. Ensure positive prices
        negative_prices = (df["price"] <= 0).sum()
        if negative_prices > 0:
            df.loc[df["price"] <= 0, "price"] = df["price"].median()
            transformations.append(
                f"Fixed {negative_prices} non-positive prices (set to median)"
            )

        # 5. Standardize categories
        df["category"] = df["category"].str.strip().str.title()
        # Map common variations
        category_mapping = {
            "Apps": "Appetizers",
            "App": "Appetizers",
            "Entree": "Entrees",
            "Main": "Entrees",
            "Drinks": "Beverages",
            "Beverage": "Beverages",
        }
        df["category"] = df["category"].replace(category_mapping)
        transformations.append("Standardized categories")

        # 6. Fill missing prep times with category averages
        null_prep = df["prep_time_minutes"].isna().sum()
        if null_prep > 0:
            category_avg_prep = df.groupby("category")["prep_time_minutes"].transform(
                "mean"
            )
            df["prep_time_minutes"] = df["prep_time_minutes"].fillna(category_avg_prep)
            transformations.append(
                f"Filled {null_prep} missing prep times with category averages"
            )

        # 7. Add metadata fields
        df["is_active"] = True
        df["created_at"] = datetime.now()
        df["updated_at"] = datetime.now()

        final_count = len(df)
        logger.info(
            f"   ✓ Menu items: {initial_count} → {final_count} ({initial_count - final_count} removed)"
        )

        self.transformation_report["transformations_applied"][
            "menu_items"
        ] = transformations

        return df

    # ========================================
    # ORDERS TRANSFORMATION
    # ========================================

    def transform_orders(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean orders data

        Transformations:
        - Fix missing timestamps
        - Remove duplicate order IDs
        - Fix negative amounts
        - Standardize order types
        - Fix invalid party sizes
        - Calculate missing durations
        """
        logger.info("📦 Transforming orders...")

        df = df.copy()
        initial_count = len(df)
        transformations = []

        # 1. Fix missing timestamps (remove records, can't infer)
        null_timestamps = df["order_timestamp"].isna().sum()
        if null_timestamps > 0:
            df = df[df["order_timestamp"].notna()]
            transformations.append(
                f"Removed {null_timestamps} orders with missing timestamps"
            )

        # 2. Convert timestamp to datetime
        df["order_timestamp"] = pd.to_datetime(df["order_timestamp"])
        transformations.append("Converted timestamps to datetime")

        # 3. Remove duplicate order IDs (keep first occurrence)
        duplicates = df.duplicated(subset=["order_id"], keep="first").sum()
        if duplicates > 0:
            df = df.drop_duplicates(subset=["order_id"], keep="first")
            transformations.append(f"Removed {duplicates} duplicate order IDs")

        # 4. Fix negative tip amounts (likely data entry error, use absolute value)
        negative_tips = (df["tip_amount"] < 0).sum()
        if negative_tips > 0:
            df["tip_amount"] = df["tip_amount"].abs()
            transformations.append(f"Fixed {negative_tips} negative tip amounts")

        # 5. Fix negative order totals (recalculate)
        negative_totals = (df["order_total"] < 0).sum()
        if negative_totals > 0:
            df["order_total"] = df["subtotal"] + df["tax_amount"] + df["tip_amount"]
            transformations.append(
                f"Recalculated {negative_totals} negative order totals"
            )

        # 6. Standardize order_type
        df["order_type"] = df["order_type"].str.strip().str.lower()
        df["order_type"] = (
            df["order_type"].map(self.order_type_mapping).fillna("dine_in")
        )
        transformations.append("Standardized order types")

        # 7. Fix invalid party sizes
        invalid_party = ((df["party_size"] <= 0) | (df["party_size"] > 20)).sum()
        if invalid_party > 0:
            # For party size 0 or negative, set to 1
            df.loc[df["party_size"] <= 0, "party_size"] = 1
            # For party size > 20, cap at 20 (or remove if extreme)
            df.loc[df["party_size"] > 20, "party_size"] = 20
            transformations.append(f"Fixed {invalid_party} invalid party sizes")

        # 8. Ensure duration is positive
        if "duration_minutes" in df.columns:
            negative_duration = (df["duration_minutes"] < 0).sum()
            if negative_duration > 0:
                df.loc[df["duration_minutes"] < 0, "duration_minutes"] = df[
                    "duration_minutes"
                ].median()
                transformations.append(f"Fixed {negative_duration} negative durations")

        # 9. Add created_at timestamp
        df["created_at"] = datetime.now()

        final_count = len(df)
        logger.info(
            f"   ✓ Orders: {initial_count} → {final_count} ({initial_count - final_count} removed)"
        )

        self.transformation_report["transformations_applied"][
            "orders"
        ] = transformations

        return df

    # ========================================
    # ORDER ITEMS TRANSFORMATION
    # ========================================

    def transform_order_items(
        self, df: pd.DataFrame, orders_df: pd.DataFrame, menu_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Clean order items and ensure referential integrity

        Transformations:
        - Remove items with invalid order_ids
        - Standardize item names (match menu)
        - Fix negative quantities/prices
        - Recalculate item totals
        """
        logger.info("📦 Transforming order items...")

        df = df.copy()
        initial_count = len(df)
        transformations = []

        # 1. Remove order items for orders that were removed
        valid_order_ids = set(orders_df["order_id"].unique())
        invalid_orders = ~df["order_id"].isin(valid_order_ids)
        invalid_count = invalid_orders.sum()
        if invalid_count > 0:
            df = df[~invalid_orders]
            transformations.append(
                f"Removed {invalid_count} items with invalid order_ids"
            )

        # 2. Standardize item names to match menu
        df["item_name"] = df["item_name"].str.strip().str.title()
        df["item_name_lower"] = df["item_name"].str.lower()
        df["item_name"] = (
            df["item_name_lower"].map(self.menu_item_mapping).fillna(df["item_name"])
        )
        df = df.drop("item_name_lower", axis=1)
        transformations.append("Standardized item names to match menu")

        # 3. Fix non-positive quantities
        invalid_qty = (df["quantity"] <= 0).sum()
        if invalid_qty > 0:
            df = df[df["quantity"] > 0]  # Remove invalid quantities
            transformations.append(
                f"Removed {invalid_qty} items with non-positive quantities"
            )

        # 4. Fix negative unit prices
        negative_prices = (df["unit_price"] < 0).sum()
        if negative_prices > 0:
            df["unit_price"] = df["unit_price"].abs()
            transformations.append(f"Fixed {negative_prices} negative unit prices")

        # 5. Recalculate item_total to ensure consistency
        df["item_total"] = df["quantity"] * df["unit_price"]
        df["item_total"] = df["item_total"].round(2)
        transformations.append("Recalculated item totals")

        # 6. Add created_at timestamp
        df["created_at"] = datetime.now()

        final_count = len(df)
        logger.info(
            f"   ✓ Order items: {initial_count} → {final_count} ({initial_count - final_count} removed)"
        )

        self.transformation_report["transformations_applied"][
            "order_items"
        ] = transformations

        return df

    # ========================================
    # WAIT TIMES TRANSFORMATION
    # ========================================

    def transform_wait_times(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean wait times data

        Transformations:
        - Convert timestamps
        - Fix negative wait times
        - Validate occupancy percentages
        - Calculate missing fields
        """
        logger.info("⏱️  Transforming wait times...")

        df = df.copy()
        initial_count = len(df)
        transformations = []

        # 1. Convert timestamps
        df["log_timestamp"] = pd.to_datetime(df["log_timestamp"])
        if "seated_timestamp" in df.columns:
            df["seated_timestamp"] = pd.to_datetime(df["seated_timestamp"])
        transformations.append("Converted timestamps to datetime")

        # 2. Fix negative quoted wait times
        negative_quoted = (df["quoted_wait_minutes"] < 0).sum()
        if negative_quoted > 0:
            df["quoted_wait_minutes"] = df["quoted_wait_minutes"].abs()
            transformations.append(
                f"Fixed {negative_quoted} negative quoted wait times"
            )

        # 3. Fix negative actual wait times
        if "actual_wait_minutes" in df.columns:
            negative_actual = (df["actual_wait_minutes"] < 0).sum()
            if negative_actual > 0:
                df["actual_wait_minutes"] = df["actual_wait_minutes"].abs()
                transformations.append(
                    f"Fixed {negative_actual} negative actual wait times"
                )

        # 4. Validate and fix occupancy percentages
        invalid_occ = (
            (df["current_table_occupancy_pct"] < 0)
            | (df["current_table_occupancy_pct"] > 100)
        ).sum()
        if invalid_occ > 0:
            df["current_table_occupancy_pct"] = df["current_table_occupancy_pct"].clip(
                0, 100
            )
            transformations.append(f"Fixed {invalid_occ} invalid occupancy percentages")

        # 5. Ensure day_of_week and hour_of_day are correct
        df["day_of_week"] = df["log_timestamp"].dt.dayofweek
        df["hour_of_day"] = df["log_timestamp"].dt.hour
        transformations.append(
            "Recalculated day_of_week and hour_of_day from timestamps"
        )

        # 6. Fix invalid party sizes
        invalid_party = ((df["party_size"] <= 0) | (df["party_size"] > 20)).sum()
        if invalid_party > 0:
            df.loc[df["party_size"] <= 0, "party_size"] = 2  # Default to 2
            df.loc[df["party_size"] > 20, "party_size"] = 20
            transformations.append(f"Fixed {invalid_party} invalid party sizes")

        # 7. Add created_at timestamp
        df["created_at"] = datetime.now()

        final_count = len(df)
        logger.info(
            f"   ✓ Wait times: {initial_count} → {final_count} ({initial_count - final_count} removed)"
        )

        self.transformation_report["transformations_applied"][
            "wait_times"
        ] = transformations

        return df

    # ========================================
    # EXTERNAL FACTORS TRANSFORMATION
    # ========================================

    def transform_external_factors(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean external factors data

        Transformations:
        - Ensure unique dates
        - Validate temperatures
        - Fix negative precipitation
        - Standardize weather conditions
        """
        logger.info("🌤️  Transforming external factors...")

        df = df.copy()
        initial_count = len(df)
        transformations = []

        # 1. Convert dates
        df["factor_date"] = pd.to_datetime(df["factor_date"])
        transformations.append("Converted dates to datetime")

        # 2. Remove duplicate dates (keep first)
        duplicates = df.duplicated(subset=["factor_date"], keep="first").sum()
        if duplicates > 0:
            df = df.drop_duplicates(subset=["factor_date"], keep="first")
            transformations.append(f"Removed {duplicates} duplicate dates")

        # 3. Validate temperatures (reasonable ranges for Tulsa)
        invalid_temp = (
            (df["temperature_high_f"] < -20) | (df["temperature_high_f"] > 120)
        ).sum()
        if invalid_temp > 0:
            # Replace with seasonal averages
            df.loc[
                (df["temperature_high_f"] < -20) | (df["temperature_high_f"] > 120),
                "temperature_high_f",
            ] = df["temperature_high_f"].median()
            transformations.append(f"Fixed {invalid_temp} unlikely temperatures")

        # 4. Fix negative precipitation
        negative_precip = (df["precipitation_inches"] < 0).sum()
        if negative_precip > 0:
            df["precipitation_inches"] = df["precipitation_inches"].abs()
            transformations.append(
                f"Fixed {negative_precip} negative precipitation values"
            )

        # 5. Standardize weather conditions
        df["weather_condition"] = df["weather_condition"].str.strip().str.lower()
        weather_mapping = {
            "rain": "rainy",
            "raining": "rainy",
            "snow": "snowy",
            "snowing": "snowy",
            "sun": "sunny",
            "clear": "sunny",
            "cloud": "cloudy",
            "clouds": "cloudy",
            "storm": "stormy",
            "storms": "stormy",
        }
        for key, value in weather_mapping.items():
            df.loc[
                df["weather_condition"].str.contains(key, na=False), "weather_condition"
            ] = value
        transformations.append("Standardized weather conditions")

        # 6. Ensure day_of_week is correct
        df["day_of_week"] = df["factor_date"].dt.dayofweek
        transformations.append("Recalculated day_of_week from dates")

        # 7. Add created_at and updated_at timestamps
        df["created_at"] = datetime.now()
        df["updated_at"] = datetime.now()

        final_count = len(df)
        logger.info(
            f"   ✓ External factors: {initial_count} → {final_count} ({initial_count - final_count} removed)"
        )

        self.transformation_report["transformations_applied"][
            "external_factors"
        ] = transformations

        return df

    # ========================================
    # REPORTING
    # ========================================

    def _calculate_transformation_summary(self, raw_data: Dict, cleaned_data: Dict):
        """Calculate summary statistics"""
        total_raw = sum(len(df) for df in raw_data.values())
        total_cleaned = sum(len(df) for df in cleaned_data.values())

        self.transformation_report["records_cleaned"] = total_raw
        self.transformation_report["records_removed"] = total_raw - total_cleaned
        self.transformation_report["records_final"] = total_cleaned

    def _log_transformation_summary(self):
        """Log summary of transformation process"""
        logger.info("\n" + "=" * 60)
        logger.info("🔧 TRANSFORMATION SUMMARY")
        logger.info("=" * 60)

        for dataset, transforms in self.transformation_report[
            "transformations_applied"
        ].items():
            logger.info(f"\n{dataset.upper()}:")
            for transform in transforms:
                logger.info(f"   ✓ {transform}")

        logger.info(f"\n📊 Records Summary:")
        logger.info(f"   Initial: {self.transformation_report['records_cleaned']:,}")
        logger.info(f"   Removed: {self.transformation_report['records_removed']:,}")
        logger.info(f"   Final: {self.transformation_report['records_final']:,}")
        logger.info(
            f"   Retention Rate: {(self.transformation_report['records_final'] / self.transformation_report['records_cleaned'] * 100):.1f}%"
        )

        logger.info("=" * 60 + "\n")

    def _save_transformation_report(self):
        """Save transformation report to JSON"""
        report_path = Path("data") / "transformation_report.json"

        with open(report_path, "w") as f:
            json.dump(self.transformation_report, f, indent=2, default=str)

        logger.info(f"📄 Transformation report saved to: {report_path}")


# ========================================
# MAIN EXECUTION
# ========================================


def main():
    """Main transformation function"""
    try:
        # Import extraction to get raw data
        from etl.extract import DataExtractor

        # Extract raw data
        logger.info("📥 Extracting raw data first...")
        extractor = DataExtractor(data_dir="data")
        raw_data = extractor.extract_all()

        # Transform data
        transformer = DataTransformer()
        cleaned_data = transformer.transform_all(raw_data)

        logger.info("✅ Transformation phase complete!")
        logger.info("📦 Data ready for loading into database")

        return cleaned_data

    except Exception as e:
        logger.error(f"❌ Transformation failed: {str(e)}")
        raise


if __name__ == "__main__":
    cleaned_data = main()
