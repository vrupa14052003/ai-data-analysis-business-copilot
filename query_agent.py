import json
import pandas as pd
from gemini_helper import safe_generate

# Load our Gold tables once
daily_revenue = pd.read_csv('data/gold_daily_revenue.csv')
category_performance = pd.read_csv('data/gold_category_performance.csv')
city_performance = pd.read_csv('data/gold_city_performance.csv')

daily_revenue['order_date'] = pd.to_datetime(daily_revenue['order_date'])

def ask_gemini_to_plan(question):
    """
    Step 1: Ask Gemini to figure out WHICH table and WHAT calculation
    we need - but NOT do the math itself.
    """
    prompt = f"""You are a data analyst assistant. A user asked this business question:

"{question}"

You have access to 3 tables:
1. daily_revenue - columns: order_date, total_revenue, order_count, avg_order_value
2. category_performance - columns: product_category_name, total_revenue, order_count, avg_price, avg_review_score
3. city_performance - columns: customer_city, total_revenue, order_count, avg_review_score

Decide which table is most relevant and what operation is needed.

Operations available:
- "sum" - total of a column across all data
- "average" - mean of a column
- "top_n" - ranked top N rows
- "filter_year" - total for one specific year
- "compare_periods" - compare two specific months (use this for ANY question mentioning two time periods, "change from X to Y", "vs", comparisons)

Respond ONLY in this exact JSON format, nothing else:
{{
  "table": "daily_revenue" or "category_performance" or "city_performance",
  "operation": "sum" or "top_n" or "filter_year" or "average" or "compare_periods",
  "column": "the column name to calculate on",
  "year": null or a year like 2017,
  "n": null or a number like 5,
  "period1_year": null or 2018,
  "period1_month": null or 7,
  "period2_year": null or 2018,
  "period2_month": null or 8
}}
"""
    response_text = safe_generate(prompt)
    text = response_text.strip()
    text = text.replace('```json', '').replace('```', '').strip()

    return json.loads(text)

def run_calculation(plan):
    """
    Step 2: Actually run the calculation using Pandas - reliable, no hallucination.
    """
    table_map = {
        'daily_revenue': daily_revenue,
        'category_performance': category_performance,
        'city_performance': city_performance
    }
    df = table_map[plan['table']]

    if plan['operation'] == 'filter_year' and plan['year']:
        filtered = df[df['order_date'].dt.year == plan['year']]
        result = filtered[plan['column']].sum()
        return f"{result:,.2f}"

    elif plan['operation'] == 'sum':
        result = df[plan['column']].sum()
        return f"{result:,.2f}"

    elif plan['operation'] == 'average':
        result = df[plan['column']].mean()
        return f"{result:,.2f}"

    elif plan['operation'] == 'top_n':
        n = plan['n'] or 5
        top = df.sort_values(plan['column'], ascending=False).head(n)
        return top.to_string(index=False)

    elif plan['operation'] == 'compare_periods':
        # Period 1
        mask1 = (df['order_date'].dt.year == plan['period1_year']) & (df['order_date'].dt.month == plan['period1_month'])
        period1_total = df[mask1][plan['column']].sum()

        # Period 2
        mask2 = (df['order_date'].dt.year == plan['period2_year']) & (df['order_date'].dt.month == plan['period2_month'])
        period2_total = df[mask2][plan['column']].sum()

        change = period2_total - period1_total
        change_pct = (change / period1_total * 100) if period1_total > 0 else 0

        return (f"Period 1 ({plan['period1_year']}-{plan['period1_month']:02d}): {period1_total:,.2f}\n"
                f"Period 2 ({plan['period2_year']}-{plan['period2_month']:02d}): {period2_total:,.2f}\n"
                f"Change: {change:,.2f} ({change_pct:+.2f}%)")

    return "Could not calculate"


def ask_gemini_to_explain(question, result):
    """
    Step 3: Ask Gemini to explain the result in plain English business language.
    """
    prompt = f"""A user asked: "{question}"

The actual calculated answer (from real data, already verified) is:
{result}

Write a clear, 2-sentence business answer using this exact number. 
Do not make up any additional numbers - only use what's given above."""

    response_text = safe_generate(prompt)
    return response_text


# ----- MAIN: Test it -----
if __name__ == "__main__":
    question = "What was total revenue in 2017?"

    print(f"Question: {question}\n")

    plan = ask_gemini_to_plan(question)
    print(f"Agent's plan: {plan}\n")


    result = run_calculation(plan)
    print(f"Calculated result: {result}\n")

    answer = ask_gemini_to_explain(question, result)
    print(f"Final answer: {answer}")