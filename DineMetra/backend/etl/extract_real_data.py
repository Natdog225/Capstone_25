"""
Dinemetra Real Restaurant Data Extractor
Extracts actual POS data from restaurant CSV files

This script:
1. Reads real CSV files from data/real/
2. Transforms summary data into detailed records
3. Generates realistic order-level data based on patterns
4. Outputs in our standard schema format

Run: python scripts/process_real_data.py
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta, time
from pathlib import Path
import logging
import random
import re

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RealDataExtractor:
    """
    Extracts and processes real restaurant data
    """

    def __init__(self, data_dir: str = "data/real"):
        """
        Initialize extractor

        Args:
            data_dir: Directory containing real CSV files
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Store parsed data
        self.daily_sales = None
        self.hourly_pattern = None
        self.day_of_week_pattern = None
        self.service_periods = None

    def load_all_data(self):
        """Load all available CSV files"""
        logger.info("📥 Loading real restaurant data...")

        # Look for CSV files in the directory
        csv_files = list(self.data_dir.glob("*.csv"))

        if not csv_files:
            logger.warning(f"No CSV files found in {self.data_dir}")
            return

        logger.info(f"Found {len(csv_files)} CSV files")

        for csv_file in csv_files:
            logger.info(f"   - {csv_file.name}")
            self._process_csv_file(csv_file)

    # Add this to RealDataExtractor class


    # Add this to RealDataExtractor class

    def load_all_data_by_month(self):
        """Load data from multiple monthly folders"""
        logger.info("📥 Loading real restaurant data from monthly folders...")
        
        # Find all month directories (format: YYYY-MM)
        month_dirs = []
        for d in self.data_dir.iterdir():
            if d.is_dir() and re.match(r'^\d{4}-\d{2}$', d.name):
                month_dirs.append(d)
        
        month_dirs = sorted(month_dirs)
        
        if not month_dirs:
            logger.warning(f"No monthly folders found in {self.data_dir}")
            logger.info("Expected format: data/real/2025-01/, data/real/2025-02/, etc.")
            logger.info("\nFalling back to loading files directly from data/real/...")
            # Fall back to old method
            self.load_all_data()
            return
        
        logger.info(f"Found {len(month_dirs)} monthly folders")
        
        # Storage for combined data
        all_daily_sales = []
        all_hourly_patterns = []
        all_day_of_week = []
        
        for month_dir in month_dirs:
            logger.info(f"\n📅 Processing {month_dir.name}...")
            
            # Temporarily change data_dir to process this month
            original_data_dir = self.data_dir
            self.data_dir = month_dir
            
            csv_files = list(month_dir.glob("*.csv"))
            logger.info(f"   Found {len(csv_files)} CSV files")
            
            # Reset these for each month
            self.daily_sales = None
            self.hourly_pattern = None
            self.day_of_week_pattern = None
            
            for csv_file in csv_files:
                self._process_csv_file(csv_file)
            
            # Collect data from this month
            if self.daily_sales is not None:
                self.daily_sales['month'] = month_dir.name
                all_daily_sales.append(self.daily_sales.copy())
            
            if self.hourly_pattern is not None:
                self.hourly_pattern['month'] = month_dir.name
                all_hourly_patterns.append(self.hourly_pattern.copy())
            
            if self.day_of_week_pattern is not None:
                self.day_of_week_pattern['month'] = month_dir.name
                all_day_of_week.append(self.day_of_week_pattern.copy())
            
            # Restore original data_dir
            self.data_dir = original_data_dir
        
        # Combine all months
        if all_daily_sales:
            self.daily_sales = pd.concat(all_daily_sales, ignore_index=True)
            logger.info(f"\n✓ Combined daily sales: {len(self.daily_sales)} days total")
        
        if all_hourly_patterns:
            # Average hourly patterns across all months
            combined = pd.concat(all_hourly_patterns)
            self.hourly_pattern = combined.groupby('hour').agg({
                'order_count': 'sum',
                'revenue': 'sum',
                'guest_count': 'sum'
            }).reset_index()
            logger.info(f"✓ Combined hourly pattern from {len(all_hourly_patterns)} months")
        
        if all_day_of_week:
            # Average day-of-week patterns across all months
            combined = pd.concat(all_day_of_week)
            self.day_of_week_pattern = combined.groupby('day_of_week').agg({
                'order_count': 'sum',
                'revenue': 'sum',
                'guest_count': 'sum'
            }).reset_index()
            logger.info(f"✓ Combined day-of-week pattern from {len(all_day_of_week)} months")

    def _process_csv_file(self, file_path: Path):
        """
        Process a single CSV file
        Auto-detects format based on columns
        """
        try:
            # Read CSV
            df = pd.read_csv(file_path)

            # Detect data type based on columns
            columns = [col.lower().strip() for col in df.columns]

            if "yyyymmdd" in columns or ("net sales" in columns and len(df) > 20):
                # Daily sales data
                self.daily_sales = self._parse_daily_sales(df)
                logger.info(f"   ✓ Loaded daily sales ({len(self.daily_sales)} days)")

            elif "hour of day" in columns:
                # Hourly pattern
                self.hourly_pattern = self._parse_hourly_pattern(df)
                logger.info(
                    f"   ✓ Loaded hourly pattern ({len(self.hourly_pattern)} hours)"
                )

            elif "day of week" in columns and len(df) == 7:
                # Day of week pattern
                self.day_of_week_pattern = self._parse_day_of_week(df)
                logger.info(f"   ✓ Loaded day-of-week pattern")

            elif "service" in columns or "day part" in columns:
                # Service periods
                self.service_periods = self._parse_service_periods(df)
                logger.info(f"   ✓ Loaded service periods")

            else:
                logger.info(f"   ⚠️  Unknown format: {columns}")

        except Exception as e:
            logger.error(f"Error processing {file_path.name}: {e}")

    def _parse_daily_sales(self, df: pd.DataFrame) -> pd.DataFrame:
        """Parse daily sales data"""
        # Standardize column names
        df.columns = [col.lower().strip() for col in df.columns]

        # Convert date column
        if "yyyymmdd" in df.columns:
            df["date"] = pd.to_datetime(df["yyyymmdd"], format="%Y%m%d")

        # Rename columns to our standard
        column_map = {
            "net sales": "revenue",
            "total orders": "order_count",
            "total guests": "guest_count",
        }
        df = df.rename(columns=column_map)

        return df

    def _parse_hourly_pattern(self, df: pd.DataFrame) -> pd.DataFrame:
        """Parse hourly sales pattern"""
        df.columns = [col.lower().strip() for col in df.columns]

        column_map = {
            "hour of day": "hour",
            "net sales": "revenue",
            "total orders": "order_count",
            "total guests": "guest_count",
        }
        df = df.rename(columns=column_map)

        # Ensure hour is integer
        df["hour"] = df["hour"].astype(int)

        # Sort by hour
        df = df.sort_values("hour")

        return df

    def _parse_day_of_week(self, df: pd.DataFrame) -> pd.DataFrame:
        """Parse day of week pattern"""
        df.columns = [col.lower().strip() for col in df.columns]

        # Map day names to numbers
        day_map = {
            "mon": 0,
            "monday": 0,
            "tue": 1,
            "tuesday": 1,
            "wed": 2,
            "wednesday": 2,
            "thu": 3,
            "thursday": 3,
            "fri": 4,
            "friday": 4,
            "sat": 5,
            "saturday": 5,
            "sun": 6,
            "sunday": 6,
        }

        df["day_of_week"] = df["day of week"].str.lower().str.strip().map(day_map)

        column_map = {
            "net sales": "revenue",
            "total orders": "order_count",
            "total guests": "guest_count",
        }
        df = df.rename(columns=column_map)

        return df

    def _parse_service_periods(self, df: pd.DataFrame) -> pd.DataFrame:
        """Parse service period data"""
        df.columns = [col.lower().strip() for col in df.columns]

        # Clean service names
        if "service / day part" in df.columns:
            df["service_period"] = df["service / day part"].str.strip().str.lower()

        return df

    def generate_detailed_orders(self) -> pd.DataFrame:
        """
        Generate detailed order records from summary data
        Uses statistical patterns to create realistic individual orders

        Returns:
            DataFrame with individual order records
        """
        logger.info("🔄 Generating detailed order records...")

        if self.daily_sales is None:
            logger.error("No daily sales data loaded")
            return pd.DataFrame()

        orders = []
        order_id = 1000

        for _, day_row in self.daily_sales.iterrows():
            date = day_row["date"]
            daily_orders = int(day_row["order_count"])
            daily_revenue = day_row["revenue"]

            # Get day of week
            day_of_week = date.dayofweek

            # Distribute orders across hours using hourly pattern
            hourly_distribution = self._get_hourly_distribution(day_of_week)

            for hour, hour_pct in hourly_distribution.items():
                # Number of orders this hour
                orders_this_hour = int(daily_orders * hour_pct)

                if orders_this_hour == 0:
                    continue

                # Generate orders for this hour
                for _ in range(orders_this_hour):
                    # Random minute within hour
                    minute = random.randint(0, 59)
                    second = random.randint(0, 59)

                    order_timestamp = datetime.combine(
                        date.date(), time(hour, minute, second)
                    )

                    # Generate realistic order details
                    party_size = self._generate_party_size()
                    order_total = self._generate_order_total(
                        party_size, daily_revenue / daily_orders
                    )

                    # Determine order type
                    order_type = self._determine_order_type(hour)

                    # Calculate components
                    subtotal = order_total / 1.0895  # Remove 8.95% tax
                    tax_amount = order_total - subtotal
                    tip_amount = (
                        subtotal * random.uniform(0.15, 0.22)
                        if order_type == "dine_in"
                        else 0
                    )

                    # Duration (prep time)
                    duration_minutes = int(
                        random.gauss(45, 15)
                    )  # Average 45 min, std 15 min
                    duration_minutes = max(20, min(90, duration_minutes))

                    orders.append(
                        {
                            "order_id": order_id,
                            "order_timestamp": order_timestamp,
                            "party_size": party_size,
                            "order_total": round(order_total + tip_amount, 2),
                            "subtotal": round(subtotal, 2),
                            "tax_amount": round(tax_amount, 2),
                            "tip_amount": round(tip_amount, 2),
                            "order_type": order_type,
                            "table_number": (
                                f"T{random.randint(1, 30)}"
                                if order_type == "dine_in"
                                else None
                            ),
                            "server_id": (
                                random.randint(100, 110)
                                if order_type == "dine_in"
                                else None
                            ),
                            "order_status": "completed",
                            "duration_minutes": duration_minutes,
                        }
                    )

                    order_id += 1

        orders_df = pd.DataFrame(orders)
        logger.info(f"   ✓ Generated {len(orders_df)} individual orders")

        return orders_df

    def _get_hourly_distribution(self, day_of_week: int) -> dict:
        """
        Get hourly distribution of orders

        Args:
            day_of_week: 0=Monday, 6=Sunday

        Returns:
            Dictionary of {hour: percentage}
        """
        if self.hourly_pattern is not None:
            # Use actual hourly pattern
            total_orders = self.hourly_pattern["order_count"].sum()
            distribution = {}

            for _, row in self.hourly_pattern.iterrows():
                hour = int(row["hour"])
                pct = row["order_count"] / total_orders
                distribution[hour] = pct

            return distribution
        else:
            # Default pattern if no hourly data
            # Lunch: 11am-2pm, Dinner: 5pm-9pm
            return {
                10: 0.02,
                11: 0.15,
                12: 0.20,
                13: 0.12,
                14: 0.08,
                15: 0.04,
                16: 0.05,
                17: 0.10,
                18: 0.13,
                19: 0.08,
                20: 0.02,
                21: 0.01,
            }

    def _generate_party_size(self) -> int:
        """Generate realistic party size"""
        # Distribution based on typical restaurant patterns
        return np.random.choice(
            [1, 2, 3, 4, 5, 6, 7, 8], p=[0.12, 0.38, 0.18, 0.20, 0.06, 0.03, 0.02, 0.01]
        )

    def _generate_order_total(self, party_size: int, avg_check: float) -> float:
        """
        Generate realistic order total

        Args:
            party_size: Number of people
            avg_check: Average check size from real data

        Returns:
            Order total in dollars
        """
        # Base on party size with some variance
        per_person = avg_check * random.uniform(0.8, 1.2)
        total = party_size * per_person * random.uniform(0.85, 1.15)

        return round(total, 2)

    def _determine_order_type(self, hour: int) -> str:
        """
        Determine order type based on hour

        Args:
            hour: Hour of day (0-23)

        Returns:
            'dine_in', 'takeout', or 'delivery'
        """
        # Lunch/dinner = more dine-in
        # Late night = more takeout/delivery

        if 11 <= hour <= 14 or 17 <= hour <= 20:
            # Peak meal times - mostly dine-in
            return np.random.choice(
                ["dine_in", "takeout", "delivery"], p=[0.75, 0.20, 0.05]
            )
        else:
            # Off-peak - more takeout
            return np.random.choice(
                ["dine_in", "takeout", "delivery"], p=[0.60, 0.30, 0.10]
            )

    def generate_wait_times(self, orders_df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate wait time logs based on order patterns

        Args:
            orders_df: DataFrame with orders

        Returns:
            DataFrame with wait time records
        """
        logger.info("⏱️  Generating wait time logs...")

        # Group orders by hour to calculate occupancy
        orders_df["date"] = pd.to_datetime(orders_df["order_timestamp"]).dt.date
        orders_df["hour"] = pd.to_datetime(orders_df["order_timestamp"]).dt.hour

        hourly_counts = (
            orders_df.groupby(["date", "hour"]).size().reset_index(name="order_count")
        )

        wait_times = []
        wait_time_id = 1

        for _, hour_row in hourly_counts.iterrows():
            date = hour_row["date"]
            hour = hour_row["hour"]
            order_count = hour_row["order_count"]

            # Calculate occupancy based on order count
            # Assume max capacity is 30 tables, peak hour has ~20 orders
            occupancy_pct = min(95, (order_count / 20) * 70)

            # Generate 2-5 wait time logs per hour
            num_logs = random.randint(2, 5)

            for _ in range(num_logs):
                minute = random.randint(0, 59)
                log_timestamp = datetime.combine(date, time(hour, minute))

                party_size = self._generate_party_size()

                # Calculate wait time based on occupancy
                if occupancy_pct < 50:
                    quoted_wait = random.randint(5, 15)
                elif occupancy_pct < 75:
                    quoted_wait = random.randint(15, 30)
                else:
                    quoted_wait = random.randint(25, 45)

                # Actual wait varies from quoted (-30% to +50%)
                actual_wait = int(quoted_wait * random.uniform(0.7, 1.5))
                actual_wait = max(0, actual_wait)

                seated_timestamp = log_timestamp + timedelta(minutes=actual_wait)

                wait_times.append(
                    {
                        "wait_time_id": wait_time_id,
                        "log_timestamp": log_timestamp,
                        "party_size": party_size,
                        "quoted_wait_minutes": quoted_wait,
                        "actual_wait_minutes": actual_wait,
                        "seated_timestamp": seated_timestamp,
                        "day_of_week": log_timestamp.weekday(),
                        "hour_of_day": hour,
                        "current_party_count": int(order_count * 1.5),  # Estimate
                        "current_table_occupancy_pct": round(occupancy_pct, 2),
                        "wait_type": "walk_in",
                    }
                )

                wait_time_id += 1

        wait_times_df = pd.DataFrame(wait_times)
        logger.info(f"   ✓ Generated {len(wait_times_df)} wait time records")

        return wait_times_df

    def save_processed_data(self, orders_df: pd.DataFrame, wait_times_df: pd.DataFrame):
        """Save processed data to CSV files"""
        output_dir = Path("data/processed")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save orders
        orders_file = output_dir / "orders_from_real_data.csv"
        orders_df.to_csv(orders_file, index=False)
        logger.info(f"✓ Saved orders to {orders_file}")

        # Save wait times
        wait_times_file = output_dir / "wait_times_from_real_data.csv"
        wait_times_df.to_csv(wait_times_file, index=False)
        logger.info(f"✓ Saved wait times to {wait_times_file}")

        # Generate summary report
        self._generate_summary_report(orders_df, wait_times_df, output_dir)

    def _generate_summary_report(
        self, orders_df: pd.DataFrame, wait_times_df: pd.DataFrame, output_dir: Path
    ):
        """Generate summary report of processed data"""
        report_file = output_dir / "data_summary.txt"

        with open(report_file, "w") as f:
            f.write("=" * 60 + "\n")
            f.write("DINEMETRA - REAL DATA PROCESSING SUMMARY\n")
            f.write("=" * 60 + "\n\n")

            f.write("📊 ORDERS DATA:\n")
            f.write(f"   Total Orders: {len(orders_df):,}\n")
            f.write(
                f"   Date Range: {orders_df['order_timestamp'].min().date()} to {orders_df['order_timestamp'].max().date()}\n"
            )
            f.write(f"   Total Revenue: ${orders_df['order_total'].sum():,.2f}\n")
            f.write(f"   Average Check: ${orders_df['order_total'].mean():.2f}\n")
            f.write(f"   Average Party Size: {orders_df['party_size'].mean():.1f}\n\n")

            f.write("⏱️  WAIT TIMES DATA:\n")
            f.write(f"   Total Logs: {len(wait_times_df):,}\n")
            f.write(
                f"   Avg Quoted Wait: {wait_times_df['quoted_wait_minutes'].mean():.1f} min\n"
            )
            f.write(
                f"   Avg Actual Wait: {wait_times_df['actual_wait_minutes'].mean():.1f} min\n"
            )
            f.write(
                f"   Avg Accuracy: {((wait_times_df['quoted_wait_minutes'] - wait_times_df['actual_wait_minutes']).abs().mean()):.1f} min error\n\n"
            )

            f.write("📅 BUSIEST DAYS:\n")
            daily = (
                orders_df.groupby(pd.to_datetime(orders_df["order_timestamp"]).dt.date)
                .agg({"order_id": "count", "order_total": "sum"})
                .nlargest(5, "order_id")
            )

            for date, row in daily.iterrows():
                f.write(
                    f"   {date}: {row['order_id']} orders, ${row['order_total']:.2f}\n"
                )

            f.write("\n" + "=" * 60 + "\n")

        logger.info(f"✓ Saved summary report to {report_file}")


# ========================================
# MAIN EXECUTION
# ========================================


def main():
    """Process real restaurant data"""
    logger.info("=" * 60)
    logger.info("🍽️  DINEMETRA - REAL DATA PROCESSOR")
    logger.info("=" * 60)

    # Initialize extractor
    extractor = RealDataExtractor(data_dir="data/real")

    # Load all CSV files
    extractor.load_all_data_by_month()

    if extractor.daily_sales is None:
        logger.error("\n❌ No data loaded. Please add CSV files to data/real/")
        return

    # Generate detailed orders
    orders_df = extractor.generate_detailed_orders()

    if orders_df.empty:
        logger.error("\n❌ Failed to generate orders")
        return

    # Generate wait times
    wait_times_df = extractor.generate_wait_times(orders_df)

    # Save processed data
    extractor.save_processed_data(orders_df, wait_times_df)

    logger.info("\n" + "=" * 60)
    logger.info("✅ REAL DATA PROCESSING COMPLETE!")
    logger.info("=" * 60)
    logger.info("\nNext steps:")
    logger.info("1. Review data/processed/ for generated files")
    logger.info("2. Run ETL pipeline: python -m etl.transform")
    logger.info("3. Train models: python scripts/train_models.py")


if __name__ == "__main__":
    main()
