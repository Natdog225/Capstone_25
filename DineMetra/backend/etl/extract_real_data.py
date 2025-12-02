import pandas as pd
import numpy as np
import os
import json
import logging
import random
from datetime import datetime, time, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RealDataExtractor:
    """
    Extracts and processes real restaurant data from CSV exports.
    Generates simulated detailed orders based on aggregate daily totals
    and real product mix distributions.
    """

    def __init__(self, data_dir: str = "data/real"):
        self.data_dir = Path(data_dir)
        self.processed_dir = Path("data/processed")
        self.processed_dir.mkdir(parents=True, exist_ok=True)

        # Data containers
        self.daily_sales = pd.DataFrame()
        self.hourly_patterns = {}
        self.product_mix = []  # List of {name, category, price, weight}
        self.menu_map = {}  # name -> ID mapping

    def run(self):
        """Main execution flow"""
        logger.info("🚀 Starting Real Data Extraction...")

        # 1. Traverse directories and load data
        self.load_raw_files()

        # 2. Generate Menu from Product Mix
        self.generate_menu_reference()

        # 3. Generate Orders & Order Items
        orders_df, order_items_df = self.generate_detailed_orders()

        # 4. Save Outputs
        if not orders_df.empty:
            orders_path = self.processed_dir / "orders_from_real_data.csv"
            orders_df.to_csv(orders_path, index=False)
            logger.info(f"✓ Saved {len(orders_df)} orders to {orders_path}")

        if not order_items_df.empty:
            items_path = self.processed_dir / "order_items_from_real_data.csv"
            order_items_df.to_csv(items_path, index=False)
            logger.info(f"✓ Saved {len(order_items_df)} order items to {items_path}")

    def load_raw_files(self):
        """Scans monthly folders and identifies file types by column headers"""
        if not self.data_dir.exists():
            logger.error(f"❌ Data directory not found: {self.data_dir}")
            return

        # Walk through month folders (2025-01, etc.)
        for month_dir in sorted(self.data_dir.glob("202*-*")):
            if not month_dir.is_dir():
                continue

            logger.info(f"\n📅 Processing {month_dir.name}...")

            for csv_file in month_dir.glob("*.csv"):
                try:
                    filename = csv_file.name.lower()

                    # 1. DAILY SALES DETECTION
                    if "sales by day" in filename:
                        self._process_daily_sales(csv_file)
                        continue

                    # 2. HOURLY SALES
                    elif "time of day" in filename:
                        self._process_hourly_sales(csv_file)
                        continue

                    # 3. PRODUCT MIX (Look for "_Items.csv")
                    elif "_items.csv" in filename or "menu item" in filename:
                        self._process_product_mix(csv_file)
                        continue

                    # Fallback: Header Inspection (Last Resort)
                    try:
                        df_preview = pd.read_csv(csv_file, nrows=1)
                        columns = set(c.lower().strip() for c in df_preview.columns)

                        if {"date", "gross sales", "net sales"}.issubset(columns):
                            self._process_daily_sales(csv_file)
                        elif {"item", "qty sold"}.issubset(columns):
                            self._process_product_mix(csv_file)

                    except:
                        continue

                except Exception as e:
                    logger.warning(f"   ⚠️ Error reading {csv_file.name}: {e}")

    def _process_daily_sales(self, filepath):
        try:
            df = pd.read_csv(filepath)
            # Normalize columns
            df.columns = [c.lower().strip() for c in df.columns]

            # Map common column names
            date_col = next((c for c in df.columns if "date" in c or "day" in c), None)
            orders_col = next(
                (
                    c
                    for c in df.columns
                    if "count" in c or "orders" in c or "trans" in c
                ),
                None,
            )
            rev_col = next(
                (c for c in df.columns if "net sales" in c or "revenue" in c), None
            )

            if date_col and orders_col:
                # Clean data
                df = df[[date_col, orders_col, rev_col]].copy()
                df.columns = ["date", "order_count", "revenue"]
                df["date"] = pd.to_datetime(df["date"], errors="coerce")
                df = df.dropna(subset=["date"])

                self.daily_sales = pd.concat([self.daily_sales, df], ignore_index=True)
                logger.info(f"   ✓ Loaded daily sales ({len(df)} days)")
        except Exception as e:
            logger.warning(f"   ⚠️ Failed to process daily sales: {e}")

    def _process_hourly_sales(self, filepath):
        try:
            df = pd.read_csv(filepath)
            df.columns = [c.lower().strip() for c in df.columns]

            # Look for Time and Count/Sales
            time_col = next((c for c in df.columns if "time" in c or "hour" in c), None)
            val_col = next(
                (
                    c
                    for c in df.columns
                    if "count" in c or "orders" in c or "sales" in c
                ),
                None,
            )

            if time_col and val_col:
                # Create a distribution profile
                df["hour"] = pd.to_datetime(
                    df[time_col], format="%H:%M", errors="coerce"
                ).dt.hour
                df = df.dropna(subset=["hour"])

                total = df[val_col].sum()
                if total > 0:
                    dist = df.set_index("hour")[val_col] / total
                    # Store average pattern (could be refined by day of week)
                    self.hourly_patterns["default"] = dist.to_dict()
                    logger.info("   ✓ Loaded hourly pattern")
        except Exception as e:
            logger.warning(f"   ⚠️ Failed to process hourly pattern: {e}")

    def _process_product_mix(self, filepath):
        """Reads item sales data to build a product catalog and popularity weights"""
        try:
            df = pd.read_csv(filepath)
            df.columns = [c.lower().strip() for c in df.columns]

            # Map columns
            item_col = next(
                (c for c in df.columns if c in ["item", "menu item", "name"]), None
            )
            qty_col = next(
                (c for c in df.columns if c in ["qty sold", "quantity", "count"]), None
            )
            price_col = next(
                (c for c in df.columns if c in ["avg. price", "price", "amount"]), None
            )
            cat_col = next(
                (c for c in df.columns if c in ["sales category", "group", "category"]),
                None,
            )

            if item_col and qty_col:
                # Add to master product mix list
                for _, row in df.iterrows():
                    name = str(row[item_col]).strip()
                    if not name or name.lower() in ["total", "nan"]:
                        continue

                    try:
                        qty = float(row[qty_col])
                        if qty <= 0:
                            continue

                        price = float(row[price_col]) if price_col else 10.0
                        category = str(row[cat_col]) if cat_col else "Food"

                        self.product_mix.append(
                            {
                                "name": name,
                                "category": category,
                                "price": price,
                                "weight": qty,  # Used for weighted random choice
                            }
                        )
                    except:
                        continue
                logger.info(f"   ✓ Loaded {len(df)} items into product mix")
        except Exception as e:
            logger.warning(f"   ⚠️ Failed to process product mix: {e}")

    def generate_menu_reference(self):
        """Creates a consolidated menu from all product mix files"""
        if not self.product_mix:
            logger.warning("⚠️ No product mix data found. Using dummy menu.")
            self.menu_map = {"Generic Item": 1}
            return

        # Deduplicate and average prices
        menu_df = pd.DataFrame(self.product_mix)
        menu_df = (
            menu_df.groupby("name")
            .agg(
                {
                    "category": "first",
                    "price": "mean",
                    "weight": "sum",  # Aggregate popularity across months
                }
            )
            .reset_index()
        )

        # Assign IDs
        menu_df["item_id"] = range(1, len(menu_df) + 1)

        # Save reference
        menu_path = self.data_dir.parent / "menu_items_reference.csv"
        menu_df.to_csv(menu_path, index=False)
        logger.info(f"✓ Generated unified menu with {len(menu_df)} items")

        # Create lookup map and weights for generation
        self.menu_items = menu_df.to_dict("records")
        self.item_weights = menu_df["weight"].values / menu_df["weight"].sum()

    def generate_detailed_orders(self):
        """
        Generates Orders AND OrderItems using the real product mix.
        """
        logger.info("🔄 Generating detailed orders and items...")

        if self.daily_sales.empty:
            logger.error("❌ No daily sales data loaded")
            return pd.DataFrame(), pd.DataFrame()

        # Fix NaNs
        self.daily_sales["order_count"] = self.daily_sales["order_count"].fillna(0)

        all_orders = []
        all_order_items = []
        order_id_counter = 100000

        for _, day_row in self.daily_sales.iterrows():
            # Safe date parsing
            try:
                date = pd.to_datetime(day_row["date"])
                total_orders = int(day_row["order_count"])
                if total_orders <= 0:
                    continue
            except:
                continue

            # Get hourly pattern (default if missing)
            dist = self.hourly_patterns.get("default", {12: 0.3, 19: 0.7})

            # Generate orders for each hour
            for hour, prob in dist.items():
                hour = int(hour)
                num_orders_hour = int(total_orders * prob)

                for _ in range(num_orders_hour):
                    order_id = order_id_counter
                    order_id_counter += 1

                    # Random minute
                    timestamp = date.replace(hour=hour, minute=random.randint(0, 59))

                    # 1. Determine Party Size (Weighted towards 2-4)
                    party_size = random.choices(
                        [1, 2, 3, 4, 5, 6, 8], weights=[10, 40, 20, 15, 10, 4, 1]
                    )[0]

                    # 2. Pick Items (Based on REAL popularity)
                    # A party of 4 usually orders ~4-6 items
                    num_items = random.randint(party_size, party_size + 2)

                    if self.product_mix:
                        selected_items = np.random.choice(
                            self.menu_items, size=num_items, p=self.item_weights
                        )
                    else:
                        # Fallback if no product mix found
                        selected_items = [
                            {
                                "name": "Generic Food",
                                "price": 15.0,
                                "category": "Food",
                                "item_id": 1,
                            }
                        ] * num_items

                    # 3. Create Order Items & Calculate Total
                    order_total = 0
                    for item in selected_items:
                        qty = 1  # Simplified: 1 line per item choice
                        price = item["price"]
                        order_total += price

                        all_order_items.append(
                            {
                                "order_id": order_id,
                                "item_id": item["item_id"],
                                "item_name": item["name"],
                                "category": item["category"],
                                "quantity": qty,
                                "price": round(price, 2),
                            }
                        )

                    # 4. Create Order Header
                    all_orders.append(
                        {
                            "order_id": order_id,
                            "order_timestamp": timestamp,
                            "party_size": party_size,
                            "order_total": round(order_total * 1.08, 2),  # Add tax
                            "item_count": num_items,
                        }
                    )

        return pd.DataFrame(all_orders), pd.DataFrame(all_order_items)


def main():
    extractor = RealDataExtractor()
    extractor.run()


if __name__ == "__main__":
    main()
