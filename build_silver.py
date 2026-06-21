import pandas as pd

# ----- BRONZE: Load raw data -----
orders = pd.read_csv('data/olist_orders_dataset.csv')
customers = pd.read_csv('data/olist_customers_dataset.csv')
order_items = pd.read_csv('data/olist_order_items_dataset.csv')
products = pd.read_csv('data/olist_products_dataset.csv')
reviews = pd.read_csv('data/olist_order_reviews_dataset.csv')


# ----- Apply Daily Drip Filter (only show orders "released" so far) -----
import os

if os.path.exists('data/visible_order_ids.csv'):
    visible_ids = pd.read_csv('data/visible_order_ids.csv')['order_id'].tolist()
    orders = orders[orders['order_id'].isin(visible_ids)]
    print(f"Daily drip active: filtering to {len(visible_ids)} visible orders")
else:
    print("No drip filter found - using full dataset")
# ----- SILVER: Clean + Join into one master table -----

# Step 1: Keep only delivered orders (most reliable data)
orders_clean = orders[orders['order_status'] == 'delivered'].copy()

# Step 2: Convert date columns to actual dates (not text)
orders_clean['order_purchase_timestamp'] = pd.to_datetime(orders_clean['order_purchase_timestamp'])

# Step 3: Join orders with customers (who bought it)
silver = orders_clean.merge(customers, on='customer_id', how='left')

# Step 4: Join with order_items (what was bought, price)
silver = silver.merge(order_items, on='order_id', how='left')

# Step 5: Join with products (category info)
silver = silver.merge(products, on='product_id', how='left')

# Step 5b: Label missing categories as "unknown" instead of leaving blank
silver['product_category_name'] = silver['product_category_name'].fillna('unknown')

# Step 6: Join with reviews (customer satisfaction)
reviews_unique = reviews.drop_duplicates(subset='order_id', keep='first')
silver = silver.merge(reviews_unique, on='order_id', how='left')

# Step 7: Drop rows with no price (broken/incomplete order)
silver = silver.dropna(subset=['price'])

# ----- Save Silver Layer -----
silver.to_csv('data/silver_master.csv', index=False)

print("Silver layer built successfully!")
print(f"Shape: {silver.shape}")
print(f"Date range: {silver['order_purchase_timestamp'].min()} to {silver['order_purchase_timestamp'].max()}")
print()
print("Columns available:")
print(silver.columns.tolist())