-- ==============================================================================
-- PROJECT: Omnichannel Profitability & Margin Leakage Intelligence Engine
-- SCRIPT: Database Schema & Relational Constraints
-- DIALECT: SQLite / PostgreSQL Compatible
-- ==============================================================================

-- Enable Foreign Key Enforcement (SQLite)
PRAGMA foreign_keys = ON;

-- 1. CUSTOMERS TABLE (Dimension)
DROP TABLE IF EXISTS customers;
CREATE TABLE customers (
    customer_id VARCHAR(20) PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    customer_segment VARCHAR(50) NOT NULL,       -- Consumer, Corporate, Small Business
    region VARCHAR(50) NOT NULL,                 -- North, South, East, West, Central
    acquisition_channel VARCHAR(50) NOT NULL,    -- Paid Search, Organic, Affiliate, Social, Direct
    signup_date DATE NOT NULL,
    loyalty_tier VARCHAR(20) DEFAULT 'Standard'  -- Standard, Silver, Gold, Platinum
);

-- 2. PRODUCTS TABLE (Dimension)
DROP TABLE IF EXISTS products;
CREATE TABLE products (
    product_id VARCHAR(20) PRIMARY KEY,
    product_name VARCHAR(150) NOT NULL,
    category VARCHAR(50) NOT NULL,               -- Electronics, Apparel, Home & Kitchen, Office, Beauty
    sub_category VARCHAR(50) NOT NULL,
    cost_price DECIMAL(10, 2) NOT NULL,          -- Base wholesale cost to company
    base_retail_price DECIMAL(10, 2) NOT NULL,   -- Standard list price
    weight_kg DECIMAL(6, 2) NOT NULL             -- Physical weight affecting shipping fees
);

-- 3. ORDERS TABLE (Fact Table)
DROP TABLE IF EXISTS orders;
CREATE TABLE orders (
    order_id VARCHAR(25) PRIMARY KEY,
    order_date TIMESTAMP NOT NULL,
    customer_id VARCHAR(20) NOT NULL,
    order_channel VARCHAR(30) NOT NULL,          -- Web Desktop, Mobile App, Marketplace (Amazon/eBay)
    payment_method VARCHAR(30) NOT NULL,         -- Credit Card, Debit Card, PayPal, BNPL (Klarna/Affirm)
    coupon_code VARCHAR(30),                     -- Applied promotional code (if any)
    order_discount_rate DECIMAL(5, 4) DEFAULT 0, -- Overall cart-level discount percentage (e.g. 0.15 = 15%)
    shipping_fee_charged DECIMAL(8, 2) DEFAULT 0,-- Amount customer paid for shipping (0 = Free Shipping)
    order_status VARCHAR(30) NOT NULL,           -- Completed, Cancelled, Returned
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- 4. ORDER_ITEMS TABLE (Fact Details / Granular Line Items)
DROP TABLE IF EXISTS order_items;
CREATE TABLE order_items (
    order_item_id VARCHAR(30) PRIMARY KEY,
    order_id VARCHAR(25) NOT NULL,
    product_id VARCHAR(20) NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_retail_price DECIMAL(10, 2) NOT NULL,   -- Price at time of order
    unit_cost_price DECIMAL(10, 2) NOT NULL,     -- Cost at time of order
    item_discount_rate DECIMAL(5, 4) DEFAULT 0,  -- Item-level promotional markdown
    line_total_revenue DECIMAL(10, 2) NOT NULL,  -- (unit_retail_price * (1 - item_discount_rate) * quantity)
    line_total_cogs DECIMAL(10, 2) NOT NULL,     -- (unit_cost_price * quantity)
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- 5. LOGISTICS & FULFILLMENT TABLE (Fact / Operational Dimension)
DROP TABLE IF EXISTS logistics;
CREATE TABLE logistics (
    shipment_id VARCHAR(30) PRIMARY KEY,
    order_id VARCHAR(25) NOT NULL,
    carrier VARCHAR(50) NOT NULL,                -- FedEx, UPS, DHL, USPS, Local Courier
    shipping_service VARCHAR(50) NOT NULL,       -- Next Day Air, 2-Day Priority, Ground, Economy
    actual_shipping_cost DECIMAL(10, 2) NOT NULL,-- What company paid carrier to ship order
    estimated_delivery_days INTEGER NOT NULL,
    actual_delivery_days INTEGER NOT NULL,
    delivery_status VARCHAR(30) NOT NULL,        -- On-Time, Delayed, Lost
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

-- 6. RETURNS & REFUNDS TABLE (Fact / Margin Erosion)
DROP TABLE IF EXISTS returns;
CREATE TABLE returns (
    return_id VARCHAR(30) PRIMARY KEY,
    order_item_id VARCHAR(30) NOT NULL,
    return_date DATE NOT NULL,
    return_reason VARCHAR(100) NOT NULL,         -- Defective, Sizing Mismatch, Buyer Remorse, Late Delivery, Fraud
    refund_amount DECIMAL(10, 2) NOT NULL,
    restocking_fee DECIMAL(8, 2) DEFAULT 0,
    reverse_logistics_cost DECIMAL(8, 2) NOT NULL,-- Return shipping & warehouse inspection expense
    item_disposition VARCHAR(50) NOT NULL,       -- Restocked, Liquidated, Scrapped
    salvage_recovered_value DECIMAL(8, 2) DEFAULT 0,
    FOREIGN KEY (order_item_id) REFERENCES order_items(order_item_id)
);

-- Indexes for high-performance analytical queries & joins
CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product ON order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_logistics_order ON logistics(order_id);
CREATE INDEX IF NOT EXISTS idx_returns_order_item ON returns(order_item_id);
