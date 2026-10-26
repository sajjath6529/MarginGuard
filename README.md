# 📊 Omnichannel Profitability & Margin Leakage Intelligence Engine

> **An End-to-End Enterprise Data Analytics Project auditing ₹18.5 Lakhs (₹1.85 Cr) in Gross Merchandise Value (GMV) to uncover hidden margin erosion across promotional discounting, logistics subsidization, and product return write-offs.**

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://python.org)
[![SQL](https://img.shields.io/badge/SQL-Advanced_CTEs_%26_Window_Functions-003B57?logo=sqlite&logoColor=white)](sql/)
[![Excel](https://img.shields.io/badge/Excel-C--Suite_Financial_Model-217346?logo=microsoftexcel&logoColor=white)](outputs/executive_financial_model.xlsx)
[![Power BI](https://img.shields.io/badge/Power_BI-15_Production_DAX_Measures-F2C811?logo=powerbi&logoColor=black)](powerbi_tableau/)
[![Interactive Dashboard](https://img.shields.io/badge/Live_Dashboard-HTML5%20%2F%20Chart.js-E34F26?logo=html5&logoColor=white)](outputs/dashboard/index.html)

---

## 📌 Executive Summary

Modern e-commerce brands often chase top-line revenue while bleeding cash through unmonitored unit-economics leakage. In this project, I acted as the **Lead Data Analyst** conducting an end-to-end profitability audit of **8,500 enterprise orders** (₹18,51,000 GMV).

### 🔍 Key Financial Findings:
* **Gross Merchandise Value (GMV):** `₹18,51,000.27` across 14,647 line items.
* **Total Margin Leakage Discovered:** `-₹5,11,554.34` (27.6% of GMV evaporated before reaching operating profit).
  * 🏷️ **Promotional Discount Markdown:** `-₹1,63,005.85` (-8.8%)
  * 🚚 **Logistics Subsidization (Free Shipping):** `-₹2,01,393.98` (-10.9%)
  * 🔄 **Returns, Reverse Logistics & Scrapped Inventory:** `-₹1,47,154.51` (-7.9%)
* **Net Realized Profit:** `₹6,32,298.43` (**34.2% True Net Margin** vs. the deceptive 61.8% catalog gross margin).
* **The "Silent Bleed":** **1,075 orders (12.6%) generated negative net profit**, primarily driven by low-value carts receiving free shipping and unmonitored coupon stacking.

---

## 🏗️ Project Architecture & Data Pipeline

```
[ Raw Multi-Table Data (CSV) ]
 ├── customers.csv (1,200 records)
 ├── products.csv (40 SKUs across 5 categories)
 ├── orders.csv (8,500 orders)
 ├── order_items.csv (14,647 line items)
 ├── logistics.csv (8,500 carrier shipments)
 └── returns.csv (1,961 logged returns)
               │
               ▼
   [ 1. Python ETL & Ingestion ]
      - Data cleaning, anomaly validation, feature engineering
               │
               ▼
   [ 2. Relational SQL Database (SQLite) ]
      - Star Schema with primary/foreign keys & high-speed indexes
      - 10 Advanced Production Queries (CTEs, Window functions, RFM)
               │
       ┌───────┼─────────────────────────┐
       ▼       ▼                         ▼
[ 3. Statistical Analysis ]   [ 4. Excel Financial Model ]   [ 5. Power BI & Dashboard ]
 - Hypothesis Testing (p<0.001) - Multi-tab formatted .xlsx   - 15 Production DAX Measures
 - K-Means Customer Clustering  - Dynamic P&L Waterfall       - Interactive Live HTML5 App
 - 4 High-Res Visual Charts     - What-If Scenario Matrix     - Wireframes & Star Schema
```

---

## 🛠️ Tech Stack & Skills Demonstrated

| Tool | Technical Implementation & Deliverables |
| :--- | :--- |
| **SQL** | Relational database schema (`schema.sql`), Common Table Expressions (CTEs), Window Functions (`NTILE(4)`, `AVG() OVER()`, `SUM() OVER()`), complex multi-table joins, negative-margin audits. |
| **Python** | Core analytical programming, automated ETL pipeline, and database ingestion. |
| **Libraries** | `Pandas`, `NumPy`, `SciPy` (hypothesis testing), `Scikit-learn` (K-Means clustering), `Matplotlib`, `Seaborn`, and `openpyxl`. |
| **Microsoft Excel** | C-Suite Financial Model (`executive_financial_model.xlsx`) with custom typography, P&L Waterfall formulas (`SUMIFS`, dynamic cell linking), and a What-If Scenario Recovery table. |
| **Power BI / Tableau** | Star Schema data model, 15 enterprise DAX measures, Tableau calculated fields & LOD expressions, multi-page wireframe layout guide. |
| **Interactive Web Dashboard** | Standalone HTML5/CSS3/Chart.js web app (`outputs/dashboard/index.html`) featuring real-time sliders simulating margin recovery. |

---

## 📈 Statistical Hypotheses & Data Science Insights

### 1. Hypothesis 1: Deep Discounts Correlate with Increased Product Returns
* **Test:** Point-Biserial correlation between effective discount rate and return probability.
* **Result:** $r = 0.0856$, $p = 2.76 \times 10^{-15}$ (**Statistically Significant**).
* **Finding:** Items sold at $>35\%$ discount exhibited a **38.9% return rate**, compared to just **18.4%** for full-price merchandise. Heavy discounts trigger impulse buying with subsequent buyer remorse.

### 2. Hypothesis 2: Carrier SLA Delivery Delays Spike Return Likelihood
* **Test:** Welch's Two-Sample t-test comparing return rates between delayed and on-time shipments.
* **Result:** $t = 9.6477$, $p = 1.97 \times 10^{-21}$ (**Statistically Significant**).
* **Finding:** Delayed orders suffered a **32.8% return rate** vs. **19.2% for on-time deliveries**. Inefficient carrier routes directly increase inventory write-offs.

### 3. Machine Learning: K-Means Customer Segmentation (RFM + Margin)
Trained an unsupervised clustering model (`k=4`) based on frequency, recency, spend, discount affinity, and net margin contribution:
* **Champions (32%):** High LTV, low discount dependence, generating **₹7,820 avg margin** per customer.
* **Bargain Seekers (26%):** High order count but aggressive coupon usage, yielding only **₹3,290 avg margin**.
* **At-Risk / Dormant (9%):** High recency lag (>180 days) with low repeat activity.
* **Core Moderate Customers (33%):** Steady baseline consumer volume.

---

## 💼 Actionable Business Recommendations

1. **Raise the Free-Shipping Basket Threshold from ₹650 to ₹800:**
   * *Impact:* Eliminates 68% of negative-contribution orders, recovering **+₹38,500/year** in carrier subsidies.
2. **Cap Promotional Coupon Stacking at 20%:**
   * *Impact:* Prevents stacking cart-level coupons with already marked-down clearance items, saving **+₹54,200/year**.
3. **Apparel Sizing Digital Fit Assistant:**
   * *Impact:* Apparel returns represented the highest category write-offs (26.4%). Reducing sizing mismatches by 15% recovers **+₹24,000/year**.
4. **Logistics SLA Re-Negotiation & Carrier Re-Routing:**
   * *Impact:* Penalize carriers with delay rates $>15\%$ (USPS / Local Couriers) or re-route priority orders through FedEx/UPS Ground, capturing **+₹18,500/year**.
5. **Total Forecasted Annual Profit Expansion:** **`+₹1,35,200`** (Expands net realized margin from **34.2% &rarr; 41.5%**).

---

## 📂 Repository Directory Structure

```text
d:\data anayst\
│
├── 📁 data/                               # Enterprise relational CSV extracts
│   ├── customers.csv                      # 1,200 customer profiles & loyalty tiers
│   ├── products.csv                       # 40 SKUs across 5 product categories
│   ├── orders.csv                         # 8,500 transaction records
│   ├── order_items.csv                    # 14,647 individual line items & COGS
│   ├── logistics.csv                      # 8,500 carrier tracking & SLA logs
│   └── returns.csv                        # 1,961 return, refund & disposition records
│
├── 📁 database/
│   └── margin_leakage.db                  # Fully populated relational SQLite database
│
├── 📁 sql/
│   ├── schema.sql                         # Table definitions, constraints, indexes
│   └── analysis_queries.sql               # 10 Advanced SQL queries (CTEs, Window Functions)
│
├── 📁 python/
│   ├── 01_generate_data.py                # Reproducible synthetic data generator
│   ├── 02_load_to_sql.py                  # Ingestion pipeline & database integrity tests
│   ├── 03_eda_and_statistics.py           # Statistical hypothesis testing & K-Means clustering
│   └── 04_export_excel_model.py           # Programmatic openpyxl financial workbook generator
│
├── 📁 outputs/
│   ├── executive_financial_model.xlsx     # Formatted Excel model with P&L and What-If tabs
│   ├── 📁 charts/                         # 4 publication-ready 300 DPI analytical charts
│   │   ├── 01_margin_leakage_waterfall.png
│   │   ├── 02_discount_vs_return_rate.png
│   │   ├── 03_carrier_delay_vs_returns.png
│   │   └── 04_customer_clusters_rfm_margin.png
│   └── 📁 dashboard/
│       └── index.html                     # Live interactive web dashboard with What-If sliders
│
├── 📁 powerbi_tableau/
│   └── DAX_AND_MODEL_GUIDE.md             # Star schema diagram & 15 production DAX measures
│
└── README.md                              # Complete GitHub portfolio project documentation
```

---

## 🚀 How to Run & Reproduce

```bash
# 1. Clone or open workspace
cd "d:\data anayst"

# 2. Run data generation
python python/01_generate_data.py

# 3. Load data into SQLite relational database
python python/02_load_to_sql.py

# 4. Execute statistical EDA and generate charts
python python/03_eda_and_statistics.py

# 5. Export styled Excel Financial Model
python python/04_export_excel_model.py

# 6. Open the interactive dashboard in your browser
# Double-click 'outputs/dashboard/index.html' or serve locally:
python -m http.server 8000 -d outputs/dashboard
```

---

## 📋 Key Project Resume Bullets (Ready for your CV)

* **Engineered an end-to-end profitability analytics pipeline** using **Python (Pandas, NumPy)** and **SQL** across 14,000+ transaction line items, isolating **₹5.11 Lakhs in margin leakage** across discounting, logistics subsidies, and returns.
* **Developed 10 well-structured SQL scripts** utilizing CTEs, window functions (`NTILE`, `SUM() OVER()`, `AVG() OVER()`), and multi-table joins to audit **1,075 negative-margin orders** caused by unmonitored coupon stacking.
* **Executed statistical hypothesis testing** (Pearson correlation, Welch’s t-test) in **Python (SciPy)** showing a statistically significant link ($p < 0.001$) between $>35\%$ discount depth and a **2.1x spike in product return rates**.
* **Segmented 1,200 customers via K-Means machine learning** based on RFM and net margin contribution to identify high-LTV champions (₹7,820 avg margin) vs. margin-diluting discount seekers.
* **Constructed an executive financial model in Excel** featuring dynamic P&L waterfall calculations and a What-If scenario matrix projecting **₹1.35 Lakhs in annual profit expansion** via free-shipping threshold optimization.
* **Formulated strategic business recommendations**, including **capping stacked coupons at 20% and raising the free-shipping threshold from ₹650 to ₹800 to reduce margin leakage** and capture **₹1.35 Lakhs in annual net profit**.
* **Architected a Star Schema data model and 15 DAX measures** for **Power BI / Tableau**, paired with an interactive live HTML5 executive dashboard.
