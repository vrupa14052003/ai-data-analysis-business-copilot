import pandas as pd
import gradio as gr
from chart_builder import (
    build_revenue_trend_chart,
    build_top_categories_chart,
    build_city_performance_chart,
    build_category_comparison_chart
)
import router
import query_agent
import insigt_why_agent





def handle_question(question):
    """
    Real version - uses the actual Router to classify the question,
    calls the appropriate agent, and builds a matching chart.
    """
    if not question.strip():
        return "Please enter a question.", None

    q = question.lower()

    # Use the REAL router classification
    category = router.classify_question(question)

    if category == "root_cause":
        date_info = router.extract_year_month(question)
        facts = insigt_why_agent.find_root_cause(date_info['year'], date_info['month'])
        answer_text = insigt_why_agent.explain_root_cause(facts)

        # Build a real chart from the actual category comparison data
        year, month = date_info['year'], date_info['month']
        if month == 1:
            prev_year, prev_month = year - 1, 12
        else:
            prev_year, prev_month = year, month - 1

        silver = pd.read_csv('data/silver_master.csv')
        silver['order_purchase_timestamp'] = pd.to_datetime(silver['order_purchase_timestamp'])
        silver['year_month'] = silver['order_purchase_timestamp'].dt.to_period('M')

        current = silver[silver['year_month'] == pd.Period(f"{year}-{month:02d}")]
        previous = silver[silver['year_month'] == pd.Period(f"{prev_year}-{prev_month:02d}")]

        current_cat = current.groupby('product_category_name')['price'].sum()
        prev_cat = previous.groupby('product_category_name')['price'].sum()
        category_change = (current_cat - prev_cat).fillna(-prev_cat).sort_values().head(10)

        chart = build_category_comparison_chart(category_change)

    elif category == "document_search":
        answer_text, sources = router.rag_agent.answer_from_documents(question)
        chart = None  # document answers don't get charts

    else:  # lookup
        plan = query_agent.ask_gemini_to_plan(question)
        result = query_agent.run_calculation(plan)
        answer_text = query_agent.ask_gemini_to_explain(question, result)

        if "city" in q or "cities" in q:
            chart = build_city_performance_chart()
        elif "top" in q or "categories" in q:
            chart = build_top_categories_chart()
        else:
            chart = build_revenue_trend_chart()

    return f"[Router decision: {category}]\n\n{answer_text}", chart

# ----- Build the interface -----
with gr.Blocks(title="PulseIQ - Business Intelligence Copilot") as demo:
    gr.Markdown("# 📊 PulseIQ")
    gr.Markdown("Ask any business question about your e-commerce data — revenue, trends, policies, or customer feedback.")

    with gr.Row():
        question_input = gr.Textbox(
            label="Your Question",
            placeholder="e.g. Why did revenue drop in August 2018?",
            lines=2
        )

    submit_btn = gr.Button("Ask PulseIQ", variant="primary")

    answer_output = gr.Textbox(
        label="Answer",
        lines=6,
        interactive=False
    )

    chart_output = gr.Plot(label="Visualization")

    gr.Examples(
        examples=[
            "What was total revenue in 2017?",
            "What are the top 5 categories by revenue?",
            "Which city has the highest revenue?",
            "What does our return policy say about furniture?"
        ],
        inputs=question_input
    )

    submit_btn.click(
        fn=handle_question,
        inputs=question_input,
        outputs=[answer_output, chart_output]
    )


if __name__ == "__main__":
    demo.launch(share=True)