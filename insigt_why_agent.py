import json
import pandas as pd
from gemini_helper import safe_generate

# Load Silver layer - we need order-level detail for this, not just Gold summaries
silver = pd.read_csv('data/silver_master.csv')
silver['order_purchase_timestamp'] = pd.to_datetime(silver['order_purchase_timestamp'])
silver['year_month'] = silver['order_purchase_timestamp'].dt.to_period('M')


def get_monthly_revenue(year, month):
    """Get total revenue for a specific year-month."""
    period = pd.Period(f"{year}-{month:02d}")
    data = silver[silver['year_month'] == period]
    return data['price'].sum(), data


def find_root_cause(year, month):
    """
    Compare this month vs previous month.
    Find which category and city changed the most.
    """
    # Current month
    current_revenue, current_data = get_monthly_revenue(year, month)

    # Previous month (handle January -> December of previous year)
    if month == 1:
        prev_year, prev_month = year - 1, 12
    else:
        prev_year, prev_month = year, month - 1

    prev_revenue, prev_data = get_monthly_revenue(prev_year, prev_month)

    # Overall change
    change_pct = ((current_revenue - prev_revenue) / prev_revenue) * 100 if prev_revenue > 0 else 0

    # Category-level comparison
    current_by_category = current_data.groupby('product_category_name')['price'].sum()
    prev_by_category = prev_data.groupby('product_category_name')['price'].sum()
    category_change = (current_by_category - prev_by_category).fillna(-prev_by_category).sort_values()

    # City-level comparison
    current_by_city = current_data.groupby('customer_city')['price'].sum()
    prev_by_city = prev_data.groupby('customer_city')['price'].sum()
    city_change = (current_by_city - prev_by_city).fillna(-prev_by_city).sort_values()

    return {
        "current_month": f"{year}-{month:02d}",
        "previous_month": f"{prev_year}-{prev_month:02d}",
        "current_revenue": round(current_revenue, 2),
        "previous_revenue": round(prev_revenue, 2),
        "change_pct": round(change_pct, 2),
        "biggest_category_decline": category_change.index[0] if len(category_change) > 0 else None,
        "category_decline_amount": round(category_change.iloc[0], 2) if len(category_change) > 0 else None,
        "biggest_city_decline": city_change.index[0] if len(city_change) > 0 else None,
        "city_decline_amount": round(city_change.iloc[0], 2) if len(city_change) > 0 else None,
    }


def explain_root_cause(facts):
    """
    Give Gemini the REAL calculated facts and ask it to explain WHY,
    using only these numbers - no inventing new ones.
    """
    prompt = f"""You are a business analyst. Here are VERIFIED facts comparing two months:

Current month: {facts['current_month']} - Revenue: {facts['current_revenue']:,.2f}
Previous month: {facts['previous_month']} - Revenue: {facts['previous_revenue']:,.2f}
Change: {facts['change_pct']}%

Category that declined the most: {facts['biggest_category_decline']} (change: {facts['category_decline_amount']:,.2f})
City that declined the most: {facts['biggest_city_decline']} (change: {facts['city_decline_amount']:,.2f})

Write a 3-sentence root cause analysis using ONLY these numbers. 
Sentence 1: State what happened to overall revenue.
Sentence 2: Identify the primary driver (category or city).
Sentence 3: One actionable recommendation.

Do not invent any numbers not given above."""

    response_text = safe_generate(prompt)
    return response_text


# ----- MAIN: Test it -----
if __name__ == "__main__":
    year, month = 2018, 8  # August 2018

    print(f"Analyzing: {year}-{month:02d}\n")

    facts = find_root_cause(year, month)
    print("Verified facts:")
    for k, v in facts.items():
        print(f"  {k}: {v}")
    print()

    explanation = explain_root_cause(facts)
    print(f"Root Cause Analysis:\n{explanation}")