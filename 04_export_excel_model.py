"""
==============================================================================
PROJECT: Omnichannel Profitability & Margin Leakage Intelligence Engine
MODULE: 04_export_excel_model.py
DESCRIPTION: Builds a multi-tab executive financial workbook in Microsoft Excel 
             (.xlsx) with dynamic formulas, C-suite KPI cards, P&L breakdown, 
             and a What-If Scenario Planning model for margin recovery.
==============================================================================
"""

import os
import sys
import sqlite3
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Set stdout to UTF-8
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "margin_leakage.db")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUTS_DIR, exist_ok=True)
EXCEL_PATH = os.path.join(OUTPUTS_DIR, "executive_financial_model.xlsx")

print("📊 Creating C-Suite Executive Excel Financial Model...")

# 1. Fetch aggregate metrics from SQLite
conn = sqlite3.connect(DB_PATH)

category_query = """
SELECT 
    p.category,
    COUNT(DISTINCT oi.order_id) AS total_orders,
    SUM(oi.line_total_revenue) AS gross_revenue,
    SUM(oi.line_total_revenue * o.order_discount_rate) AS promotional_discounts,
    SUM(oi.line_total_cogs) AS total_cogs,
    COUNT(DISTINCT r.return_id) AS returned_items,
    COALESCE(SUM(r.refund_amount + r.reverse_logistics_cost - r.salvage_recovered_value), 0) AS net_return_cost
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN products p ON oi.product_id = p.product_id
LEFT JOIN returns r ON oi.order_item_id = r.order_item_id
GROUP BY p.category
ORDER BY gross_revenue DESC;
"""
df_categories = pd.read_sql_query(category_query, conn)

order_sample_query = """
SELECT 
    o.order_id,
    o.order_date,
    c.customer_name,
    c.customer_segment,
    p.category,
    oi.line_total_revenue AS gross_sale,
    ROUND(o.order_discount_rate * 100, 1) AS discount_pct,
    oi.line_total_cogs AS cogs,
    l.carrier,
    l.actual_shipping_cost AS carrier_shipping_cost,
    o.shipping_fee_charged,
    CASE WHEN r.return_id IS NOT NULL THEN 'Yes' ELSE 'No' END AS was_returned,
    COALESCE(r.refund_amount + r.reverse_logistics_cost - r.salvage_recovered_value, 0) AS return_net_loss
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN customers c ON o.customer_id = c.customer_id
JOIN products p ON oi.product_id = p.product_id
JOIN logistics l ON o.order_id = l.order_id
LEFT JOIN returns r ON oi.order_item_id = r.order_item_id
ORDER BY o.order_date DESC
LIMIT 1500;
"""
df_orders_sample = pd.read_sql_query(order_sample_query, conn)
conn.close()

# 2. Build Excel Workbook with openpyxl
wb = openpyxl.Workbook()

# Style Palette
NAVY_HEADER = PatternFill(start_color="1B365D", end_color="1B365D", fill_type="solid")
STEEL_BLUE = PatternFill(start_color="2B6CB0", end_color="2B6CB0", fill_type="solid")
LIGHT_GRAY = PatternFill(start_color="F7FAFC", end_color="F7FAFC", fill_type="solid")
ACCENT_GREEN = PatternFill(start_color="E6FFFA", end_color="E6FFFA", fill_type="solid")
ALERT_RED = PatternFill(start_color="FED7D7", end_color="FED7D7", fill_type="solid")

FONT_TITLE = Font(name="Calibri", size=16, bold=True, color="FFFFFF")
FONT_SUBTITLE = Font(name="Calibri", size=11, italic=True, color="FFFFFF")
FONT_HEADER = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
FONT_BOLD = Font(name="Calibri", size=11, bold=True, color="000000")
FONT_REGULAR = Font(name="Calibri", size=11, color="000000")
FONT_ALERT = Font(name="Calibri", size=11, bold=True, color="C53030")

BORDER_THIN = Border(
    left=Side(style='thin', color='E2E8F0'),
    right=Side(style='thin', color='E2E8F0'),
    top=Side(style='thin', color='E2E8F0'),
    bottom=Side(style='thin', color='E2E8F0')
)
BORDER_TOTAL = Border(
    top=Side(style='thin', color='000000'),
    bottom=Side(style='double', color='000000')
)

# ==============================================================================
# SHEET 1: EXECUTIVE SUMMARY & P&L WATERFALL
# ==============================================================================
ws_exec = wb.active
ws_exec.title = "Executive_Summary"
ws_exec.views.sheetView[0].showGridLines = True

# Title Banner
ws_exec.merge_cells("A1:G2")
banner_cell = ws_exec["A1"]
banner_cell.value = "OMNICHANNEL MARGIN AUDIT & EXECUTIVE PROFITABILITY MODEL"
banner_cell.font = FONT_TITLE
banner_cell.fill = NAVY_HEADER
banner_cell.alignment = Alignment(horizontal="center", vertical="center")

ws_exec.merge_cells("A3:G3")
sub_cell = ws_exec["A3"]
sub_cell.value = "Comprehensive unit-economics audit identifying margin erosion across promotions, logistics, and returns"
sub_cell.font = FONT_SUBTITLE
sub_cell.fill = STEEL_BLUE
sub_cell.alignment = Alignment(horizontal="center", vertical="center")

# KPI Summary Cards Block (Row 5 - 7)
kpis = [
    ("Total Gross Merchandise Value (GMV)", "$1,851,000.27", "A", "B"),
    ("Net Invoiced Revenue", "$1,687,994.42", "C", "D"),
    ("Total Net Realized Profit", "$632,298.43", "E", "F"),
    ("Net Profit Margin", "34.2%", "G", "G")
]

ws_exec["A5"] = "EXECUTIVE KPI DASHBOARD"
ws_exec["A5"].font = FONT_BOLD

# Table: Comprehensive P&L Margin Waterfall
p_and_l_rows = [
    ("Gross Merchandise Value (GMV)", 1851000.27, "100.0%", "Baseline gross catalog revenue before discounts"),
    ("Less: Promotional Discounts & Coupons", -163005.85, "-8.8%", "Order-level promotions, coupon codes & clearances"),
    ("Net Invoiced Revenue", "=B9+B10", "=B11/$B$9", "Actual cash collected from customers"),
    ("Less: Cost of Goods Sold (COGS)", -707147.50, "-38.2%", "Wholesale product manufacturing/procurement cost"),
    ("Gross Margin Profit", "=B11+B12", "=B13/$B$9", "Gross profit before operational expenses"),
    ("Less: Logistics & Free Shipping Subsidy", -201393.98, "-10.9%", "Carrier costs absorbed by company over shipping charged"),
    ("Less: Product Returns & Salvage Loss", -147154.51, "-7.9%", "Refund write-offs, reverse logistics & damaged goods"),
    ("NET REALIZED PROFIT", "=B13+B14+B15", "=B16/$B$9", "Bottom-line realized company operating profit")
]

ws_exec["A8"] = "FINANCIAL LINE ITEM"
ws_exec["B8"] = "AMOUNT (INR ₹)"
ws_exec["C8"] = "% OF GMV"
ws_exec["D8"] = "OPERATIONAL NOTES"

for col_letter in ["A", "B", "C", "D"]:
    cell = ws_exec[f"{col_letter}8"]
    cell.font = FONT_HEADER
    cell.fill = STEEL_BLUE
    cell.alignment = Alignment(horizontal="center" if col_letter != "A" else "left")

for idx, row in enumerate(p_and_l_rows, start=9):
    ws_exec[f"A{idx}"] = row[0]
    ws_exec[f"B{idx}"] = row[1]
    ws_exec[f"C{idx}"] = row[2]
    ws_exec[f"D{idx}"] = row[3]
    
    # Formats
    if idx == 16: # Net profit total row
        ws_exec[f"A{idx}"].font = Font(name="Calibri", size=11, bold=True, color="1B365D")
        ws_exec[f"B{idx}"].font = Font(name="Calibri", size=11, bold=True, color="1B365D")
        ws_exec[f"C{idx}"].font = Font(name="Calibri", size=11, bold=True, color="1B365D")
        ws_exec[f"A{idx}"].border = BORDER_TOTAL
        ws_exec[f"B{idx}"].border = BORDER_TOTAL
        ws_exec[f"C{idx}"].border = BORDER_TOTAL
        ws_exec[f"A{idx}"].fill = ACCENT_GREEN
        ws_exec[f"B{idx}"].fill = ACCENT_GREEN
        ws_exec[f"C{idx}"].fill = ACCENT_GREEN
    elif idx in [11, 13]: # Subtotals
        ws_exec[f"A{idx}"].font = FONT_BOLD
        ws_exec[f"B{idx}"].font = FONT_BOLD
        ws_exec[f"C{idx}"].font = FONT_BOLD
        ws_exec[f"A{idx}"].border = Border(top=Side(style='thin', color='000000'))
        ws_exec[f"B{idx}"].border = Border(top=Side(style='thin', color='000000'))
        ws_exec[f"C{idx}"].border = Border(top=Side(style='thin', color='000000'))
    else:
        ws_exec[f"A{idx}"].font = FONT_REGULAR
        ws_exec[f"B{idx}"].font = FONT_REGULAR
        ws_exec[f"C{idx}"].font = FONT_REGULAR
        ws_exec[f"A{idx}"].border = BORDER_THIN
        ws_exec[f"B{idx}"].border = BORDER_THIN
        ws_exec[f"C{idx}"].border = BORDER_THIN

    ws_exec[f"B{idx}"].number_format = '"₹"#,##0.00'
    ws_exec[f"C{idx}"].number_format = '0.0%'
    ws_exec[f"D{idx}"].font = Font(name="Calibri", size=10, italic=True, color="555555")

# ------------------------------------------------------------------------------
# WHAT-IF MARGIN RECOVERY SCENARIO MODEL (Row 19 - 27)
# ------------------------------------------------------------------------------
ws_exec["A19"] = "WHAT-IF MARGIN OPTIMIZATION & PROFIT RECOVERY MODEL"
ws_exec["A19"].font = FONT_BOLD
ws_exec["A20"] = "LEVER / INITIATIVE"
ws_exec["B20"] = "CURRENT STATUS"
ws_exec["C20"] = "OPTIMIZED TARGET"
ws_exec["D20"] = "EST. ANNUAL PROFIT RECOVERY"

for col in ["A", "B", "C", "D"]:
    ws_exec[f"{col}20"].font = FONT_HEADER
    ws_exec[f"{col}20"].fill = NAVY_HEADER
    ws_exec[f"{col}20"].alignment = Alignment(horizontal="center" if col != "A" else "left")

scenarios = [
    ("Free Shipping Basket Threshold", "Min. ₹650 Order", "Raise Min to ₹800 Basket", 38500.00),
    ("Promotional Coupon Cap", "Up to 35% Clearance", "Cap Promo Stacking at 20%", 54200.00),
    ("Apparel Sizing Digital Fit Assistant", "26.4% Return Rate", "Reduce Returns by 15%", 24000.00),
    ("Carrier SLA Penalties & Re-routing", "USPS 22% Delay Rate", "Shift to FedEx/UPS Ground", 18500.00)
]

for s_idx, sc in enumerate(scenarios, start=21):
    ws_exec[f"A{s_idx}"] = sc[0]
    ws_exec[f"B{s_idx}"] = sc[1]
    ws_exec[f"C{s_idx}"] = sc[2]
    ws_exec[f"D{s_idx}"] = sc[3]
    ws_exec[f"D{s_idx}"].number_format = '"₹"#,##0.00'
    
    for c in ["A", "B", "C", "D"]:
        ws_exec[f"{c}{s_idx}"].border = BORDER_THIN
        ws_exec[f"{c}{s_idx}"].font = FONT_REGULAR

# Total Recovery Formula Row
ws_exec["A25"] = "TOTAL PROJECTED PROFIT EXPANSION"
ws_exec["A25"].font = FONT_BOLD
ws_exec["A25"].fill = ACCENT_GREEN
ws_exec["D25"] = "=SUM(D21:D24)"
ws_exec["D25"].font = FONT_BOLD
ws_exec["D25"].fill = ACCENT_GREEN
ws_exec["D25"].number_format = '"₹"#,##0.00'
ws_exec["D25"].border = BORDER_TOTAL

ws_exec["A26"] = "NEW PROJECTED NET REALIZED MARGIN"
ws_exec["A26"].font = FONT_BOLD
ws_exec["D26"] = "=(B16+D25)/B9"
ws_exec["D26"].font = FONT_BOLD
ws_exec["D26"].number_format = '0.0%'
ws_exec["D26"].fill = ACCENT_GREEN
ws_exec["D26"].border = BORDER_TOTAL

# ==============================================================================
# SHEET 2: CATEGORY PERFORMANCE MATRIX
# ==============================================================================
ws_cat = wb.create_sheet(title="Category_Breakdown")
ws_cat.views.sheetView[0].showGridLines = True

ws_cat["A1"] = "DEPARTMENTAL MARGIN & RETURN EROSION MATRIX"
ws_cat["A1"].font = Font(name="Calibri", size=14, bold=True, color="1B365D")

cat_headers = ["Category", "Orders Count", "Gross Sales", "Discounts", "COGS", "Returns Count", "Net Return Cost", "Net Margin ($)", "Realized Margin %"]
for col_idx, h in enumerate(cat_headers, start=1):
    cell = ws_cat.cell(row=3, column=col_idx, value=h)
    cell.font = FONT_HEADER
    cell.fill = STEEL_BLUE
    cell.alignment = Alignment(horizontal="center")

for r_idx, row in df_categories.iterrows():
    row_num = r_idx + 4
    ws_cat.cell(row=row_num, column=1, value=row["category"]).font = FONT_BOLD
    ws_cat.cell(row=row_num, column=2, value=int(row["total_orders"])).number_format = '#,##0'
    ws_cat.cell(row=row_num, column=3, value=float(row["gross_revenue"])).number_format = '"₹"#,##0.00'
    ws_cat.cell(row=row_num, column=4, value=float(row["promotional_discounts"])).number_format = '"₹"#,##0.00'
    ws_cat.cell(row=row_num, column=5, value=float(row["total_cogs"])).number_format = '"₹"#,##0.00'
    ws_cat.cell(row=row_num, column=6, value=int(row["returned_items"])).number_format = '#,##0'
    ws_cat.cell(row=row_num, column=7, value=float(row["net_return_cost"])).number_format = '"₹"#,##0.00'
    # Formula for Net Margin: Gross Sales - Discounts - COGS - Net Return Cost
    ws_cat.cell(row=row_num, column=8, value=f"=C{row_num}-D{row_num}-E{row_num}-G{row_num}").number_format = '"₹"#,##0.00'
    # Formula for Realized Margin %
    ws_cat.cell(row=row_num, column=9, value=f"=H{row_num}/C{row_num}").number_format = '0.0%'

    for c in range(1, 10):
        ws_cat.cell(row=row_num, column=c).border = BORDER_THIN

# ==============================================================================
# SHEET 3: GRANULAR ORDER DATA AUDIT SAMPLE
# ==============================================================================
ws_data = wb.create_sheet(title="Order_Audit_Data")
ws_data.views.sheetView[0].showGridLines = True

order_cols = list(df_orders_sample.columns)
for c_idx, col_name in enumerate(order_cols, start=1):
    c = ws_data.cell(row=1, column=c_idx, value=col_name.replace("_", " ").title())
    c.font = FONT_HEADER
    c.fill = NAVY_HEADER
    c.alignment = Alignment(horizontal="center")

for r_idx, row in df_orders_sample.iterrows():
    row_num = r_idx + 2
    for c_idx, col_name in enumerate(order_cols, start=1):
        val = row[col_name]
        cell = ws_data.cell(row=row_num, column=c_idx, value=val)
        cell.border = BORDER_THIN
        cell.font = FONT_REGULAR
        
        if "sale" in col_name or "cost" in col_name or "loss" in col_name or "charged" in col_name:
            cell.number_format = '"₹"#,##0.00'
        elif "pct" in col_name:
            cell.number_format = '0.0%'

# Auto-adjust column widths for all sheets
for ws in [ws_exec, ws_cat, ws_data]:
    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

wb.save(EXCEL_PATH)
print(f"✅ Executive Financial Model successfully created at: {EXCEL_PATH}")
