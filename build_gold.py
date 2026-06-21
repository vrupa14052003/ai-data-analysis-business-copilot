import pandas as pd

# Load Silver layer
silver = pd.read_csv('data/silver_master.csv')
silver['order_purchase_timestamp'] = pd.to_datetime(silver['order_purchase_timestamp'])
silver['order_date'] = silver['order_purchase_timestamp'].dt.date

# ----- GOLD TABLE 1: Daily Revenue -----
daily_revenue = silver.groupby('order_date').agg(
    total_revenue=('price', 'sum'),
    order_count=('order_id', 'nunique'),
    avg_order_value=('price', 'mean')
).reset_index()

daily_revenue.to_csv('data/gold_daily_revenue.csv', index=False)

# ----- GOLD TABLE 2: Category Performance -----
category_performance = silver.groupby('product_category_name').agg(
    total_revenue=('price', 'sum'),
    order_count=('order_id', 'nunique'),
    avg_price=('price', 'mean'),
    avg_review_score=('review_score', 'mean')
).reset_index().sort_values('total_revenue', ascending=False)

category_performance.to_csv('data/gold_category_performance.csv', index=False)

# ----- GOLD TABLE 3: City Performance -----
city_performance = silver.groupby('customer_city').agg(
    total_revenue=('price', 'sum'),
    order_count=('order_id', 'nunique'),
    avg_review_score=('review_score', 'mean')
).reset_index().sort_values('total_revenue', ascending=False)

city_performance.to_csv('data/gold_city_performance.csv', index=False)

# ----- Print Summary -----
print("Gold layer built successfully!\n")

print("DAILY REVENUE (sample):")
print(daily_revenue.head())
print(f"Total days: {len(daily_revenue)}\n")

print("CATEGORY PERFORMANCE (top 5):")
print(category_performance.head())
print(f"Total categories: {len(category_performance)}\n")

print("CITY PERFORMANCE (top 5):")
print(city_performance.head())
print(f"Total cities: {len(city_performance)}")