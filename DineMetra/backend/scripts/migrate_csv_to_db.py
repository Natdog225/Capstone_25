"""Migrate CSV to Neon Database"""

import pandas as pd
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from app.database.database import SessionLocal, init_db
from app.models.database_models import MenuItem, Order, OrderItem, WaitTime


def main():
    print("🚀 MIGRATING TO NEON DATABASE")
    print("=" * 60)

    init_db()

    base = Path("data/processed")
    items_df = pd.read_csv(base / "order_items_from_real_data.csv")
    orders_df = pd.read_csv(base / "orders_from_real_data.csv")
    wait_df = pd.read_csv(base / "wait_times_from_real_data.csv")

    print(f"✓ {len(items_df):,} items")
    print(f"✓ {len(orders_df):,} orders")
    print(f"✓ {len(wait_df):,} wait times\n")

    db = SessionLocal()

    try:
        # Menu items
        print("Loading menu items...")
        unique = items_df[["item_name", "category", "unit_price"]].drop_duplicates(
            "item_name"
        )
        menu_items = [
            MenuItem(
                item_name=r["item_name"],
                category=r["category"],
                price=float(r["unit_price"]),
                is_active=True,
            )
            for _, r in unique.iterrows()
        ]
        db.bulk_save_objects(menu_items)
        db.commit()
        item_map = {i.item_name: i.id for i in db.query(MenuItem).all()}
        print(f"✓ {len(item_map)} menu items\n")

        # Orders
        print("Loading orders...")
        orders = [
            Order(
                order_number=str(r["order_id"]),
                order_timestamp=pd.to_datetime(r["order_timestamp"]),
                order_total=float(r["order_total"]),
                party_size=int(r.get("party_size", 2)),
            )
            for _, r in orders_df.iterrows()
        ]
        db.bulk_save_objects(orders)
        db.commit()
        order_map = {o.order_number: o.id for o in db.query(Order).all()}
        print(f"✓ {len(order_map)} orders\n")

        # Order items
        print("Loading order items (batched)...")
        order_items = []
        for _, r in items_df.iterrows():
            item_id = item_map.get(r["item_name"])
            order_id = order_map.get(str(r["order_id"]))
            if item_id and order_id:
                order_items.append(
                    OrderItem(
                        order_id=order_id,
                        menu_item_id=item_id,
                        quantity=int(r["quantity"]),
                        unit_price=float(r["unit_price"]),
                        total_price=float(r["total_price"]),
                    )
                )

        for i in range(0, len(order_items), 1000):
            db.bulk_save_objects(order_items[i : i + 1000])
            db.commit()
            print(f"  Batch {i//1000 + 1}")
        print(f"✓ {len(order_items)} order items\n")

        # Wait times
        print("Loading wait times...")
        wait_times = []
        for _, r in wait_df.iterrows():
            ts = pd.to_datetime(r["timestamp"])
            wait_times.append(
                WaitTime(
                    timestamp=ts,
                    party_size=int(r["party_size"]),
                    actual_wait_minutes=int(r["actual_wait_minutes"]),
                    occupancy_percentage=float(r.get("current_table_occupancy_pct", 0)),
                    day_of_week=ts.weekday(),
                    hour_of_day=ts.hour,
                )
            )
        db.bulk_save_objects(wait_times)
        db.commit()
        print(f"✓ {len(wait_times)} wait times\n")

        print("=" * 60)
        print("✅ MIGRATION COMPLETE!")
        print("=" * 60)
        print(f"Menu Items: {db.query(MenuItem).count():,}")
        print(f"Orders: {db.query(Order).count():,}")
        print(f"Order Items: {db.query(OrderItem).count():,}")
        print(f"Wait Times: {db.query(WaitTime).count():,}")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
