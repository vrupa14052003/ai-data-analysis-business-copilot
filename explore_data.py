import pandas as pd

# Show all columns when printing (so nothing gets cut off)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

# Load the core datasets
orders = pd.read_csv('data/olist_orders_dataset.csv')
customers = pd.read_csv('data/olist_customers_dataset.csv')
order_items = pd.read_csv('data/olist_order_items_dataset.csv')
products = pd.read_csv('data/olist_products_dataset.csv')
reviews = pd.read_csv('data/olist_order_reviews_dataset.csv')

# Print shape (rows, columns) for each
print("=" * 50)
print("ORDERS")
print("=" * 50)
print(f"Shape: {orders.shape}")
print(orders.head(3))
print()

print("=" * 50)
print("CUSTOMERS")
print("=" * 50)
print(f"Shape: {customers.shape}")
print(customers.head(3))
print()

print("=" * 50)
print("ORDER ITEMS")
print("=" * 50)
print(f"Shape: {order_items.shape}")
print(order_items.head(3))
print()

print("=" * 50)
print("PRODUCTS")
print("=" * 50)
print(f"Shape: {products.shape}")
print(products.head(3))
print()

print("=" * 50)
print("REVIEWS")
print("=" * 50)
print(f"Shape: {reviews.shape}")
print(reviews.head(3))


