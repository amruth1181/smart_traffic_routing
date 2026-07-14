# ------------------------------------------------------------------
# Warehouse Loader:  MongoDB (or CSV fallback)  ->  Postgres  raw.*
# ------------------------------------------------------------------
# This is the "Load" step of the ELT pipeline. It takes the enriched,
# stream-joined records and lands them in a `raw` schema in the warehouse.
# dbt then does the "Transform" step on top of this raw table.
#
# Run:  python warehouse/load_to_postgres.py
# ------------------------------------------------------------------

import os
from datetime import datetime, timezone

import pandas as pd
from sqlalchemy import create_engine, text

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv is optional; env vars can be exported manually

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Canonical column set for the raw table (matches the Spark enriched output).
CANONICAL_COLUMNS = [
    "time", "station_id", "freeway", "direction", "lane_type",
    "flow", "occupancy", "speed", "region", "temperature",
    "windspeed", "weathercode", "incident_type", "severity", "description",
]

RAW_SCHEMA = os.getenv("WAREHOUSE_RAW_SCHEMA", "raw")
RAW_TABLE = "traffic_weather_incidents"


def get_engine():
    """Build a SQLAlchemy engine from environment variables."""
    host = os.getenv("WAREHOUSE_HOST", "localhost")
    port = os.getenv("WAREHOUSE_PORT", "5432")
    db = os.getenv("WAREHOUSE_DB", "traffic_warehouse")
    user = os.getenv("WAREHOUSE_USER", "traffic")
    password = os.getenv("WAREHOUSE_PASSWORD", "traffic")
    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
    return create_engine(url)


def extract_from_mongo():
    """Primary source: the enriched collection written by the Spark job."""
    try:
        from pymongo import MongoClient
    except ImportError:
        return None

    uri = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/")
    db_name = os.getenv("MONGO_DB", "smart_traffic_db")
    coll_name = os.getenv("MONGO_COLLECTION", "traffic_weather_incidents")

    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=3000)
        client.admin.command("ping")  # fail fast if Mongo is unreachable
        docs = list(client[db_name][coll_name].find({}, {"_id": 0}))
        if not docs:
            print("ℹ️  MongoDB reachable but collection is empty.")
            return None
        print(f"✅ Extracted {len(docs)} records from MongoDB.")
        return pd.DataFrame(docs)
    except Exception as e:
        print(f"⚠️  Could not read from MongoDB ({e}). Falling back to CSV.")
        return None


def extract_from_csv():
    """Fallback source: the generated synthetic dataset."""
    csv_path = os.path.join(BASE_DIR, "traffic_weather_incidents.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"No data source available. Run generate_mock_traffic.py first "
            f"(expected {csv_path})."
        )
    print(f"✅ Extracted records from CSV fallback: {csv_path}")
    return pd.read_csv(csv_path)


def standardize(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure every canonical column exists, then add a load timestamp."""
    for col in CANONICAL_COLUMNS:
        if col not in df.columns:
            df[col] = None
    df = df[CANONICAL_COLUMNS].copy()
    df["_loaded_at"] = datetime.now(timezone.utc)
    return df


def load(df: pd.DataFrame, engine):
    """Create the raw schema and (re)load the raw table."""
    with engine.begin() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {RAW_SCHEMA};"))
    df.to_sql(
        RAW_TABLE,
        engine,
        schema=RAW_SCHEMA,
        if_exists="replace",   # full-refresh load; simple & idempotent for a demo
        index=False,
    )
    print(f"✅ Loaded {len(df)} rows into {RAW_SCHEMA}.{RAW_TABLE}.")


def main():
    df = extract_from_mongo()
    if df is None:
        df = extract_from_csv()

    df = standardize(df)
    engine = get_engine()
    load(df, engine)
    print("🏁 Warehouse load complete.")


if __name__ == "__main__":
    main()
