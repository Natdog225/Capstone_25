"""
Dinemetra ETL - Transform Phase
Cleans and normalizes raw POS data for database loading
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
            "takeout": "takeout",
            "take out": "takeout",
            "delivery": "delivery",
        }

        # Menu item deduplication mapping
        self.menu_item_mapping = {
            "buffalo wings": "Wings",
            "wings": "Wings",
            "fries": "French Fries",
            "french fries": "French Fries",
        }

    def transform_all(
        self, raw_data: Dict[str, pd.DataFrame]
    ) -> Dict[str, pd.DataFrame]:
        logger.info("🔧 Starting data transformation process...")
        cleaned_data = {}

        # Transform each dataset
        if "menu_items" in raw_data:
            cleaned_data["menu_items"] = self.transform_menu_items(
                raw_data["menu_items"]
            )

        if "orders" in raw_data:
            cleaned_data["orders"] = self.transform_orders(raw_data["orders"])

        if "order_items" in raw_data and "menu_items" in cleaned_data:
            cleaned_data["order_items"] = self.transform_order_items(
                raw_data["order_items"],
                cleaned_data["orders"],
                cleaned_data["menu_items"],
            )

        # Create wait_times from orders if strictly missing
        if "wait_times" not in raw_data or raw_data["wait_times"].empty:
            if "orders" in cleaned_data:
                logger.info("⚠️ No wait times found. Generating from Orders...")
                cleaned_data["wait_times"] = self.transform_wait_times(
                    cleaned_data["orders"].copy()
                )
        else:
            cleaned_data["wait_times"] = self.transform_wait_times(
                raw_data["wait_times"]
            )

        if "external_factors" in raw_data:
            cleaned_data["external_factors"] = self.transform_external_factors(
                raw_data["external_factors"]
            )

        self._calculate_transformation_summary(raw_data, cleaned_data)
        self._log_transformation_summary()
        self._save_transformation_report()

        return cleaned_data

    def transform_menu_items(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        if "name" in df.columns and "item_name" not in df.columns:
            df = df.rename(columns={"name": "item_name"})

        initial_count = len(df)
        transformations = []
        df["item_name"] = df["item_name"].astype(str).str.strip().str.title()
        df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(10.0)
        df["category"] = df["category"].fillna("Food")
        return df

    def transform_orders(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["order_timestamp"] = pd.to_datetime(df["order_timestamp"])
        df["party_size"] = (
            pd.to_numeric(df["party_size"], errors="coerce").fillna(2).astype(int)
        )
        df["order_total"] = pd.to_numeric(df["order_total"], errors="coerce").fillna(0)
        return df

    def transform_order_items(
        self, df: pd.DataFrame, orders_df: pd.DataFrame, menu_df: pd.DataFrame
    ) -> pd.DataFrame:
        df = df.copy()
        # Ensure order_id matches
        valid_ids = set(orders_df["order_id"])
        df = df[df["order_id"].isin(valid_ids)]
        return df

    def transform_wait_times(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        # Map columns if coming from orders
        if "order_timestamp" in df.columns:
            df["log_timestamp"] = df["order_timestamp"]
            df["actual_wait_minutes"] = np.random.randint(
                5, 45, size=len(df)
            )  # Mock wait times for now
            df["quoted_wait_minutes"] = df["actual_wait_minutes"] + np.random.randint(
                -5, 5, size=len(df)
            )
            df["current_table_occupancy_pct"] = np.random.randint(20, 100, size=len(df))

        df["log_timestamp"] = pd.to_datetime(df["log_timestamp"])
        df["hour_of_day"] = df["log_timestamp"].dt.hour
        df["day_of_week"] = df["log_timestamp"].dt.dayofweek
        return df

    def transform_external_factors(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["factor_date"] = pd.to_datetime(df["factor_date"])
        return df

    def _calculate_transformation_summary(self, raw_data, cleaned_data):
        self.transformation_report["records_final"] = sum(
            len(df) for df in cleaned_data.values()
        )

    def _log_transformation_summary(self):
        logger.info(
            f"✅ Transformation Complete. Records: {self.transformation_report['records_final']}"
        )

    def _save_transformation_report(self):
        with open("data/transformation_report.json", "w") as f:
            json.dump(self.transformation_report, f, default=str)


# ========================================
# MAIN EXECUTION
# ========================================


def main():
    """Main transformation function"""
    try:
        # Import extraction
        from etl.extract_real_data import RealDataExtractor

        # 1. Run Extraction (Ensures CSVs exist)
        logger.info("📥 Running Extraction Phase...")
        extractor = RealDataExtractor(data_dir="data/real")
        extractor.run()

        # 2. Load CSVs from Disk
        logger.info("📥 Loading extracted CSVs for transformation...")
        processed_dir = Path("data/processed")

        raw_data = {}

        if (processed_dir / "orders_from_real_data.csv").exists():
            raw_data["orders"] = pd.read_csv(
                processed_dir / "orders_from_real_data.csv"
            )
            # Use orders as wait times base if real wait times don't exist
            raw_data["wait_times"] = raw_data["orders"].copy()

        if (processed_dir / "order_items_from_real_data.csv").exists():
            raw_data["order_items"] = pd.read_csv(
                processed_dir / "order_items_from_real_data.csv"
            )

        if (Path("data/menu_items_reference.csv")).exists():
            raw_data["menu_items"] = pd.read_csv("data/menu_items_reference.csv")

        # 3. Transform
        transformer = DataTransformer()
        cleaned_data = transformer.transform_all(raw_data)

        # 4. Save Final Cleaned Files (Ready for Training)
        # We overwrite the processed files with the CLEAN versions
        if "orders" in cleaned_data:
            cleaned_data["orders"].to_csv(
                processed_dir / "orders_from_real_data.csv", index=False
            )
        if "wait_times" in cleaned_data:
            cleaned_data["wait_times"].to_csv(
                processed_dir / "wait_times_from_real_data.csv", index=False
            )

        logger.info("📦 Data ready for Model Training")
        return cleaned_data

    except Exception as e:
        logger.error(f"❌ Transformation failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
