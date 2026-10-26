"""
==============================================================================
PROJECT: Omnichannel Profitability & Margin Leakage Intelligence Engine
MODULE: 01_generate_data.py
DESCRIPTION: Generates realistic multi-table enterprise retail dataset with 
             embedded margin leaks (discount stacking, return rate skew, 
             logistics subsidization).
==============================================================================
"""

import os
import sys
import random
import datetime
import numpy as np
import pandas as pd

# Reconfigure stdout for UTF-8 compatibility on Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Set fixed seed for reproducibility
np.random.seed(42)
random.seed(42)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("🚀 Starting synthetic retail enterprise data generation...")

# ------------------------------------------------------------------------------
# 1. GENERATE CUSTOMERS (Dimension)
# ------------------------------------------------------------------------------
N_CUSTOMERS = 1200
first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
               "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
               "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
               "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley"]
last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
              "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
              "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White"]

segments = ["Consumer", "Corporate", "Small Business"]
segment_weights = [0.65, 0.22, 0.13]

regions = ["North", "South", "East", "West", "Central"]
region_weights = [0.25, 0.22, 0.26, 0.17, 0.10]

channels = ["Paid Search", "Organic Search", "Affiliate", "Social Media", "Direct"]
channel_weights = [0.30, 0.25, 0.15, 0.20, 0.10]

loyalty_tiers = ["Standard", "Silver", "Gold", "Platinum"]
loyalty_weights = [0.55, 0.25, 0.14, 0.06]

customers_data = []
base_signup = datetime.date(2023, 1, 1)

for i in range(1, N_CUSTOMERS + 1):
    cid = f"CUST-{i:05d}"
    name = f"{random.choice(first_names)} {random.choice(last_names)}"
    segment = np.random.choice(segments, p=segment_weights)
    region = np.random.choice(regions, p=region_weights)
    channel = np.random.choice(channels, p=channel_weights)
    signup = base_signup + datetime.timedelta(days=random.randint(0, 600))
    tier = np.random.choice(loyalty_tiers, p=loyalty_weights)
    
    customers_data.append({
        "customer_id": cid,
        "customer_name": name,
        "customer_segment": segment,
        "region": region,
        "acquisition_channel": channel,
        "signup_date": signup.strftime("%Y-%m-%d"),
        "loyalty_tier": tier
    })

df_customers = pd.DataFrame(customers_data)
df_customers.to_csv(os.path.join(OUTPUT_DIR, "customers.csv"), index=False)
print(f"✅ Generated {len(df_customers)} customers -> data/customers.csv")

# ------------------------------------------------------------------------------
# 2. GENERATE PRODUCTS (Dimension)
# ------------------------------------------------------------------------------
product_catalog = [
    # Electronics
    ("Noise-Cancelling Headphones", "Electronics", "Audio", 85.00, 199.99, 0.8),
    ("Wireless Bluetooth Earbuds", "Electronics", "Audio", 28.00, 79.99, 0.3),
    ("Smartwatch Fitness Tracker", "Electronics", "Wearables", 65.00, 149.99, 0.4),
    ("Ultra-Slim 4K Monitor 27in", "Electronics", "Monitors", 160.00, 329.99, 6.2),
    ("Mechanical Gaming Keyboard", "Electronics", "Accessories", 42.00, 109.99, 1.2),
    ("Wireless Ergonomic Mouse", "Electronics", "Accessories", 18.00, 49.99, 0.4),
    ("100W USB-C Fast Charger", "Electronics", "Accessories", 12.00, 39.99, 0.3),
    ("Portable 1TB SSD Drive", "Electronics", "Storage", 52.00, 119.99, 0.2),
    ("Smart Home Security Cam", "Electronics", "Smart Home", 34.00, 89.99, 0.7),
    ("Streaming 4K Media Stick", "Electronics", "Smart Home", 20.00, 49.99, 0.3),
    
    # Apparel
    ("Classic Slim Fit Jeans", "Apparel", "Denim", 18.00, 59.99, 0.8),
    ("Organic Cotton Crew T-Shirt", "Apparel", "Tops", 6.00, 24.99, 0.3),
    ("Water-Resistant Hooded Parka", "Apparel", "Outerwear", 45.00, 139.99, 1.5),
    ("Merino Wool Knit Sweater", "Apparel", "Knitwear", 28.00, 89.99, 0.7),
    ("Athletic Performance Leggings", "Apparel", "Activewear", 14.00, 49.99, 0.4),
    ("Running Shoes Cushion Sole", "Apparel", "Footwear", 35.00, 119.99, 1.1),
    ("Leather Dress Oxford Shoes", "Apparel", "Footwear", 55.00, 159.99, 1.4),
    ("Thermal Fleece Zip Jacket", "Apparel", "Outerwear", 22.00, 69.99, 0.9),
    ("Breathable Workout Shorts", "Apparel", "Activewear", 9.00, 29.99, 0.3),
    ("Business Casual Chino Pants", "Apparel", "Pants", 16.00, 54.99, 0.6),

    # Home & Kitchen
    ("Stainless Steel Cookware Set", "Home & Kitchen", "Cookware", 80.00, 229.99, 8.5),
    ("Ceramic Non-Stick Frying Pan", "Home & Kitchen", "Cookware", 16.00, 44.99, 1.4),
    ("Espresso Coffee Maker Deluxe", "Home & Kitchen", "Appliances", 95.00, 249.99, 4.8),
    ("Digital Air Fryer 5.8 Qt", "Home & Kitchen", "Appliances", 42.00, 119.99, 5.2),
    ("High-Speed Blender 1200W", "Home & Kitchen", "Appliances", 38.00, 99.99, 3.6),
    ("Memory Foam Contour Pillow", "Home & Kitchen", "Bedding", 15.00, 49.99, 1.2),
    ("Egyptian Cotton 4-Piece Sheet", "Home & Kitchen", "Bedding", 32.00, 89.99, 2.1),
    ("Aromatherapy Essential Diffuser", "Home & Kitchen", "Decor", 11.00, 32.99, 0.6),
    ("Robot Vacuum Cleaner Wi-Fi", "Home & Kitchen", "Appliances", 110.00, 279.99, 4.5),
    ("Insulated Stainless Water Bottle", "Home & Kitchen", "Dining", 7.00, 24.99, 0.5),

    # Office Supplies
    ("Ergonomic Mesh Office Chair", "Office Supplies", "Furniture", 75.00, 219.99, 14.5),
    ("Electric Standing Desk 55in", "Office Supplies", "Furniture", 140.00, 379.99, 28.0),
    ("Dual Monitor Desk Mount Arm", "Office Supplies", "Accessories", 22.00, 59.99, 3.8),
    ("Executive Leather Notebook A5", "Office Supplies", "Stationery", 4.50, 18.99, 0.4),
    ("Noise-Dampening Desk Divider", "Office Supplies", "Furniture", 19.00, 54.99, 2.5),
    ("Heavy-Duty Document Shredder", "Office Supplies", "Equipment", 36.00, 89.99, 5.5),

    # Beauty & Personal Care
    ("Sonic Electric Toothbrush", "Beauty & Personal", "Dental", 24.00, 69.99, 0.5),
    ("Ionic Hair Dryer Salon Pro", "Beauty & Personal", "Haircare", 30.00, 89.99, 1.2),
    ("Anti-Aging Retinol Serum 50ml", "Beauty & Personal", "Skincare", 8.50, 38.99, 0.2),
    ("Hydrating Botanical Cleanser", "Beauty & Personal", "Skincare", 6.00, 22.99, 0.3),
]

products_data = []
for idx, p in enumerate(product_catalog, 1):
    pid = f"PROD-{idx:04d}"
    products_data.append({
        "product_id": pid,
        "product_name": p[0],
        "category": p[1],
        "sub_category": p[2],
        "cost_price": round(p[3], 2),
        "base_retail_price": round(p[4], 2),
        "weight_kg": round(p[5], 2)
    })

df_products = pd.DataFrame(products_data)
df_products.to_csv(os.path.join(OUTPUT_DIR, "products.csv"), index=False)
print(f"✅ Generated {len(df_products)} products -> data/products.csv")

# ------------------------------------------------------------------------------
# 3. GENERATE ORDERS, ORDER ITEMS, LOGISTICS & RETURNS
# ------------------------------------------------------------------------------
N_ORDERS = 8500
order_channels = ["Web Desktop", "Mobile App", "Marketplace"]
channel_p = [0.42, 0.48, 0.10]

payment_methods = ["Credit Card", "Debit Card", "PayPal", "BNPL"]
payment_p = [0.52, 0.20, 0.18, 0.10]

coupons = [
    (None, 0.0),
    ("WELCOME10", 0.10),
    ("VIP20", 0.20),
    ("FLASH25", 0.25),
    ("CLEARANCE35", 0.35),
    ("FREESHIP", 0.0)
]
coupon_weights = [0.50, 0.18, 0.12, 0.10, 0.06, 0.04]

carriers = [
    ("FedEx", 1.15),
    ("UPS", 1.10),
    ("DHL", 1.25),
    ("USPS", 0.85),
    ("Local Courier", 0.95)
]

start_date = datetime.datetime(2023, 11, 1, 8, 0, 0)
end_date = datetime.datetime(2024, 10, 31, 23, 59, 59)
total_seconds = int((end_date - start_date).total_seconds())

orders_list = []
order_items_list = []
logistics_list = []
returns_list = []

item_counter = 1
return_counter = 1

customer_ids = df_customers["customer_id"].values
product_records = df_products.to_dict("records")

print("🔄 Generating 8,500 orders and detailed line-item economics...")

for i in range(1, N_ORDERS + 1):
    order_id = f"ORD-{i:06d}"
    order_timestamp = start_date + datetime.timedelta(seconds=random.randint(0, total_seconds))
    cust_id = np.random.choice(customer_ids)
    channel = np.random.choice(order_channels, p=channel_p)
    payment = np.random.choice(payment_methods, p=payment_p)
    
    # Coupon selection
    coupon_idx = np.random.choice(len(coupons), p=coupon_weights)
    coupon_code, order_discount_rate = coupons[coupon_idx]

    # Order Items (1 to 4 distinct items per order)
    num_items = np.random.choice([1, 2, 3, 4], p=[0.50, 0.32, 0.13, 0.05])
    selected_products = random.sample(product_records, num_items)
    
    order_gross_subtotal = 0
    total_order_weight = 0
    order_item_ids = []
    
    for prod in selected_products:
        item_id = f"ITEM-{item_counter:07d}"
        item_counter += 1
        order_item_ids.append((item_id, prod))
        
        qty = np.random.choice([1, 2, 3], p=[0.82, 0.14, 0.04])
        unit_retail = prod["base_retail_price"]
        unit_cost = prod["cost_price"]
        
        # Item-level promotional discount (e.g. Clearance sale markdown on specific SKU)
        # Margin leak condition: Sometimes items are already discounted 15-25%
        if random.random() < 0.20:
            item_discount = random.choice([0.10, 0.15, 0.20, 0.30])
        else:
            item_discount = 0.0
            
        line_rev = round(unit_retail * (1.0 - item_discount) * qty, 2)
        line_cogs = round(unit_cost * qty, 2)
        order_gross_subtotal += line_rev
        total_order_weight += prod["weight_kg"] * qty
        
        order_items_list.append({
            "order_item_id": item_id,
            "order_id": order_id,
            "product_id": prod["product_id"],
            "quantity": qty,
            "unit_retail_price": unit_retail,
            "unit_cost_price": unit_cost,
            "item_discount_rate": item_discount,
            "line_total_revenue": line_rev,
            "line_total_cogs": line_cogs
        })
        
    # Free shipping policy rule & margin leak:
    # Company policy: Free shipping if basket > $65 OR if coupon FREESHIP used.
    # But shipping actual cost depends on weight and carrier.
    if order_gross_subtotal >= 65.0 or coupon_code == "FREESHIP":
        shipping_fee_charged = 0.0
    else:
        shipping_fee_charged = 6.99
        
    order_status = "Completed"
    
    # --------------------------------------------------------------------------
    # LOGISTICS GENERATION
    # --------------------------------------------------------------------------
    carrier_info = random.choice(carriers)
    carrier_name = carrier_info[0]
    carrier_multiplier = carrier_info[1]
    
    shipping_service = random.choice(["Ground", "2-Day Priority", "Next Day Air", "Economy"])
    service_rates = {"Economy": 5.50, "Ground": 8.00, "2-Day Priority": 14.50, "Next Day Air": 26.00}
    
    base_carrier_charge = service_rates[shipping_service] + (total_order_weight * 1.75)
    actual_shipping_cost = round(base_carrier_charge * carrier_multiplier, 2)
    
    est_days = {"Next Day Air": 1, "2-Day Priority": 2, "Ground": 4, "Economy": 6}[shipping_service]
    
    # Delivery performance & delay probability
    # Carriers like USPS or Local Courier occasionally suffer from delays
    delay_prob = 0.22 if carrier_name in ["USPS", "Local Courier"] else 0.08
    if random.random() < delay_prob:
        actual_days = est_days + random.randint(2, 6)
        delivery_status = "Delayed"
    else:
        actual_days = est_days
        delivery_status = "On-Time"
        
    logistics_list.append({
        "shipment_id": f"SHIP-{i:06d}",
        "order_id": order_id,
        "carrier": carrier_name,
        "shipping_service": shipping_service,
        "actual_shipping_cost": actual_shipping_cost,
        "estimated_delivery_days": est_days,
        "actual_delivery_days": actual_days,
        "delivery_status": delivery_status
    })

    # --------------------------------------------------------------------------
    # RETURNS & REFUNDS (Margin Leak Mechanism)
    # --------------------------------------------------------------------------
    # Return probability drivers:
    # 1. Apparel has higher return rate (sizing)
    # 2. Delayed deliveries cause buyer remorse/cancellation
    # 3. High discounts (>25%) trigger impulse buying and higher return rates
    for itm_id, prod in order_item_ids:
        ret_prob = 0.06 # baseline
        if prod["category"] == "Apparel":
            ret_prob += 0.16 # 22% baseline for clothes
        if delivery_status == "Delayed":
            ret_prob += 0.10
        if order_discount_rate >= 0.25:
            ret_prob += 0.09
            
        if random.random() < ret_prob:
            order_status = "Returned"
            ret_id = f"RET-{return_counter:06d}"
            return_counter += 1
            
            # Days after order for return
            ret_date = (order_timestamp + datetime.timedelta(days=random.randint(4, 25))).date()
            
            # Determine return reason
            if prod["category"] == "Apparel":
                reason = np.random.choice(["Sizing Mismatch", "Buyer Remorse", "Late Delivery"], p=[0.60, 0.25, 0.15])
            elif delivery_status == "Delayed":
                reason = np.random.choice(["Late Delivery", "Buyer Remorse", "Defective"], p=[0.65, 0.25, 0.10])
            else:
                reason = np.random.choice(["Defective", "Buyer Remorse", "Sizing Mismatch"], p=[0.40, 0.40, 0.20])
                
            # Refund calculation
            refund_amt = prod["base_retail_price"] * (1.0 - order_discount_rate)
            restocking_fee = 0.0 # Modern retail rarely charges restocking fee
            reverse_logistics = round(6.50 + (prod["weight_kg"] * 1.5), 2)
            
            # Disposition: restocked, liquidated, or scrapped
            if reason == "Defective":
                disposition = np.random.choice(["Scrapped", "Liquidated"], p=[0.70, 0.30])
                salvage_val = round(prod["cost_price"] * 0.20, 2) if disposition == "Liquidated" else 0.0
            elif reason == "Sizing Mismatch":
                disposition = np.random.choice(["Restocked", "Liquidated"], p=[0.75, 0.25])
                salvage_val = round(prod["cost_price"] * 0.85, 2) if disposition == "Restocked" else round(prod["cost_price"] * 0.30, 2)
            else:
                disposition = "Restocked"
                salvage_val = round(prod["cost_price"] * 0.90, 2)
                
            returns_list.append({
                "return_id": ret_id,
                "order_item_id": itm_id,
                "return_date": ret_date.strftime("%Y-%m-%d"),
                "return_reason": reason,
                "refund_amount": round(refund_amt, 2),
                "restocking_fee": restocking_fee,
                "reverse_logistics_cost": reverse_logistics,
                "item_disposition": disposition,
                "salvage_recovered_value": salvage_val
            })
            
    orders_list.append({
        "order_id": order_id,
        "order_date": order_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "customer_id": cust_id,
        "order_channel": channel,
        "payment_method": payment,
        "coupon_code": coupon_code if coupon_code else "NONE",
        "order_discount_rate": order_discount_rate,
        "shipping_fee_charged": shipping_fee_charged,
        "order_status": order_status
    })

# Export to CSVs
df_orders = pd.DataFrame(orders_list)
df_order_items = pd.DataFrame(order_items_list)
df_logistics = pd.DataFrame(logistics_list)
df_returns = pd.DataFrame(returns_list)

df_orders.to_csv(os.path.join(OUTPUT_DIR, "orders.csv"), index=False)
df_order_items.to_csv(os.path.join(OUTPUT_DIR, "order_items.csv"), index=False)
df_logistics.to_csv(os.path.join(OUTPUT_DIR, "logistics.csv"), index=False)
df_returns.to_csv(os.path.join(OUTPUT_DIR, "returns.csv"), index=False)

print(f"✅ Generated {len(df_orders):,} orders -> data/orders.csv")
print(f"✅ Generated {len(df_order_items):,} order line items -> data/order_items.csv")
print(f"✅ Generated {len(df_logistics):,} logistics shipments -> data/logistics.csv")
print(f"✅ Generated {len(df_returns):,} product returns -> data/returns.csv")
print("🎉 Synthetic enterprise data generation completed successfully!")
