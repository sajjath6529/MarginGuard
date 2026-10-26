"""
==============================================================================
PROJECT: Omnichannel Profitability & Margin Leakage Intelligence Engine
MODULE: 03_eda_and_statistics.py
DESCRIPTION: Performs Exploratory Data Analysis (EDA), Statistical Hypothesis 
             Testing, and K-Means Customer Clustering. Exports high-resolution 
             charts for portfolio reports and dashboards.
==============================================================================
"""

import os
import sys
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# Set stdout to UTF-8
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Setup directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "margin_leakage.db")
CHARTS_DIR = os.path.join(BASE_DIR, "outputs", "charts")
os.makedirs(CHARTS_DIR, exist_ok=True)

# Styling configuration for professional charts
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['axes.edgecolor'] = '#CCCCCC'
plt.rcParams['axes.linewidth'] = 0.8

print("🔬 Connecting to database and loading data for EDA & Modeling...")
conn = sqlite3.connect(DB_PATH)

# ==============================================================================
# 1. COMPREHENSIVE ORDER-LEVEL FINANCIAL AUDIT
# ==============================================================================
order_level_sql = """
WITH order_base AS (
    SELECT 
        o.order_id,
        o.order_date,
        o.customer_id,
        o.order_channel,
        o.payment_method,
        o.coupon_code,
        o.order_discount_rate,
        o.shipping_fee_charged,
        SUM(oi.line_total_revenue) AS gross_revenue,
        SUM(oi.line_total_cogs) AS total_cogs,
        SUM(oi.line_total_revenue * (1.0 - o.order_discount_rate)) AS net_sales,
        COUNT(oi.order_item_id) AS items_in_order,
        AVG(oi.item_discount_rate) AS avg_item_discount
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY o.order_id
),
shipping_data AS (
    SELECT 
        order_id,
        carrier,
        shipping_service,
        actual_shipping_cost,
        delivery_status,
        actual_delivery_days - estimated_delivery_days AS delay_days
    FROM logistics
),
returns_data AS (
    SELECT 
        oi.order_id,
        COUNT(r.return_id) AS returned_items_count,
        SUM(r.refund_amount) AS total_refunded,
        SUM(r.reverse_logistics_cost) AS total_reverse_shipping,
        SUM(r.salvage_recovered_value) AS total_salvage_recovered,
        SUM(r.refund_amount + r.reverse_logistics_cost - r.salvage_recovered_value) AS net_return_loss
    FROM order_items oi
    JOIN returns r ON oi.order_item_id = r.order_item_id
    GROUP BY oi.order_id
)
SELECT 
    ob.*,
    sd.carrier,
    sd.shipping_service,
    sd.actual_shipping_cost,
    sd.delivery_status,
    sd.delay_days,
    COALESCE(rd.returned_items_count, 0) AS returned_items_count,
    COALESCE(rd.total_refunded, 0) AS total_refunded,
    COALESCE(rd.total_reverse_shipping, 0) AS total_reverse_shipping,
    COALESCE(rd.net_return_loss, 0) AS net_return_loss,
    (sd.actual_shipping_cost - ob.shipping_fee_charged) AS shipping_subsidy_loss,
    (ob.net_sales - ob.total_cogs - (sd.actual_shipping_cost - ob.shipping_fee_charged) - COALESCE(rd.net_return_loss, 0)) AS net_realized_profit
FROM order_base ob
JOIN shipping_data sd ON ob.order_id = sd.order_id
LEFT JOIN returns_data rd ON ob.order_id = rd.order_id;
"""

df_orders = pd.read_sql_query(order_level_sql, conn)
df_orders["order_date"] = pd.to_datetime(df_orders["order_date"])
df_orders["effective_discount_rate"] = df_orders["order_discount_rate"] + df_orders["avg_item_discount"]
df_orders["is_returned"] = (df_orders["returned_items_count"] > 0).astype(int)

# ==============================================================================
# 2. EXECUTIVE METRICS & MARGIN LEAKAGE SUMMARY
# ==============================================================================
total_gmv = df_orders["gross_revenue"].sum()
total_cogs = df_orders["total_cogs"].sum()
total_discounts = total_gmv - df_orders["net_sales"].sum()
net_sales = df_orders["net_sales"].sum()
total_shipping_loss = df_orders["shipping_subsidy_loss"].sum()
total_return_loss = df_orders["net_return_loss"].sum()
net_profit = df_orders["net_realized_profit"].sum()
net_margin_pct = (net_profit / total_gmv) * 100
negative_profit_orders = (df_orders["net_realized_profit"] < 0).sum()

print("\n" + "="*70)
print("📊 EXECUTIVE MARGIN AUDIT & LEAKAGE SUMMARY")
print("="*70)
print(f"  • Gross Merchandise Value (GMV):   ${total_gmv:>12,.2f}  (100.0%)")
print(f"  • Promotional Discounts & Coupons:  -${total_discounts:>12,.2f}  (-{(total_discounts/total_gmv)*100:.1f}%)")
print(f"  • Net Invoiced Sales:               ${net_sales:>12,.2f}  ({(net_sales/total_gmv)*100:.1f}%)")
print(f"  • Cost of Goods Sold (COGS):       -${total_cogs:>12,.2f}  (-{(total_cogs/total_gmv)*100:.1f}%)")
print(f"  • Shipping Subsidies (Free Ship):  -${total_shipping_loss:>12,.2f}  (-{(total_shipping_loss/total_gmv)*100:.1f}%)")
print(f"  • Product Returns & Restock Loss:  -${total_return_loss:>12,.2f}  (-{(total_return_loss/total_gmv)*100:.1f}%)")
print(f"  ------------------------------------------------------------------")
print(f"  • NET REALIZED PROFIT:              ${net_profit:>12,.2f}  ({net_margin_pct:.1f}% Net Margin)")
print(f"  • Negative-Profit Orders:           {negative_profit_orders:>12,} ({negative_profit_orders/len(df_orders)*100:.1f}% of all orders)")
print("="*70)

# ==============================================================================
# 3. STATISTICAL HYPOTHESIS TESTING
# ==============================================================================
print("\n📈 Running Statistical Hypothesis Tests...")

# Hypothesis 1: Higher discounts significantly increase the probability of product returns
corr_r, p_value = stats.pointbiserialr(df_orders["effective_discount_rate"], df_orders["is_returned"])
print(f"  [H1: Discount Rate vs. Return Propensity]")
print(f"       Pearson correlation r = {corr_r:.4f}, p-value = {p_value:.4e}")
if p_value < 0.05:
    print("       ==> STATISTICALLY SIGNIFICANT: Aggressive discounting correlates with higher returns!")

# Hypothesis 2: Delivery Delays increase Return Likelihood
delayed_returns = df_orders[df_orders["delivery_status"] == "Delayed"]["is_returned"]
ontime_returns = df_orders[df_orders["delivery_status"] == "On-Time"]["is_returned"]
t_stat, t_pval = stats.ttest_ind(delayed_returns, ontime_returns, equal_var=False)
print(f"\n  [H2: Carrier Delivery Delays vs. Return Rate]")
print(f"       Delayed Orders Return Rate: {delayed_returns.mean()*100:.1f}% vs On-Time: {ontime_returns.mean()*100:.1f}%")
print(f"       Welch's t-stat = {t_stat:.4f}, p-value = {t_pval:.4e}")
if t_pval < 0.05:
    print("       ==> STATISTICALLY SIGNIFICANT: Delayed shipments experience significantly higher returns!")

# ==============================================================================
# 4. K-MEANS CUSTOMER CLUSTERING (SEGMENTATION BY MARGIN CONTRIBUTION)
# ==============================================================================
print("\n🤖 Training K-Means Machine Learning Customer Segmentation...")

cust_agg_sql = """
WITH cust_metrics AS (
    SELECT 
        c.customer_id,
        c.customer_segment,
        c.loyalty_tier,
        COUNT(DISTINCT o.order_id) AS frequency,
        JULIANDAY('2024-11-01') - JULIANDAY(MAX(o.order_date)) AS recency_days,
        SUM(oi.line_total_revenue * (1.0 - o.order_discount_rate)) AS monetary_spend,
        AVG(o.order_discount_rate + oi.item_discount_rate) AS avg_discount_affinity,
        COUNT(DISTINCT r.return_id) * 1.0 / COUNT(oi.order_item_id) AS return_ratio,
        SUM((oi.line_total_revenue * (1.0 - o.order_discount_rate)) - oi.line_total_cogs - (l.actual_shipping_cost - o.shipping_fee_charged)) AS net_customer_margin
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN logistics l ON o.order_id = l.order_id
    LEFT JOIN returns r ON oi.order_item_id = r.order_item_id
    GROUP BY c.customer_id
)
SELECT * FROM cust_metrics;
"""
df_cust = pd.read_sql_query(cust_agg_sql, conn)

features = ["frequency", "recency_days", "monetary_spend", "avg_discount_affinity", "net_customer_margin"]
X = df_cust[features].fillna(0)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
df_cust["cluster"] = kmeans.fit_predict(X_scaled)

# Map clusters to business personas based on centroids
cluster_summary = df_cust.groupby("cluster")[features].mean()
# Determine persona mapping dynamically based on margin and discount affinity
high_margin_cluster = cluster_summary["net_customer_margin"].idxmax()
bargain_cluster = cluster_summary["avg_discount_affinity"].idxmax()
churn_risk_cluster = cluster_summary["recency_days"].idxmax()
# Remaining cluster
remaining = set(range(4)) - {high_margin_cluster, bargain_cluster, churn_risk_cluster}
core_cluster = list(remaining)[0] if remaining else 0

cluster_names = {
    high_margin_cluster: "Champions (High Margin & LTV)",
    bargain_cluster: "Bargain Seekers (High Discount, Low Margin)",
    churn_risk_cluster: "At-Risk / Dormant Buyers",
    core_cluster: "Core Moderate Customers"
}
df_cust["persona"] = df_cust["cluster"].map(cluster_names)

print("\n  Customer Personas Breakdown:")
for persona, grp in df_cust.groupby("persona"):
    print(f"   • {persona:<42} | Size: {len(grp):>4} | Avg Margin: ${grp['net_customer_margin'].mean():>7.2f} | Avg Spend: ${grp['monetary_spend'].mean():>8.2f}")

# ==============================================================================
# 5. GENERATE & EXPORT VISUAL CHARTS
# ==============================================================================
print("\n📊 Generating executive visual charts...")

# --- CHART 1: MARGIN LEAKAGE WATERFALL ---
plt.figure(figsize=(10, 6))
waterfall_stages = ["Gross GMV", "Discounts", "Net Sales", "COGS", "Shipping Loss", "Return Write-Offs", "Net Profit"]
waterfall_values = [total_gmv, -total_discounts, net_sales, -total_cogs, -total_shipping_loss, -total_return_loss, net_profit]
colors = ["#2B6CB0", "#E53E3E", "#3182CE", "#E53E3E", "#DD6B20", "#C53030", "#38A169"]

bars = plt.bar(waterfall_stages, [abs(v) for v in waterfall_values], color=colors, width=0.6, edgecolor="#333333", linewidth=0.8)
plt.title("Financial Margin Leakage Waterfall (Gross GMV to Net Profit)", fontsize=14, fontweight="bold", pad=15)
plt.ylabel("Amount in INR (₹)", fontsize=11, fontweight="bold")
plt.xticks(rotation=25, ha="right", fontsize=10)

# Annotate values on top of bars
for bar, val in zip(bars, waterfall_values):
    prefix = "+" if val > 0 else "-"
    if bar.get_x() in [0, 2, 6]:
        label = f"₹{abs(val)/1e6:.2f}M"
    else:
        label = f"-₹{abs(val)/1e3:.1f}k"
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 18000, label, ha="center", va="bottom", fontsize=9, fontweight="bold")

plt.tight_layout()
chart1_path = os.path.join(CHARTS_DIR, "01_margin_leakage_waterfall.png")
plt.savefig(chart1_path, dpi=300)
plt.close()
print(f"  ✅ Saved: {chart1_path}")

# --- CHART 2: DISCOUNT DEPTH VS RETURN RATE ---
plt.figure(figsize=(9, 5.5))
df_orders["discount_bin"] = pd.cut(
    df_orders["effective_discount_rate"], 
    bins=[-0.01, 0.0, 0.10, 0.20, 0.30, 0.50, 1.0], 
    labels=["Full Price", "1-10%", "11-20%", "21-30%", "31-50%", ">50%"]
)
bin_returns = df_orders.groupby("discount_bin", observed=False)["is_returned"].mean() * 100

ax = sns.barplot(x=bin_returns.index, y=bin_returns.values, palette="Reds_d")
plt.title("Product Return Rate by Promotional Discount Depth", fontsize=13, fontweight="bold", pad=15)
plt.xlabel("Discount Bracket", fontsize=11, fontweight="bold")
plt.ylabel("Return Rate (%)", fontsize=11, fontweight="bold")

for p in ax.patches:
    ax.annotate(f"{p.get_height():.1f}%", (p.get_x() + p.get_width() / 2., p.get_height()),
                ha='center', va='center', xytext=(0, 7), textcoords='offset points', fontweight='bold', fontsize=10)

plt.tight_layout()
chart2_path = os.path.join(CHARTS_DIR, "02_discount_vs_return_rate.png")
plt.savefig(chart2_path, dpi=300)
plt.close()
print(f"  ✅ Saved: {chart2_path}")

# --- CHART 3: CARRIER TRANSIT DELAYS VS RETURN RATES ---
plt.figure(figsize=(9, 5))
carrier_stats = df_orders.groupby("carrier").agg(
    delay_rate=("delivery_status", lambda x: (x == "Delayed").mean() * 100),
    return_rate=("is_returned", lambda x: x.mean() * 100)
).reset_index()

ax = sns.scatterplot(data=carrier_stats, x="delay_rate", y="return_rate", s=250, hue="carrier", palette="Set2")
for i in range(carrier_stats.shape[0]):
    plt.text(carrier_stats.delay_rate[i] + 0.3, carrier_stats.return_rate[i], carrier_stats.carrier[i], 
             fontweight="bold", fontsize=10, va="center")

plt.title("Carrier Delay Rate vs. Order Return Rate", fontsize=13, fontweight="bold", pad=15)
plt.xlabel("Carrier SLA Delay Rate (%)", fontsize=11, fontweight="bold")
plt.ylabel("Order Return Rate (%)", fontsize=11, fontweight="bold")
plt.legend([],[], frameon=False)
plt.tight_layout()
chart3_path = os.path.join(CHARTS_DIR, "03_carrier_delay_vs_returns.png")
plt.savefig(chart3_path, dpi=300)
plt.close()
print(f"  ✅ Saved: {chart3_path}")

# --- CHART 4: K-MEANS CUSTOMER CLUSTERING (SPEND VS NET MARGIN) ---
plt.figure(figsize=(10, 6))
sns.scatterplot(
    data=df_cust, 
    x="monetary_spend", 
    y="net_customer_margin", 
    hue="persona", 
    palette="Dark2", 
    s=50, 
    alpha=0.85
)
plt.axhline(0, color="#E53E3E", linestyle="--", linewidth=1.2, label="Break-Even (Zero Margin)")
plt.title("Customer Value Segmentation: Spend vs. Realized Net Margin", fontsize=13, fontweight="bold", pad=15)
plt.xlabel("Total Customer Spend (₹)", fontsize=11, fontweight="bold")
plt.ylabel("Net Profit Contribution (₹)", fontsize=11, fontweight="bold")
plt.legend(title="Customer Persona", frameon=True, loc="upper left")
plt.tight_layout()
chart4_path = os.path.join(CHARTS_DIR, "04_customer_clusters_rfm_margin.png")
plt.savefig(chart4_path, dpi=300)
plt.close()
print(f"  ✅ Saved: {chart4_path}")

conn.close()
print("🎉 Exploratory Analysis, Statistical Tests & Visual Exports Complete!")
