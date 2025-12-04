"""
Dinemetra ETL - Extract Phase
Reads raw POS data files and performs initial validation

This script:
1. Loads CSV files from data/ directory
2. Performs basic validation
3. Logs data quality issues
4. Returns raw DataFrames for transformation phase

Run: python -m etl.extract
"""

import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import logging
import json
from typing import Dict, Tuple

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DataExtractor:
    """
    Handles extraction of raw POS data from CSV files
    """

    def __init__(self, data_dir: str = "data"):
        """
        Initialize extractor with data directory path

        Args:
            data_dir: Path to directory containing raw CSV files
        """
        self.data_dir = Path(data_dir)
        self.extraction_report = {
            "timestamp": datetime.now().isoformat(),
            "files_processed": {},
            "total_records": 0,
            "issues_found": [],
        }

    def extract_all(self) -> Dict[str, pd.DataFrame]:
        """
        Extract all data files

        Returns:
            Dictionary of DataFrames: {
                'orders': DataFrame,
                'order_items': DataFrame,
                'wait_times': DataFrame,
                'external_factors': DataFrame,
                'menu_items': DataFrame
            }
        """
        logger.info("🚀 Starting data extraction process...")

        data = {}

        # Extract each file
        data["orders"] = self.extract_orders()
        data["order_items"] = self.extract_order_items()
        data["wait_times"] = self.extract_wait_times()
        data["external_factors"] = self.extract_external_factors()
        data["menu_items"] = self.extract_menu_items()

        # Calculate totals
        self.extraction_report["total_records"] = sum(len(df) for df in data.values())

        # Log summary
        self._log_extraction_summary()

        # Save extraction report
        self._save_extraction_report()

        return data

    def extract_orders(self) -> pd.DataFrame:
        """Extract orders data"""
        logger.info("� Extracting orders data...")

        file_path = self.data_dir / "orders_raw.csv"

        if not file_path.exists():
            raise FileNotFoundError(f"Orders file not found: {file_path}")

        # Read CSV
        df = pd.read_csv(file_path)

        # Log file info
        self.extraction_report["files_processed"]["orders"] = {
            "file": str(file_path),
            "rows": len(df),
            "columns": list(df.columns),
            "size_mb": file_path.stat().st_size / (1024 * 1024),
        }

        # Validate expected columns
        expected_columns = [
            "order_id",
            "order_timestamp",
            "party_size",
            "order_total",
            "subtotal",
            "tax_amount",
            "tip_amount",
            "order_type",
            "table_number",
            "server_id",
            "order_status",
            "duration_minutes",
        ]

        missing_columns = set(expected_columns) - set(df.columns)
        if missing_columns:
            issue = f"Orders: Missing columns: {missing_columns}"
            logger.warning(f"⚠️  {issue}")
            self.extraction_report["issues_found"].append(issue)

        # Data quality checks
        self._check_orders_quality(df)

        logger.info(f"   ✓ Extracted {len(df)} orders")
        return df

    def extract_order_items(self) -> pd.DataFrame:
        """Extract order items data"""
        logger.info("📦 Extracting order items data...")

        file_path = self.data_dir / "order_items_raw.csv"

        if not file_path.exists():
            raise FileNotFoundError(f"Order items file not found: {file_path}")

        df = pd.read_csv(file_path)

        self.extraction_report["files_processed"]["order_items"] = {
            "file": str(file_path),
            "rows": len(df),
            "columns": list(df.columns),
            "size_mb": file_path.stat().st_size / (1024 * 1024),
        }

        # Validate expected columns
        expected_columns = [
            "order_item_id",
            "order_id",
            "item_name",
            "quantity",
            "unit_price",
            "item_total",
            "special_instructions",
        ]

        missing_columns = set(expected_columns) - set(df.columns)
        if missing_columns:
            issue = f"Order Items: Missing columns: {missing_columns}"
            logger.warning(f"⚠️  {issue}")
            self.extraction_report["issues_found"].append(issue)

        # Data quality checks
        self._check_order_items_quality(df)

        logger.info(f"   ✓ Extracted {len(df)} order items")
        return df

    def extract_wait_times(self) -> pd.DataFrame:
        """Extract wait times data"""
        logger.info("⏱️  Extracting wait times data...")

        file_path = self.data_dir / "wait_times_raw.csv"

        if not file_path.exists():
            raise FileNotFoundError(f"Wait times file not found: {file_path}")

        df = pd.read_csv(file_path)

        self.extraction_report["files_processed"]["wait_times"] = {
            "file": str(file_path),
            "rows": len(df),
            "columns": list(df.columns),
            "size_mb": file_path.stat().st_size / (1024 * 1024),
        }

        # Validate expected columns
        expected_columns = [
            "wait_time_id",
            "log_timestamp",
            "party_size",
            "quoted_wait_minutes",
            "actual_wait_minutes",
            "seated_timestamp",
            "day_of_week",
            "hour_of_day",
            "current_party_count",
            "current_table_occupancy_pct",
            "wait_type",
        ]

        missing_columns = set(expected_columns) - set(df.columns)
        if missing_columns:
            issue = f"Wait Times: Missing columns: {missing_columns}"
            logger.warning(f"⚠️  {issue}")
            self.extraction_report["issues_found"].append(issue)

        # Data quality checks
        self._check_wait_times_quality(df)

        logger.info(f"   ✓ Extracted {len(df)} wait time records")
        return df

    def extract_external_factors(self) -> pd.DataFrame:
        """Extract external factors data"""
        logger.info("🌤️  Extracting external factors data...")

        # Try to load file with events first
        file_path_with_events = self.data_dir / "external_factors_with_events.csv"
        file_path = self.data_dir / "external_factors_raw.csv"
    
        if file_path_with_events.exists():
            file_path = file_path_with_events
            logger.info("   Using external factors WITH event data")
    
        df = pd.read_csv(file_path)

        file_path = self.data_dir / "external_factors_raw.csv"

        if not file_path.exists():
            raise FileNotFoundError(f"External factors file not found: {file_path}")

        df = pd.read_csv(file_path)

        self.extraction_report["files_processed"]["external_factors"] = {
            "file": str(file_path),
            "rows": len(df),
            "columns": list(df.columns),
            "size_mb": file_path.stat().st_size / (1024 * 1024),
        }

        # Validate expected columns
        expected_columns = [
            "factor_date",
            "day_of_week",
            "is_holiday",
            "holiday_name",
            "weather_condition",
            "temperature_high_f",
            "temperature_low_f",
            "precipitation_inches",
            "local_event_name",
            "local_event_type",
            "event_attendance_estimated",
            "event_distance_miles",
        ]

        missing_columns = set(expected_columns) - set(df.columns)
        if missing_columns:
            issue = f"External Factors: Missing columns: {missing_columns}"
            logger.warning(f"⚠️  {issue}")
            self.extraction_report["issues_found"].append(issue)

        # Data quality checks
        self._check_external_factors_quality(df)

        logger.info(f"   ✓ Extracted {len(df)} external factor records")
        return df

    def extract_menu_items(self) -> pd.DataFrame:
        """Extract menu items reference data"""
        logger.info("🍔 Extracting menu items data...")

        file_path = self.data_dir / "menu_items_reference.csv"

        if not file_path.exists():
            raise FileNotFoundError(f"Menu items file not found: {file_path}")

        df = pd.read_csv(file_path)

        self.extraction_report["files_processed"]["menu_items"] = {
            "file": str(file_path),
            "rows": len(df),
            "columns": list(df.columns),
            "size_mb": file_path.stat().st_size / (1024 * 1024),
        }

        # Validate expected columns
        expected_columns = ["item_name", "price", "category", "prep_time_minutes"]

        missing_columns = set(expected_columns) - set(df.columns)
        if missing_columns:
            issue = f"Menu Items: Missing columns: {missing_columns}"
            logger.warning(f"⚠️  {issue}")
            self.extraction_report["issues_found"].append(issue)

        # Data quality checks
        self._check_menu_items_quality(df)

        logger.info(f"   ✓ Extracted {len(df)} menu items")
        return df

    # ========================================
    # DATA QUALITY CHECKS
    # ========================================

    def _check_orders_quality(self, df: pd.DataFrame):
        """Perform data quality checks on orders"""
        issues = []

        # Missing timestamps
        null_timestamps = df["order_timestamp"].isna().sum()
        if null_timestamps > 0:
            issues.append(f"Missing timestamps: {null_timestamps}")

        # Negative amounts
        if "tip_amount" in df.columns:
            negative_tips = (df["tip_amount"] < 0).sum()
            if negative_tips > 0:
                issues.append(f"Negative tip amounts: {negative_tips}")

        if "order_total" in df.columns:
            negative_totals = (df["order_total"] < 0).sum()
            if negative_totals > 0:
                issues.append(f"Negative order totals: {negative_totals}")

        # Duplicate order IDs
        duplicates = df["order_id"].duplicated().sum()
        if duplicates > 0:
            issues.append(f"Duplicate order IDs: {duplicates}")

        # Invalid party sizes
        if "party_size" in df.columns:
            invalid_party = ((df["party_size"] <= 0) | (df["party_size"] > 20)).sum()
            if invalid_party > 0:
                issues.append(f"Invalid party sizes: {invalid_party}")

        # Inconsistent order_type formatting
        if "order_type" in df.columns:
            unique_types = df["order_type"].unique()
            if len(unique_types) > 3:  # Should only be dine_in, takeout, delivery
                issues.append(f"Inconsistent order_type values: {list(unique_types)}")

        if issues:
            logger.warning(f"   ⚠️  Orders data quality issues:")
            for issue in issues:
                logger.warning(f"      - {issue}")
                self.extraction_report["issues_found"].append(f"Orders: {issue}")

    def _check_order_items_quality(self, df: pd.DataFrame):
        """Perform data quality checks on order items"""
        issues = []

        # Negative quantities
        if "quantity" in df.columns:
            negative_qty = (df["quantity"] <= 0).sum()
            if negative_qty > 0:
                issues.append(f"Non-positive quantities: {negative_qty}")

        # Negative prices
        if "unit_price" in df.columns:
            negative_price = (df["unit_price"] < 0).sum()
            if negative_price > 0:
                issues.append(f"Negative unit prices: {negative_price}")

        # Missing item names
        if "item_name" in df.columns:
            null_names = df["item_name"].isna().sum()
            if null_names > 0:
                issues.append(f"Missing item names: {null_names}")

        # Check for potential duplicates in item names (case-insensitive)
        if "item_name" in df.columns:
            unique_items = df["item_name"].str.lower().unique()
            similar_items = []

            # Look for items that might be duplicates
            for item in unique_items:
                if pd.notna(item):
                    # Check for variations (wings vs buffalo wings, fries vs french fries)
                    if "wing" in item or "fri" in item or "mozz" in item:
                        similar_items.append(item)

            if len(similar_items) > 1:
                issues.append(
                    f"Potential duplicate items detected: {len(similar_items)} variations"
                )

        if issues:
            logger.warning(f"   ⚠️  Order items data quality issues:")
            for issue in issues:
                logger.warning(f"      - {issue}")
                self.extraction_report["issues_found"].append(f"Order Items: {issue}")

    def _check_wait_times_quality(self, df: pd.DataFrame):
        """Perform data quality checks on wait times"""
        issues = []

        # Negative wait times
        if "quoted_wait_minutes" in df.columns:
            negative_quoted = (df["quoted_wait_minutes"] < 0).sum()
            if negative_quoted > 0:
                issues.append(f"Negative quoted wait times: {negative_quoted}")

        if "actual_wait_minutes" in df.columns:
            negative_actual = (df["actual_wait_minutes"] < 0).sum()
            if negative_actual > 0:
                issues.append(f"Negative actual wait times: {negative_actual}")

        # Missing actual wait times (people left before being seated)
        if "actual_wait_minutes" in df.columns:
            null_actual = df["actual_wait_minutes"].isna().sum()
            if null_actual > 0:
                issues.append(f"Missing actual wait times: {null_actual}")

        # Invalid occupancy percentages
        if "current_table_occupancy_pct" in df.columns:
            invalid_occ = (
                (df["current_table_occupancy_pct"] < 0)
                | (df["current_table_occupancy_pct"] > 100)
            ).sum()
            if invalid_occ > 0:
                issues.append(f"Invalid occupancy percentages: {invalid_occ}")

        if issues:
            logger.warning(f"   ⚠️  Wait times data quality issues:")
            for issue in issues:
                logger.warning(f"      - {issue}")
                self.extraction_report["issues_found"].append(f"Wait Times: {issue}")

    def _check_external_factors_quality(self, df: pd.DataFrame):
        """Perform data quality checks on external factors"""
        issues = []

        # Invalid temperatures
        if "temperature_high_f" in df.columns:
            invalid_temp = (
                (df["temperature_high_f"] < -50) | (df["temperature_high_f"] > 130)
            ).sum()
            if invalid_temp > 0:
                issues.append(f"Unlikely temperatures: {invalid_temp}")

        # Negative precipitation
        if "precipitation_inches" in df.columns:
            negative_precip = (df["precipitation_inches"] < 0).sum()
            if negative_precip > 0:
                issues.append(f"Negative precipitation: {negative_precip}")

        # Missing dates
        null_dates = df["factor_date"].isna().sum()
        if null_dates > 0:
            issues.append(f"Missing dates: {null_dates}")

        # Duplicate dates
        duplicates = df["factor_date"].duplicated().sum()
        if duplicates > 0:
            issues.append(f"Duplicate dates: {duplicates}")

        if issues:
            logger.warning(f"   ⚠️  External factors data quality issues:")
            for issue in issues:
                logger.warning(f"      - {issue}")
                self.extraction_report["issues_found"].append(
                    f"External Factors: {issue}"
                )

    def _check_menu_items_quality(self, df: pd.DataFrame):
        """Perform data quality checks on menu items"""
        issues = []

        # Negative prices
        if "price" in df.columns:
            negative_price = (df["price"] <= 0).sum()
            if negative_price > 0:
                issues.append(f"Non-positive prices: {negative_price}")

        # Missing item names
        null_names = df["item_name"].isna().sum()
        if null_names > 0:
            issues.append(f"Missing item names: {null_names}")

        # Duplicate item names (case-insensitive)
        if "item_name" in df.columns:
            lowercase_names = df["item_name"].str.lower()
            duplicates = lowercase_names.duplicated().sum()
            if duplicates > 0:
                issues.append(f"Duplicate item names (case-insensitive): {duplicates}")
                # Log the actual duplicates
                dupe_items = df[lowercase_names.duplicated(keep=False)][
                    "item_name"
                ].unique()
                logger.warning(f"      Duplicate items: {list(dupe_items)}")

        if issues:
            logger.warning(f"   ⚠️  Menu items data quality issues:")
            for issue in issues:
                logger.warning(f"      - {issue}")
                self.extraction_report["issues_found"].append(f"Menu Items: {issue}")

    # ========================================
    # REPORTING
    # ========================================

    def _log_extraction_summary(self):
        """Log summary of extraction process"""
        logger.info("\n" + "=" * 60)
        logger.info("📊 EXTRACTION SUMMARY")
        logger.info("=" * 60)

        for file_type, info in self.extraction_report["files_processed"].items():
            logger.info(f"\n{file_type.upper()}:")
            logger.info(f"   Rows: {info['rows']:,}")
            logger.info(f"   Columns: {len(info['columns'])}")
            logger.info(f"   Size: {info['size_mb']:.2f} MB")

        logger.info(
            f"\n📈 Total Records Extracted: {self.extraction_report['total_records']:,}"
        )

        if self.extraction_report["issues_found"]:
            logger.info(
                f"\n⚠️  Total Issues Found: {len(self.extraction_report['issues_found'])}"
            )
        else:
            logger.info("\n✅ No data quality issues detected!")

        logger.info("=" * 60 + "\n")

    def _save_extraction_report(self):
        """Save extraction report to JSON"""
        report_path = self.data_dir / "extraction_report.json"

        with open(report_path, "w") as f:
            json.dump(self.extraction_report, f, indent=2)

        logger.info(f"📄 Extraction report saved to: {report_path}")


# ========================================
# MAIN EXECUTION
# ========================================


def main():
    """Main extraction function"""
    try:
        # Initialize extractor
        extractor = DataExtractor(data_dir="data")

        # Extract all data
        data = extractor.extract_all()

        logger.info("✅ Extraction phase complete!")
        logger.info("📦 Data ready for transformation phase")

        return data

    except Exception as e:
        logger.error(f"❌ Extraction failed: {str(e)}")
        raise


if __name__ == "__main__":
    extracted_data = main()
