import pandas as pd
import sys
from pipeline_state import get_current_state, save_state

# Default: release 15 days per run, unless overridden
DAYS_PER_RUN = 15

# Check for command-line argument to release everything at once
release_all = len(sys.argv) > 1 and sys.argv[1] == "all"

# ----- Load the FULL historical dataset (the complete "source of truth") -----
orders = pd.read_csv('data/olist_orders_dataset.csv')
orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])
orders_delivered = orders[orders['order_status'] == 'delivered'].copy()

all_dates = sorted(orders_delivered['order_purchase_timestamp'].dt.date.unique())
total_days_available = len(all_dates)

state = get_current_state()
days_already_released = state['days_released']

if days_already_released >= total_days_available:
    print("All historical data has already been released. Pipeline is fully caught up.")
    print(f"Total days available: {total_days_available}")
else:
    if release_all:
        new_days_end = total_days_available
        print("RELEASE ALL MODE - releasing entire remaining dataset")
    else:
        new_days_end = min(days_already_released + DAYS_PER_RUN, total_days_available)

    newly_released_dates = all_dates[days_already_released:new_days_end]

    print(f"Pipeline Run - {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Previously released: {days_already_released} days")
    print(f"Releasing {len(newly_released_dates)} new days: {newly_released_dates[0]} to {newly_released_dates[-1]}")

    visible_dates = all_dates[:new_days_end]
    visible_data = orders_delivered[orders_delivered['order_purchase_timestamp'].dt.date.isin(visible_dates)]

    print(f"Total orders now visible in pipeline: {len(visible_data)} (out of {len(orders_delivered)} total)")

    visible_order_ids = visible_data['order_id'].tolist()
    pd.Series(visible_order_ids).to_csv('data/visible_order_ids.csv', index=False, header=['order_id'])

    save_state(new_days_end, pd.Timestamp.now())

    print(f"\nState saved. {new_days_end}/{total_days_available} days now released.")
    print("Run build_silver.py and build_gold.py next to refresh the pipeline with this new data.")