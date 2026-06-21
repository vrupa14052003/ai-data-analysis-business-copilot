import plotly.graph_objects as go
import pandas as pd


def build_revenue_trend_chart():
    """
    Chart 1: Daily revenue trend over time - for 'what was revenue' 
    or general trend questions.
    """
    daily_revenue = pd.read_csv('data/gold_daily_revenue.csv')
    daily_revenue['order_date'] = pd.to_datetime(daily_revenue['order_date'])

    # Group by month for a cleaner chart (daily data is too noisy)
    monthly = daily_revenue.set_index('order_date').resample('ME')['total_revenue'].sum().reset_index()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly['order_date'],
        y=monthly['total_revenue'],
        mode='lines+markers',
        name='Monthly Revenue',
        line=dict(color='#4C9AFF', width=3)
    ))
    fig.update_layout(
        title='Revenue Trend Over Time',
        xaxis_title='Month',
        yaxis_title='Revenue (BRL)',
        template='plotly_white',
        height=400
    )
    return fig


def build_category_comparison_chart(category_change_data):
    """
    Chart 2: Shows category-level revenue changes - for root cause questions.
    Takes REAL data already calculated by insight_agent (no new numbers invented).

    category_change_data should be a pandas Series: category name -> change amount
    """
    top_changes = category_change_data.head(10)

    colors = ['#E74C3C' if val < 0 else '#27AE60' for val in top_changes.values]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=top_changes.index,
        y=top_changes.values,
        marker_color=colors
    ))
    fig.update_layout(
        title='Revenue Change by Category (Month over Month)',
        xaxis_title='Category',
        yaxis_title='Change in Revenue (BRL)',
        template='plotly_white',
        height=400
    )
    return fig


def build_top_categories_chart():
    """
    Chart 3: Top categories by total revenue - for 'top N' lookup questions.
    """
    category_performance = pd.read_csv('data/gold_category_performance.csv')
    top10 = category_performance.sort_values('total_revenue', ascending=False).head(10)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=top10['total_revenue'],
        y=top10['product_category_name'],
        orientation='h',
        marker_color='#4C9AFF'
    ))
    fig.update_layout(
        title='Top 10 Categories by Revenue',
        xaxis_title='Revenue (BRL)',
        yaxis_title='Category',
        template='plotly_white',
        height=400,
        yaxis=dict(autorange="reversed")  # highest at top
    )
    return fig


def build_city_performance_chart():
    """
    Chart 4: Top cities by revenue - for city-related questions.
    """
    city_performance = pd.read_csv('data/gold_city_performance.csv')
    top10 = city_performance.sort_values('total_revenue', ascending=False).head(10)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=top10['customer_city'],
        y=top10['total_revenue'],
        marker_color='#9B59B6'
    ))
    fig.update_layout(
        title='Top 10 Cities by Revenue',
        xaxis_title='City',
        yaxis_title='Revenue (BRL)',
        template='plotly_white',
        height=400
    )
    return fig


# ----- Test all 3 charts that don't need extra input -----
if __name__ == "__main__":
    print("Building revenue trend chart...")
    fig1 = build_revenue_trend_chart()
    fig1.write_html('test_chart_trend.html')
    print("  Saved to test_chart_trend.html")

    print("Building top categories chart...")
    fig2 = build_top_categories_chart()
    fig2.write_html('test_chart_categories.html')
    print("  Saved to test_chart_categories.html")

    print("Building city performance chart...")
    fig3 = build_city_performance_chart()
    fig3.write_html('test_chart_city.html')
    print("  Saved to test_chart_city.html")

    print("\nDone! Open the .html files in your browser to see the charts.")