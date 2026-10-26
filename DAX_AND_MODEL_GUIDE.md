# Power BI & Tableau Implementation Blueprint: Margin Leakage Intelligence

This guide provides the complete **Data Modeling Architecture, DAX Formulas, and Visual Wireframes** needed to build the Executive Dashboard in **Power BI Desktop** or **Tableau Desktop**.

---

## 1. Data Model Architecture (Star Schema)

Import the CSV files or connect directly to the SQLite database `database/margin_leakage.db`.

```
          ┌─────────────────────┐
          │    dim_customers    │
          │─────────────────────│
          │ customer_id (PK)    │
          │ customer_name       │
          │ customer_segment    │
          │ region              │
          │ loyalty_tier        │
          └──────────┬──────────┘
                     │ 1
                     │
                     │ *
┌────────────────────┴────────────────────┐          ┌─────────────────────┐
│               fact_orders               │          │    dim_products     │
│─────────────────────────────────────────│          │─────────────────────│
│ order_id (PK)                           │          │ product_id (PK)     │
│ customer_id (FK) ◄──────────────────────┘          │ product_name        │
│ order_date                              │          │ category            │
│ order_discount_rate                     │          │ sub_category        │
│ shipping_fee_charged                    │          │ cost_price          │
│ order_status                            │          │ base_retail_price   │
└──────────┬──────────────────────┬───────┘          └──────────┬──────────┘
           │ 1                    │ 1                           │ 1
           │                      │                             │
           │ *                    │ 1                           │ *
┌──────────┴───────────────┐  ┌───┴───────────────────────┐ ┌───┴───────────────────────┐
│     fact_order_items     │  │      fact_logistics       │ │      fact_returns         │
│──────────────────────────│  │───────────────────────────│ │───────────────────────────│
│ order_item_id (PK)       │  │ shipment_id (PK)          │ │ return_id (PK)            │
│ order_id (FK)            │  │ order_id (FK)             │ │ order_item_id (FK)        │
│ product_id (FK) ─────────┼──┘ actual_shipping_cost      │ │ return_reason             │
│ quantity                 │  │ estimated_delivery_days   │ │ refund_amount             │
│ line_total_revenue       │  │ actual_delivery_days      │ │ reverse_logistics_cost    │
│ line_total_cogs          │  │ delivery_status           │ │ salvage_recovered_value   │
│ item_discount_rate       │  │ carrier                   │ │ item_disposition          │
└──────────────────────────┘  └───────────────────────────┘ └───────────────────────────┘
```

---

## 2. 15 Production DAX Measures (Power BI)

Create a dedicated measure table called `_Measures` and add the following DAX calculations:

### 1. Gross Merchandise Value (GMV)
```dax
Total GMV = SUM(fact_order_items[line_total_revenue])
```

### 2. Promotional Markdowns
```dax
Promotional Discounts = 
SUMX(
    fact_orders,
    CALCULATE(SUM(fact_order_items[line_total_revenue])) * fact_orders[order_discount_rate]
)
```

### 3. Net Invoiced Sales
```dax
Net Invoiced Sales = [Total GMV] - [Promotional Discounts]
```

### 4. Cost of Goods Sold (COGS)
```dax
Total COGS = SUM(fact_order_items[line_total_cogs])
```

### 5. Gross Profit & Margin
```dax
Gross Profit = [Net Invoiced Sales] - [Total COGS]

Gross Margin % = DIVIDE([Gross Profit], [Net Invoiced Sales], 0)
```

### 6. Carrier Shipping Subsidy Loss
```dax
Carrier Shipping Subsidy = 
SUMX(
    fact_orders,
    RELATED(fact_logistics[actual_shipping_cost]) - fact_orders[shipping_fee_charged]
)
```

### 7. Net Return Loss Write-Off
```dax
Net Return Loss = 
SUMX(
    fact_returns,
    fact_returns[refund_amount] + fact_returns[reverse_logistics_cost] - fact_returns[salvage_recovered_value]
)
```

### 8. Net Realized Profit (The North Star Metric)
```dax
Net Realized Profit = 
[Gross Profit] - [Carrier Shipping Subsidy] - [Net Return Loss]
```

### 9. Net Realized Margin %
```dax
Net Realized Margin % = DIVIDE([Net Realized Profit], [Total GMV], 0)
```

### 10. Margin Leakage Value
```dax
Total Margin Leakage = [Promotional Discounts] + [Carrier Shipping Subsidy] + [Net Return Loss]
```

### 11. Negative Margin Order Count
```dax
Negative Margin Orders = 
COUNTROWS(
    FILTER(
        fact_orders,
        [Net Realized Profit] < 0
    )
)
```

### 12. Negative Order Leakage Ratio %
```dax
Negative Order % = DIVIDE([Negative Margin Orders], COUNTROWS(fact_orders), 0)
```

### 13. Return Rate %
```dax
Return Rate % = 
DIVIDE(
    DISTINCTCOUNT(fact_returns[return_id]),
    COUNTROWS(fact_order_items),
    0
)
```

### 14. Carrier SLA Delay Rate %
```dax
Carrier Delay Rate % = 
DIVIDE(
    CALCULATE(COUNTROWS(fact_logistics), fact_logistics[delivery_status] = "Delayed"),
    COUNTROWS(fact_logistics),
    0
)
```

### 15. Dynamic Scenario Profit Recovery ($)
```dax
Scenario Recovered Profit = 
-- Simulates raising shipping threshold and capping discounts at 20%
VAR ShippingSavings = [Carrier Shipping Subsidy] * 0.18
VAR PromoCapSavings = [Promotional Discounts] * 0.25
RETURN
ShippingSavings + PromoCapSavings
```

---

## 3. Tableau Calculated Fields (Equivalent)

If using **Tableau**, paste these calculated fields:

1. **`[Net Sales]`**:  
   `SUM([Line Total Revenue]) * (1 - ATTR([Order Discount Rate]))`
2. **`[COGS]`**:  
   `SUM([Line Total Cogs])`
3. **`[Shipping Subsidy]`**:  
   `SUM([Actual Shipping Cost]) - SUM([Shipping Fee Charged])`
4. **`[Return Loss]`**:  
   `ZN(SUM([Refund Amount])) + ZN(SUM([Reverse Logistics Cost])) - ZN(SUM([Salvage Recovered Value]))`
5. **`[Net Realized Profit]`**:  
   `[Net Sales] - [COGS] - [Shipping Subsidy] - [Return Loss]`
6. **`[Customer Margin (LOD)]`**:  
   `{ FIXED [Customer Id] : [Net Realized Profit] }`

---

## 4. Visual Dashboard Layout & Wireframe

### Page 1: Executive Margin Command Center
* **Top Banner:** 4 Primary KPI Cards:
  * `Total GMV` ($1.85M)
  * `Net Invoiced Sales` ($1.69M)
  * `Net Realized Profit` ($632.3K)
  * `Realized Net Margin %` (34.2%)
* **Center Left:** **Margin Leakage Waterfall Chart** (GMV ➔ Discounts ➔ COGS ➔ Shipping Loss ➔ Return Write-Offs ➔ Net Profit).
* **Center Right:** **Monthly Profit & Leakage Trend Line** (Invoiced Sales vs Net Realized Profit with 7-day moving average).
* **Bottom Left:** **Channel & Segment Performance Matrix** (Consumer vs Corporate vs Small Business).
* **Bottom Right:** **Negative Margin Order Alert Box** (Highlights orders where net profit < $0).

### Page 2: Return Propensity & Promo Sensitivity
* **Top Left:** **Discount Depth vs. Return Rate Bar Chart** (Shows jump from 19% return rate at full price to 38% at 35%+ discount).
* **Top Right:** **Category Return Loss Heatmap** (Apparel & Electronics return erosion breakdown).
* **Bottom:** **Detailed Product SKU Margin Leakage Table** with conditional red formatting for products with negative net margins.

### Page 3: Carrier Logistics & SLA Scorecard
* **Scatter Plot:** Carrier SLA Delay Rate (%) vs. Order Return Rate (%).
* **Carrier Spend Breakdown Bar Chart:** FedEx vs UPS vs DHL vs USPS (Comparing cost per unit and on-time reliability).
* **Free Shipping Basket Size Distribution Histogram.**
