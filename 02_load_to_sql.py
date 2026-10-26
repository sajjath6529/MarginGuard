"""
==============================================================================
PROJECT: Omnichannel Profitability & Margin Leakage Intelligence Engine
MODULE: 02_load_to_sql.py
DESCRIPTION: Ingests raw CSV data into a relational SQLite database, builds 
             schema constraints & indexes, and validates data integrity.
==============================================================================
"""

import os
import sys
import sqlite3
import pandas as pd

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
SQL_DIR = os.path.join(BASE_DIR, "sql")
DB_DIR = os.path.join(BASE_DIR, "database")
os.makedirs(DB_DIR, exist_ok=True)

DB_PATH = os.path.join(DB_DIR, "margin_leakage.db")
SCHEMA_PATH = os.path.join(SQL_DIR, "schema.sql")

def init_database():
    print(f"📦 Connecting to SQLite database at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Execute Schema Creation
    print("📜 Executing schema definition and indexing...")
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    cursor.executescript(schema_sql)
    conn.commit()
    print("✅ Schema created successfully.")

    # 2. Ingest CSV Data into Relational Tables
    tables = [
        ("customers", "customers.csv"),
        ("products", "products.csv"),
        ("orders", "orders.csv"),
        ("order_items", "order_items.csv"),
        ("logistics", "logistics.csv"),
        ("returns", "returns.csv")
    ]

    print("\n📥 Loading CSV data into database tables...")
    for table_name, csv_file in tables:
        csv_path = os.path.join(DATA_DIR, csv_file)
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Missing file: {csv_path}. Please run 01_generate_data.py first.")
        
        df = pd.read_csv(csv_path)
        # Append data to preserve schema constraints and column types
        df.to_sql(table_name, conn, if_exists="append", index=False)
        print(f"   • Loaded {len(df):>6,} rows into '{table_name}'")

    # 3. Verify Database Integrity & Health Check
    print("\n🔍 Running Data Integrity & Sanity Check:")
    cursor.execute("SELECT count(*) FROM orders WHERE order_discount_rate > 0.20;")
    heavy_discount_orders = cursor.fetchone()[0]
    
    cursor.execute("SELECT count(*) FROM returns;")
    total_returns = cursor.fetchone()[0]

    cursor.execute("""
        SELECT ROUND(SUM(line_total_revenue), 2) AS gmv, 
               ROUND(SUM(line_total_cogs), 2) AS cogs 
        FROM order_items;
    """)
    gmv, cogs = cursor.fetchone()

    print(f"   • Total Orders with Heavy Discounts (>20%): {heavy_discount_orders:,}")
    print(f"   • Total Logged Returns: {total_returns:,}")
    print(f"   • Gross Merchandise Value (GMV): ${gmv:,.2f}")
    print(f"   • Total Cost of Goods Sold (COGS): ${cogs:,.2f}")
    print(f"   • Baseline Gross Profit: ${(gmv - cogs):,.2f} ({((gmv - cogs)/gmv)*100:.1f}%)")

    conn.close()
    print("\n🎉 Database ingestion & indexing completed successfully!")

if __name__ == "__main__":
    init_database()
