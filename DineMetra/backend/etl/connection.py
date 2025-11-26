# backend/etl/connection.py
import os
import logging
from typing import Optional, Dict
from psycopg2 import pool, OperationalError

logger = logging.getLogger("etl.connection")

# Read env vars only here
PG_HOST = os.getenv("PGHOST")
PG_PORT = int(os.getenv("PGPORT", 5432))
PG_DB = os.getenv("PGDATABASE")
PG_USER = os.getenv("PGUSER")
PG_PASSWORD = os.getenv("PGPASSWORD")
PG_SSLMODE = os.getenv("PGSSLMODE", "require")
PG_SSLROOTCERT = os.getenv("PGSSLROOTCERT")  # optional
PG_POOL_MIN = int(os.getenv("PG_POOL_MIN", 1))
PG_POOL_MAX = int(os.getenv("PG_POOL_MAX", 5))
RETRY_ATTEMPTS = int(os.getenv("ETL_RETRY_ATTEMPTS", 3))
RETRY_BACKOFF_SEC = float(os.getenv("ETL_RETRY_BACKOFF_SEC", 1.0))

_conn_pool: Optional[pool.SimpleConnectionPool] = None


def _build_conn_kwargs() -> Dict:
    kwargs = {
        "host": PG_HOST,
        "port": PG_PORT,
        "dbname": PG_DB,
        "user": PG_USER,
        "password": PG_PASSWORD,
        "application_name": "etl_loader",
    }
    if PG_SSLMODE and PG_SSLMODE.lower() != "disable":
        kwargs["sslmode"] = PG_SSLMODE
        if PG_SSLROOTCERT:
            kwargs["sslrootcert"] = PG_SSLROOTCERT
    return kwargs


def init_pool():
    global _conn_pool
    if _conn_pool is not None:
        return
    kwargs = _build_conn_kwargs()
    attempt = 0
    while attempt < RETRY_ATTEMPTS:
        try:
            _conn_pool = pool.SimpleConnectionPool(
                minconn=PG_POOL_MIN, maxconn=PG_POOL_MAX, **kwargs
            )
            logger.info("DB pool created min=%d max=%d", PG_POOL_MIN, PG_POOL_MAX)
            return
        except OperationalError as e:
            attempt += 1
            logger.warning(
                "Pool creation failed attempt %d/%d: %s",
                attempt,
                RETRY_ATTEMPTS,
                str(e),
            )
            import time

            time.sleep(RETRY_BACKOFF_SEC * attempt)
    raise RuntimeError("Could not create DB connection pool")


def get_conn():
    if _conn_pool is None:
        init_pool()
    return _conn_pool.getconn()


def put_conn(conn):
    if _conn_pool:
        _conn_pool.putconn(conn)
