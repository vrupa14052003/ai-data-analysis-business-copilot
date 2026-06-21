import pandas as pd

daily_revenue = pd.read_csv('data/gold_daily_revenue.csv')
daily_revenue['order_date'] = pd.to_datetime(daily_revenue['order_date'])

# Manually filter to 2017 and sum - the "ground truth" way
data_2017 = daily_revenue[daily_revenue['order_date'].dt.year == 2017]
print(f"Number of days in 2017: {len(data_2017)}")
print(f"Sum of total_revenue for 2017: {data_2017['total_revenue'].sum():,.2f}")

# Also check: what does the dtype of order_date actually look like in the live process?
print(f"\nColumn dtype: {daily_revenue['order_date'].dtype}")
print(daily_revenue.head(2))