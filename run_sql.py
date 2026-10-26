"""
==============================================================================
PROJECT: Omnichannel Profitability & Margin Leakage Intelligence Engine
MODULE: run_sql.py
DESCRIPTION: Interactive CLI runner to execute any of the 10 advanced SQL 
             queries from 'sql/analysis_queries.sql' directly against the 
             SQLite database and display tabular results in terminal.
USAGE:
    python run_sql.py 1       # Runs Query 1 (Executive Unit Economics)
    python run_sql.py 4       # Runs Query 4 (Discount Stacking Audit)
    python run_sql.py all     # Runs all 10 queries sequentially
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

# Configure pandas terminal display
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('display.max_rows', 50)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "margin_leakage.db")
SQL_FILE = os.path.join(BASE_DIR, "sql", "analysis_queries.sql")

QUERY_TITLES = {
    1: "Executive Unit Economics & Net Margin Audit",
    2: "Margin Leakage Waterfall by Product Category",
    3: "Discount Depth vs. Return Probability Correlation",
    4: "Unmonitored Discount Stacking Audit (Negative Margin Orders)",
    5: "Carrier Performance & Transit Delays vs. Return Rate",
    6: "Customer RFM & Margin Segmentation (Window Functions)",
    7: "Top 10 'Money Losing' Products (High Sales but Negative Profit)",
    8: "Free Shipping Threshold Cannibalization Audit",
    9: "Return Reasons & Salvage Write-Off Value by Category",
    10: "Rolling 30-Day Net Margin & Cumulative Profit Trend"
}

def load_queries():
    with open(SQL_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Split queries by the separator
    parts = content.split("-- QUERY ")
    queries = {}
    for part in parts[1:]:
        lines = part.strip().split("\n")
        header_line = lines[0]
        try:
            q_num = int(header_line.split(":")[0])
            # The actual query starts with WITH or SELECT
            raw_text = "\n".join(lines[1:])
            # Strip comment lines
            clean_lines = []
            start_collecting = False
            for line in raw_text.split("\n"):
                stripped = line.strip()
                if stripped.startswith("WITH ") or stripped.startswith("SELECT "):
                    start_collecting = True
                if start_collecting:
                    clean_lines.append(line)
            query_sql = "\n".join(clean_lines).strip()
            queries[q_num] = query_sql
        except Exception:
            continue
    return queries

def execute_query(q_num, queries):
    if q_num not in queries:
        print(f"❌ Error: Query {q_num} not found. Please choose between 1 and 10.")
        return

    print("\n" + "="*85)
    print(f"▶ EXECUTING QUERY {q_num}: {QUERY_TITLES.get(q_num, '')}")
    print("="*85)

    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query(queries[q_num], conn)
        if df.empty:
            print("No records returned.")
        else:
            print(df.to_string(index=False))
            print(f"\n📊 Total rows returned: {len(df)}")
    except Exception as e:
        print(f"❌ Query execution failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    queries = load_queries()
    
    if len(sys.argv) < 2:
        print("\n📖 SQL Query Runner Usage:")
        print("   python run_sql.py <query_number_1_to_10>")
        print("   python run_sql.py all\n")
        print("Available Queries:")
        for num, title in QUERY_TITLES.items():
            print(f"   [{num:>2}] {title}")
        print("\nDefaulting to Query 1:\n")
        execute_query(1, queries)
    else:
        arg = sys.argv[1].lower()
        if arg == "all":
            for num in range(1, 11):
                execute_query(num, queries)
        else:
            try:
                num = int(arg)
                execute_query(num, queries)
            except ValueError:
                print(f"❌ Invalid argument '{arg}'. Provide a number from 1 to 10 or 'all'.")
