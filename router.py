

# Import your existing agents
import query_agent
import insigt_why_agent
import time

import json
from gemini_helper import safe_generate

import rag_agent


def classify_question(question):
    """
    Decide if this is a WHAT question (lookup), WHY question (root cause),
    or a DOCUMENT question (policy/review search).
    """
    prompt = f"""Classify this business question into exactly one category:

Question: "{question}"

Categories:
- "lookup" - asking for a specific number, total, average, ranking, or comparison between time periods (e.g. "what was revenue", "top 5 categories", "how did revenue change from July to August")
- "root_cause" - asking WHY something happened, especially unexplained changes over time (e.g. "why did revenue drop", "what caused the decline")
- "document_search" - asking about policies, rules, customer reviews, or what customers said/think (e.g. "what does our return policy say", "what do customers think about X", "what are the delivery terms")

Respond with ONLY one word: lookup or root_cause or document_search"""

    response_text = safe_generate(prompt)
    return response_text.strip().lower()


def extract_year_month(question):
    """
    For root_cause questions, extract which year/month they're asking about.
    Defaults to August 2018 (latest data) if not specified.
    """
    prompt = f"""This question is about a specific month: "{question}"

Our data covers September 2016 to August 2018.
If the question mentions a specific month/year, extract it.
If not specified, use 2018-08 (the most recent month).

Respond ONLY in this JSON format: {{"year": 2018, "month": 8}}"""

    response_text = safe_generate(prompt)
    text = response_text.strip().replace('```json', '').replace('```', '').strip()
    return json.loads(text)


def route_question(question):
    """
    Main router - decides which agent handles this question.
    """
    print(f"Question: {question}")

    category = classify_question(question)
    print(f"Router decision: {category}\n")

    if category == "root_cause":
        date_info = extract_year_month(question)
        facts = insigt_why_agent.find_root_cause(date_info['year'], date_info['month'])
        answer = insigt_why_agent.explain_root_cause(facts)
        return answer

    elif category == "document_search":
        answer, sources = rag_agent.answer_from_documents(question)
        return answer

    else:  # lookup
        plan = query_agent.ask_gemini_to_plan(question)
        result = query_agent.run_calculation(plan)
        answer = query_agent.ask_gemini_to_explain(question, result)
        return answer


# ----- MAIN: Test it -----
if __name__ == "__main__":
    test_questions = [
        # "What was total revenue in 2017?",
        # "Why did revenue drop in August 2018?",
        # "What does our return policy say about furniture?",
        "What do customers say about product quality?"
    ]


    for q in test_questions:
        answer = route_question(q)
        print(f"Answer: {answer}")
        print("=" * 70)
        print()
        time.sleep(15)