-- ==============================================================================
-- PROJECT: Omnichannel Profitability & Margin Leakage Intelligence Engine
-- SCRIPT: 10 Advanced Analytical SQL Queries for Executive Decision Making
-- SKILLS: CTEs, Window Functions (OVER, PARTITION BY, NTILE, LAG), Aggregations
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- QUERY 1: EXECUTIVE UNIT ECONOMICS & NET MARGIN AUDIT
-- Business Question: What is our TRUE Net Margin after factoring in wholesale 
-- cost (COGS), promotional discounts, carrier shipping losses, and return write-offs?
-- ------------------------------------------------------------------------------
WITH order_economics AS (
    SELECT 
        o.order_id,
        o.order_discount_rate,
        o.shipping_fee_charged,
        SUM(oi.line_total_revenue) AS gross_merchandise_value,
        SUM(oi.line_total_cogs) AS total_cogs,
        -- Net Revenue after cart-level discount
        SUM(oi.line_total_revenue) * (1.0 - o.order_discount_rate) AS net_order_revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY o.order_id, o.order_discount_rate, o.shipping_fee_charged
),
logistics_costs AS (
    SELECT 
        order_id,
        SUM(actual_shipping_cost) AS total_carrier_cost
    FROM logistics
    GROUP BY order_id
),
return_losses AS (
    SELECT 
        oi.order_id,
        SUM(r.refund_amount + r.reverse_logistics_cost - r.salvage_recovered_value) AS net_return_cost
    FROM returns r
    JOIN order_items oi ON r.order_item_id = oi.order_item_id
    GROUP BY oi.order_id
)
SELECT 
    ROUND(SUM(oe.gross_merchandise_value), 2) AS total_gmv,
    ROUND(SUM(oe.gross_merchandise_value - oe.net_order_revenue), 2) AS total_promotional_markowns,
    ROUND(SUM(oe.net_order_revenue), 2) AS net_invoiced_revenue,
    ROUND(SUM(oe.total_cogs), 2) AS total_product_cogs,
    ROUND(SUM(lc.total_carrier_cost - oe.shipping_fee_charged), 2) AS net_carrier_shipping_loss,
    ROUND(COALESCE(SUM(rl.net_return_cost), 0), 2) AS total_return_losses,
    ROUND(
        SUM(oe.net_order_revenue) - SUM(oe.total_cogs) 
        - SUM(lc.total_carrier_cost - oe.shipping_fee_charged) 
        - COALESCE(SUM(rl.net_return_cost), 0)
    , 2) AS net_realized_profit,
    ROUND(
        (SUM(oe.net_order_revenue) - SUM(oe.total_cogs) 
         - SUM(lc.total_carrier_cost - oe.shipping_fee_charged) 
         - COALESCE(SUM(rl.net_return_cost), 0)) 
        / SUM(oe.gross_merchandise_value) * 100
    , 2) AS net_realized_margin_pct
FROM order_economics oe
LEFT JOIN logistics_costs lc ON oe.order_id = lc.order_id
LEFT JOIN return_losses rl ON oe.order_id = rl.order_id;


-- ------------------------------------------------------------------------------
-- QUERY 2: MARGIN LEAKAGE WATERFALL BY PRODUCT CATEGORY
-- Business Question: Which departments bleed the most margin between gross sales 
-- and bottom-line profit?
-- ------------------------------------------------------------------------------
WITH category_metrics AS (
    SELECT 
        p.category,
        COUNT(DISTINCT oi.order_id) AS total_orders,
        SUM(oi.line_total_revenue) AS gross_revenue,
        SUM(oi.line_total_cogs) AS total_cogs,
        SUM(oi.line_total_revenue * oi.item_discount_rate) AS item_markdown_loss,
        SUM(oi.line_total_revenue - oi.line_total_cogs) AS gross_profit,
        COALESCE(SUM(r.refund_amount + r.reverse_logistics_cost - r.salvage_recovered_value), 0) AS return_erosion
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    LEFT JOIN returns r ON oi.order_item_id = r.order_item_id
    GROUP BY p.category
)
SELECT 
    category,
    ROUND(gross_revenue, 2) AS gross_revenue,
    ROUND(total_cogs, 2) AS cogs,
    ROUND(gross_profit, 2) AS gross_profit,
    ROUND((gross_profit / gross_revenue) * 100, 2) AS gross_margin_pct,
    ROUND(return_erosion, 2) AS return_erosion,
    ROUND(gross_profit - return_erosion, 2) AS operating_contribution,
    ROUND(((gross_profit - return_erosion) / gross_revenue) * 100, 2) AS realized_margin_pct
FROM category_metrics
ORDER BY realized_margin_pct ASC;


-- ------------------------------------------------------------------------------
-- QUERY 3: DISCOUNT DEPTH VS. RETURN PROBABILITY CORRELATION
-- Business Question: Does heavy discounting attract buyers with higher propensity 
-- to return products?
-- ------------------------------------------------------------------------------
WITH discount_brackets AS (
    SELECT 
        oi.order_item_id,
        oi.line_total_revenue,
        CASE 
            WHEN (oi.item_discount_rate + o.order_discount_rate) = 0 THEN '0% (Full Price)'
            WHEN (oi.item_discount_rate + o.order_discount_rate) <= 0.10 THEN '1% - 10% Discount'
            WHEN (oi.item_discount_rate + o.order_discount_rate) <= 0.20 THEN '11% - 20% Discount'
            WHEN (oi.item_discount_rate + o.order_discount_rate) <= 0.35 THEN '21% - 35% Discount'
            ELSE '> 35% Heavy Clearance'
        END AS discount_tier,
        CASE WHEN r.return_id IS NOT NULL THEN 1 ELSE 0 END AS is_returned
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    LEFT JOIN returns r ON oi.order_item_id = r.order_item_id
)
SELECT 
    discount_tier,
    COUNT(*) AS total_items_sold,
    SUM(is_returned) AS total_items_returned,
    ROUND((CAST(SUM(is_returned) AS FLOAT) / COUNT(*)) * 100, 2) AS return_rate_pct,
    ROUND(SUM(line_total_revenue), 2) AS total_revenue_in_tier
FROM discount_brackets
GROUP BY discount_tier
ORDER BY return_rate_pct DESC;


-- ------------------------------------------------------------------------------
-- QUERY 4: UNMONITORED DISCOUNT STACKING AUDIT (NEGATIVE MARGIN ORDERS)
-- Business Question: Which orders yielded negative net profit due to stacked promotions?
-- ------------------------------------------------------------------------------
WITH order_margin_check AS (
    SELECT 
        o.order_id,
        o.order_date,
        c.customer_name,
        c.customer_segment,
        o.coupon_code,
        o.order_discount_rate,
        SUM(oi.line_total_revenue * (1.0 - o.order_discount_rate)) AS final_sale_price,
        SUM(oi.line_total_cogs) AS total_cogs,
        l.actual_shipping_cost - o.shipping_fee_charged AS net_shipping_subsidy,
        (
            SUM(oi.line_total_revenue * (1.0 - o.order_discount_rate)) 
            - SUM(oi.line_total_cogs) 
            - (l.actual_shipping_cost - o.shipping_fee_charged)
        ) AS order_net_margin
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN logistics l ON o.order_id = l.order_id
    GROUP BY o.order_id, o.order_date, c.customer_name, c.customer_segment, o.coupon_code, o.order_discount_rate, l.actual_shipping_cost, o.shipping_fee_charged
)
SELECT 
    order_id,
    order_date,
    customer_name,
    customer_segment,
    coupon_code,
    ROUND(order_discount_rate * 100, 1) || '%' AS cart_discount,
    ROUND(final_sale_price, 2) AS final_sale_price,
    ROUND(total_cogs, 2) AS total_cogs,
    ROUND(net_shipping_subsidy, 2) AS shipping_subsidy,
    ROUND(order_net_margin, 2) AS net_margin_dollars
FROM order_margin_check
WHERE order_net_margin < 0
ORDER BY order_net_margin ASC
LIMIT 15;


-- ------------------------------------------------------------------------------
-- QUERY 5: CARRIER PERFORMANCE & TRANSIT DELAYS VS. RETURN RATE
-- Business Question: Are specific logistics carriers causing customer returns 
-- due to missed delivery SLAs?
-- ------------------------------------------------------------------------------
SELECT 
    l.carrier,
    l.shipping_service,
    COUNT(DISTINCT l.order_id) AS total_shipments,
    ROUND(AVG(l.actual_delivery_days), 1) AS avg_delivery_days,
    ROUND(AVG(l.actual_delivery_days - l.estimated_delivery_days), 1) AS avg_days_delayed,
    ROUND(
        SUM(CASE WHEN l.delivery_status = 'Delayed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 
        2
    ) AS delay_rate_pct,
    ROUND(
        COUNT(DISTINCT r.return_id) * 100.0 / COUNT(DISTINCT l.order_id), 
        2
    ) AS order_return_rate_pct,
    ROUND(SUM(l.actual_shipping_cost), 2) AS total_carrier_spend
FROM logistics l
JOIN order_items oi ON l.order_id = oi.order_id
LEFT JOIN returns r ON oi.order_item_id = r.order_item_id
GROUP BY l.carrier, l.shipping_service
HAVING COUNT(DISTINCT l.order_id) > 50
ORDER BY delay_rate_pct DESC;


-- ------------------------------------------------------------------------------
-- QUERY 6: CUSTOMER RFM & MARGIN SEGMENTATION (WINDOW FUNCTIONS)
-- Business Question: Who are our top profitable customers vs bargain hunters 
-- who drain our margins?
-- ------------------------------------------------------------------------------
WITH customer_aggregates AS (
    SELECT 
        c.customer_id,
        c.customer_name,
        c.customer_segment,
        MAX(o.order_date) AS last_order_date,
        COUNT(DISTINCT o.order_id) AS order_frequency,
        SUM(oi.line_total_revenue * (1.0 - o.order_discount_rate)) AS total_spend,
        SUM(
            (oi.line_total_revenue * (1.0 - o.order_discount_rate)) 
            - oi.line_total_cogs
        ) AS customer_gross_margin
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY c.customer_id, c.customer_name, c.customer_segment
),
rfm_scores AS (
    SELECT 
        customer_id,
        customer_name,
        customer_segment,
        order_frequency,
        ROUND(total_spend, 2) AS total_spend,
        ROUND(customer_gross_margin, 2) AS customer_gross_margin,
        NTILE(4) OVER (ORDER BY order_frequency DESC) AS frequency_score,
        NTILE(4) OVER (ORDER BY total_spend DESC) AS monetary_score,
        NTILE(4) OVER (ORDER BY customer_gross_margin DESC) AS margin_score
    FROM customer_aggregates
)
SELECT 
    customer_id,
    customer_name,
    customer_segment,
    order_frequency,
    total_spend,
    customer_gross_margin,
    (frequency_score + monetary_score + margin_score) AS composite_value_score,
    CASE 
        WHEN margin_score = 4 AND frequency_score >= 3 THEN 'Tier 1: High-Margin Champion'
        WHEN monetary_score = 4 AND margin_score <= 2 THEN 'Tier 2: High-Spend Bargain Hunter (Low Margin)'
        WHEN frequency_score <= 2 AND monetary_score <= 2 THEN 'Tier 3: Low-Engagement Buyer'
        ELSE 'Tier 4: Core Moderate Customer'
    END AS customer_strategic_tier
FROM rfm_scores
ORDER BY composite_value_score DESC
LIMIT 20;


-- ------------------------------------------------------------------------------
-- QUERY 7: TOP 10 "MONEY LOSING" PRODUCTS (HIGH REVENUE BUT NEGATIVE PROFIT)
-- Business Question: Which products look like best-sellers on paper, but are 
-- actually draining net company profits?
-- ------------------------------------------------------------------------------
WITH product_financials AS (
    SELECT 
        p.product_id,
        p.product_name,
        p.category,
        p.cost_price,
        p.base_retail_price,
        SUM(oi.quantity) AS units_sold,
        SUM(oi.line_total_revenue) AS gross_sales,
        SUM(oi.line_total_cogs) AS total_cogs,
        COALESCE(SUM(r.refund_amount + r.reverse_logistics_cost - r.salvage_recovered_value), 0) AS total_return_cost,
        COUNT(DISTINCT r.return_id) * 1.0 / NULLIF(SUM(oi.quantity), 0) AS return_ratio
    FROM products p
    JOIN order_items oi ON p.product_id = oi.product_id
    LEFT JOIN returns r ON oi.order_item_id = r.order_item_id
    GROUP BY p.product_id, p.product_name, p.category, p.cost_price, p.base_retail_price
)
SELECT 
    product_name,
    category,
    units_sold,
    ROUND(gross_sales, 2) AS gross_sales,
    ROUND(total_cogs, 2) AS total_cogs,
    ROUND(total_return_cost, 2) AS return_cost_impact,
    ROUND(gross_sales - total_cogs - total_return_cost, 2) AS net_product_profit,
    ROUND(((gross_sales - total_cogs - total_return_cost) / gross_sales) * 100, 2) AS net_product_margin_pct
FROM product_financials
WHERE gross_sales > 1500
ORDER BY net_product_profit ASC
LIMIT 10;


-- ------------------------------------------------------------------------------
-- QUERY 8: FREE SHIPPING THRESHOLD CANNIBALIZATION AUDIT
-- Business Question: Are low-value orders being offered free shipping that wipes 
-- out the basket gross margin?
-- ------------------------------------------------------------------------------
WITH basket_shipping_audit AS (
    SELECT 
        o.order_id,
        o.shipping_fee_charged,
        SUM(oi.line_total_revenue * (1.0 - o.order_discount_rate)) AS cart_value,
        SUM(oi.line_total_cogs) AS cart_cogs,
        l.actual_shipping_cost,
        (SUM(oi.line_total_revenue * (1.0 - o.order_discount_rate)) - SUM(oi.line_total_cogs)) AS cart_gross_margin
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN logistics l ON o.order_id = l.order_id
    GROUP BY o.order_id, o.shipping_fee_charged, l.actual_shipping_cost
)
SELECT 
    CASE 
        WHEN cart_value < 350 THEN 'Under ₹350 Basket'
        WHEN cart_value < 500 THEN '₹350 - ₹499.99 Basket'
        WHEN cart_value < 750 THEN '₹500 - ₹749.99 Basket'
        WHEN cart_value < 1000 THEN '₹750 - ₹999.99 Basket'
        ELSE '₹1,000+ High Value Basket'
    END AS basket_size_bracket,
    COUNT(*) AS total_orders,
    SUM(CASE WHEN shipping_fee_charged = 0 THEN 1 ELSE 0 END) AS free_shipping_orders_granted,
    ROUND(AVG(cart_value), 2) AS avg_cart_value,
    ROUND(AVG(actual_shipping_cost), 2) AS avg_carrier_cost,
    ROUND(AVG(cart_gross_margin - (actual_shipping_cost - shipping_fee_charged)), 2) AS avg_net_contribution,
    SUM(CASE WHEN (cart_gross_margin - (actual_shipping_cost - shipping_fee_charged)) < 0 THEN 1 ELSE 0 END) AS negative_margin_orders
FROM basket_shipping_audit
GROUP BY basket_size_bracket
ORDER BY avg_cart_value ASC;


-- ------------------------------------------------------------------------------
-- QUERY 9: RETURN REASONS & SALVAGE WRITE-OFF VALUE BY CATEGORY
-- Business Question: What are the root causes of returns, and how much inventory 
-- value is unrecoverable (scrapped/liquidated)?
-- ------------------------------------------------------------------------------
SELECT 
    p.category,
    r.return_reason,
    COUNT(r.return_id) AS total_returns,
    ROUND(SUM(r.refund_amount), 2) AS total_refunded_to_customers,
    ROUND(SUM(r.reverse_logistics_cost), 2) AS reverse_shipping_expenses,
    ROUND(SUM(r.salvage_recovered_value), 2) AS salvage_value_recovered,
    ROUND(SUM(r.refund_amount + r.reverse_logistics_cost - r.salvage_recovered_value), 2) AS net_company_loss,
    ROUND(
        SUM(CASE WHEN r.item_disposition = 'Scrapped' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 
        1
    ) AS scrapped_rate_pct
FROM returns r
JOIN order_items oi ON r.order_item_id = oi.order_item_id
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.category, r.return_reason
ORDER BY net_company_loss DESC;


-- ------------------------------------------------------------------------------
-- QUERY 10: ROLLING 30-DAY NET MARGIN & CUMULATIVE PROFIT TREND
-- Business Question: What is the day-over-day financial trajectory of net profit 
-- using moving window averages?
-- ------------------------------------------------------------------------------
WITH daily_financials AS (
    SELECT 
        DATE(o.order_date) AS order_day,
        COUNT(DISTINCT o.order_id) AS orders_count,
        SUM(oi.line_total_revenue * (1.0 - o.order_discount_rate)) AS daily_net_sales,
        SUM(oi.line_total_cogs) AS daily_cogs,
        SUM(l.actual_shipping_cost - o.shipping_fee_charged) AS daily_shipping_loss
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN logistics l ON o.order_id = l.order_id
    GROUP BY DATE(o.order_date)
)
SELECT 
    order_day,
    orders_count,
    ROUND(daily_net_sales, 2) AS daily_net_sales,
    ROUND(daily_net_sales - daily_cogs - daily_shipping_loss, 2) AS daily_net_profit,
    -- 7-Day Moving Average of Net Profit
    ROUND(
        AVG(daily_net_sales - daily_cogs - daily_shipping_loss) OVER (
            ORDER BY order_day 
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ), 
        2
    ) AS rolling_7day_avg_profit,
    -- Cumulative Total Profit over time
    ROUND(
        SUM(daily_net_sales - daily_cogs - daily_shipping_loss) OVER (
            ORDER BY order_day
        ), 
        2
    ) AS cumulative_profit_to_date
FROM daily_financials
ORDER BY order_day ASC
LIMIT 30;
