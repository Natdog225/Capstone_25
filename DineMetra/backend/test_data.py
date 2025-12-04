import pandas as pd

# Load the data
orders = pd.read_csv("data/orders_raw.csv")
order_items = pd.read_csv("data/order_items_raw.csv")
wait_times = pd.read_csv("data/wait_times_raw.csv")
external = pd.read_csv("data/external_factors_raw.csv")
menu = pd.read_csv("data/menu_items_reference.csv")

print("📊 Data Overview:")
print(f"Orders: {len(orders)}")
print(f"Order Items: {len(order_items)}")
print(f"Wait Times: {len(wait_times)}")
print(f"External Factors: {len(external)}")
print(f"Menu Items: {len(menu)}")

print("\n⚠️  Data Quality Issues Found:")
print(f"Missing timestamps: {orders['order_timestamp'].isna().sum()}")
print(f"Negative tips: {(orders['tip_amount'] < 0).sum()}")
print(
    f"Outlier party sizes: {((orders['party_size'] <= 0) | (orders['party_size'] > 10)).sum()}"
)
print(f"Duplicate order IDs: {orders['order_id'].duplicated().sum()}")

print("\n🔥 Busiest hour:")
orders["hour"] = pd.to_datetime(orders["order_timestamp"]).dt.hour
busiest = orders.groupby("hour").size().idxmax()
print(f"Hour {busiest}:00 with {orders.groupby('hour').size().max()} orders")

print("\n🍔 Top 5 items:")
top_items = (
    order_items.groupby("item_name")["quantity"]
    .sum()
    .sort_values(ascending=False)
    .head()
)
print(top_items)
