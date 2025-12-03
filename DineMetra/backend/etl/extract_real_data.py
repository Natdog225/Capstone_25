import pandas as pd
import numpy as np
import os
import json
import logging
import random
from datetime import datetime, time, timedelta
from pathlib import Path
from typing import Dict, List, Optional

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RealDataExtractor:
    def __init__(self, data_dir: str = "data/real"):
        self.data_dir = Path(data_dir)
        self.processed_dir = Path("data/processed")
        self.processed_dir.mkdir(parents=True, exist_ok=True)

        self.daily_sales = pd.DataFrame()
        self.hourly_patterns = {}
        self.product_mix = []
        self.menu_items = []
        self.item_weights = []

    def run(self):
        logger.info("🚀 Starting Real Data Extraction...")
        self.load_raw_files()
        self.generate_menu_reference()
        orders_df, order_items_df = self.generate_detailed_orders()

        if not orders_df.empty:
            orders_path = self.processed_dir / "orders_from_real_data.csv"
            orders_df.to_csv(orders_path, index=False)
            logger.info(f"✓ Saved {len(orders_df)} orders to {orders_path}")

        if not order_items_df.empty:
            items_path = self.processed_dir / "order_items_from_real_data.csv"
            order_items_df.to_csv(items_path, index=False)
            logger.info(f"✓ Saved {len(order_items_df)} order items to {items_path}")

    def load_raw_files(self):
        if not self.data_dir.exists():
            logger.error(f"❌ Data directory not found: {self.data_dir}")
            return

        for month_dir in sorted(self.data_dir.glob("202*-*")):
            if not month_dir.is_dir():
                continue
            logger.info(f"\n📅 Processing {month_dir.name}...")

            for csv_file in month_dir.glob("*.csv"):
                try:
                    filename = csv_file.name.lower()

                    # 1. DAILY SALES (Priority Match)
                    if "sales by day" in filename:
                        self._process_daily_sales(csv_file)
                        continue

                    # 2. HOURLY SALES
                    elif "time of day" in filename:
                        self._process_hourly_sales(csv_file)
                        continue

                    # 3. PRODUCT MIX
                    elif "_items.csv" in filename or "menu item" in filename:
                        self._process_product_mix(csv_file)
                        continue

                    # Fallback check
                    try:
                        df_preview = pd.read_csv(csv_file, nrows=1)
                        columns = set(c.lower().strip() for c in df_preview.columns)

                        # UPDATED MATCHERS for your specific file format
                        if {"yyyymmdd", "net sales"}.issubset(columns):
                            self._process_daily_sales(csv_file)
                        elif {"date", "gross sales"}.issubset(columns):
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
            df.columns = [c.lower().strip() for c in df.columns]

            # --- UPDATED COLUMN MATCHING LOGIC ---
            # Date: looks for 'date', 'day', OR your specific 'yyyymmdd'
            date_col = next(
                (
                    c
                    for c in df.columns
                    if any(x in c for x in ["date", "day", "yyyymmdd"])
                ),
                None,
            )

            # Orders: looks for 'orders', 'count', etc.
            orders_col = next(
                (
                    c
                    for c in df.columns
                    if any(
                        x in c
                        for x in ["total orders", "count", "orders", "trans", "checks"]
                    )
                ),
                None,
            )

            # Revenue: looks for 'net sales', 'revenue'
            rev_col = next(
                (
                    c
                    for c in df.columns
                    if any(x in c for x in ["net sales", "revenue", "sales"])
                ),
                None,
            )

            if date_col and orders_col:
                df = df[[date_col, orders_col, rev_col]].copy()
                df.columns = ["date", "order_count", "revenue"]

                # Intelligent date parsing
                if "yyyymmdd" in date_col:
                    # Parse specifically for the 20250101 format
                    df["date"] = pd.to_datetime(
                        df["date"], format="%Y%m%d", errors="coerce"
                    )
                else:
                    df["date"] = pd.to_datetime(df["date"], errors="coerce")

                df = df.dropna(subset=["date"])
                self.daily_sales = pd.concat([self.daily_sales, df], ignore_index=True)
                logger.info(f"   ✓ Loaded daily sales ({len(df)} days)")
            else:
                # Debug log if it still fails
                logger.warning(
                    f"   ⚠️ Skipping {filepath.name}: Missing cols. Found: {list(df.columns)}"
                )

        except Exception as e:
            logger.warning(f"   ⚠️ Failed to process daily sales: {e}")

    def _process_hourly_sales(self, filepath):
        try:
            df = pd.read_csv(filepath)
            df.columns = [c.lower().strip() for c in df.columns]
            time_col = next((c for c in df.columns if "time" in c or "hour" in c), None)
            val_col = next(
                (
                    c
                    for c in df.columns
                    if any(x in c for x in ["count", "orders", "sales", "trans"])
                ),
                None,
            )

            if time_col and val_col:
                df["hour"] = pd.to_datetime(
                    df[time_col], format="%H:%M", errors="coerce"
                ).dt.hour
                df = df.dropna(subset=["hour"])
                total = df[val_col].sum()
                if total > 0:
                    dist = df.set_index("hour")[val_col] / total
                    self.hourly_patterns["default"] = dist.to_dict()
                    logger.info("   ✓ Loaded hourly pattern")
        except Exception as e:
            logger.warning(f"   ⚠️ Failed to process hourly pattern: {e}")

    def _process_product_mix(self, filepath):
        try:
            df = pd.read_csv(filepath)
            df.columns = [c.lower().strip() for c in df.columns]
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
                                "weight": qty,
                            }
                        )
                    except:
                        continue
                logger.info(f"   ✓ Loaded {len(df)} items into product mix")
        except Exception as e:
            logger.warning(f"   ⚠️ Failed to process product mix: {e}")

    def generate_menu_reference(self):
        if not self.product_mix:
            logger.warning("⚠️ No product mix data found. Using dummy menu.")
            self.menu_items = [
                {
                    "name": "Generic Item",
                    "price": 10.0,
                    "item_id": 1,
                    "category": "Food",
                }
            ]
            self.item_weights = [1.0]
            return

        menu_df = pd.DataFrame(self.product_mix)
        menu_df = (
            menu_df.groupby("name")
            .agg({"category": "first", "price": "mean", "weight": "sum"})
            .reset_index()
        )
        menu_df["item_id"] = range(1, len(menu_df) + 1)

        menu_path = self.data_dir.parent / "menu_items_reference.csv"
        menu_df.to_csv(menu_path, index=False)
        logger.info(f"✓ Generated unified menu with {len(menu_df)} items")

        self.menu_items = menu_df.to_dict("records")
        self.item_weights = menu_df["weight"].values / menu_df["weight"].sum()

    def generate_detailed_orders(self):
        logger.info("🔄 Generating detailed orders...")
        if self.daily_sales.empty:
            logger.error("❌ No daily sales data loaded")
            return pd.DataFrame(), pd.DataFrame()

        # NaN Safety Fix
        self.daily_sales["order_count"] = self.daily_sales["order_count"].fillna(0)
        self.daily_sales["revenue"] = self.daily_sales["revenue"].fillna(0)

        all_orders, all_order_items = [], []
        order_id_counter = 100000

        for _, day_row in self.daily_sales.iterrows():
            try:
                # Safe date check
                if isinstance(day_row["date"], str) and "Total" in day_row["date"]:
                    continue
                date = pd.to_datetime(day_row["date"])

                total_orders = int(day_row["order_count"])
                if total_orders <= 0:
                    continue
            except:
                continue

            dist = self.hourly_patterns.get("default", {12: 0.3, 19: 0.7})

            for hour, prob in dist.items():
                hour = int(hour)
                num_orders_hour = int(total_orders * prob)

                for _ in range(num_orders_hour):
                    order_id = order_id_counter
                    order_id_counter += 1
                    timestamp = date.replace(hour=hour, minute=random.randint(0, 59))
                    party_size = random.choices(
                        [1, 2, 3, 4, 5, 6, 8], weights=[10, 40, 20, 15, 10, 4, 1]
                    )[0]
                    num_items = random.randint(party_size, party_size + 2)

                    selected_items = np.random.choice(
                        self.menu_items, size=num_items, p=self.item_weights
                    )
                    order_total = 0

                    for item in selected_items:
                        price = item["price"]
                        order_total += price
                        all_order_items.append(
                            {
                                "order_id": order_id,
                                "item_id": item["item_id"],
                                "item_name": item["name"],
                                "category": item["category"],
                                "quantity": 1,
                                "price": round(price, 2),
                            }
                        )

                    all_orders.append(
                        {
                            "order_id": order_id,
                            "order_timestamp": timestamp,
                            "party_size": party_size,
                            "order_total": round(order_total * 1.08, 2),
                            "item_count": num_items,
                        }
                    )

        return pd.DataFrame(all_orders), pd.DataFrame(all_order_items)


if __name__ == "__main__":
    RealDataExtractor().run()
