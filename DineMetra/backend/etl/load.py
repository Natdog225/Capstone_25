# backend/etl/load.py
import logging
import psycopg_pool
import pandas as pd
from config import DATABASE_URL

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

# Connection pool
pool = psycopg_pool.ConnectionPool(DATABASE_URL)

def insert_dataframe(df: pd.DataFrame, table_name: str, conn):
    """
    Generic insert function for a DataFrame into a given table.
    Assumes DataFrame columns match table columns.
    """
    with conn.cursor() as cur:
        for _, row in df.iterrows():
            cols = ','.join(df.columns)
            placeholders = ','.join(['%s'] * len(row))
            sql = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"
            cur.execute(sql, tuple(row))
    conn.commit()
    logging.info(f"Inserted {len(df)} rows into {table_name}")
    
def safe_insert(df, table, conn):
    if df.empty:
        logging.warning(f"No data to insert into {table}")
        return
    # Example: enforce schema match
    expected_cols = get_expected_columns(table)
    if set(df.columns) != set(expected_cols):
        raise ValueError(f"Schema mismatch for {table}")
    insert_dataframe(df, table, conn)

def load_dataframes(menu_items, orders, order_items, wait_times, external_factors):
    """
    Load all cleaned DataFrames into PostgreSQL with FK handling.
    """
    with pool.connection() as conn:
        # Insert menu_items first (FK target for order_items)
        insert_dataframe(menu_items, "menu_items", conn)

        # Insert orders (FK target for order_items, wait_times)
        insert_dataframe(orders, "orders", conn)

        # Insert order_items (links orders ↔ menu_items)
        insert_dataframe(order_items, "order_items", conn)

        # Insert wait_times (FK to orders)
        insert_dataframe(wait_times, "wait_times", conn)

        # Insert external_factors (independent table)
        insert_dataframe(external_factors, "external_factors", conn)

    logging.info("All DataFrames loaded successfully")
    