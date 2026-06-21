import pandas as pd

silver = pd.read_csv('data/silver_master.csv')

print("=" * 50)
print("DATA QUALITY CHECK")
print("=" * 50)

# Check for missing values in important columns
print("\nMissing values per column:")
important_cols = ['price', 'product_category_name', 'customer_state', 'review_score']
print(silver[important_cols].isnull().sum())

# Check for duplicate order_items (shouldn't exist)
print(f"\nDuplicate rows: {silver.duplicated().sum()}")

# Check price range (catch negative or zero prices - red flag)
print(f"\nPrice range: {silver['price'].min()} to {silver['price'].max()}")
print(f"Orders with price = 0: {(silver['price'] == 0).sum()}")

# Check review score range (should be 1-5 only)
print(f"\nReview score range: {silver['review_score'].min()} to {silver['review_score'].max()}")

# How many unique product categories exist?
print(f"\nUnique product categories: {silver['product_category_name'].nunique()}")
print(silver['product_category_name'].value_counts().head(10))