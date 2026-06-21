import pandas as pd

silver = pd.read_csv('data/silver_master.csv')
silver['order_purchase_timestamp'] = pd.to_datetime(silver['order_purchase_timestamp'])

data_2017 = silver[silver['order_purchase_timestamp'].dt.year == 2017]
print(f"Number of order-item rows in 2017: {len(data_2017)}")
print(f"Sum of price for 2017 (from Silver): {data_2017['price'].sum():,.2f}")