# Known Limitations & Future Work

## 1. Category/Entity-Specific Recommendation Questions
Questions like "How can we improve revenue in the Furniture category?" are 
currently routed to the root_cause path, which performs a fixed overall 
month-over-month comparison and does not filter by the specific category 
mentioned in the question.

**Root cause:** `find_root_cause()` only accepts year/month parameters - 
it has no mechanism to extract or filter by category, city, or other 
entities mentioned in the question.

**Observed example:** "How should we improve revenue in coming years" was 
classified as `lookup`, triggered the `compare_periods` operation with no 
extractable time period, and returned "Period 1 and Period 2 both 
registered at 0.00" - a technically-calculated but meaningless answer, 
since the question has no concrete date to compare against.

**Scoping decision:** This represents a 4th distinct reasoning pattern 
(recommendation/strategy) beyond lookup, root-cause, and comparison. 
Given project timeline, this was deliberately deferred in favor of 
building RAG-based document retrieval, which was prioritized higher.

**Future fix:** Extend question parsing to extract entity filters 
(category, city), add filtered comparison logic, and build a dedicated 
recommendation reasoning path that considers category-specific drivers 
(pricing, review scores, delivery performance) rather than reusing 
root-cause logic.

## 2. Single-Dataset Scope (By Design)

PulseIQ is currently built around a deep, accurate understanding of one 
business domain (e-commerce transactions, the Olist dataset) - agents, 
RAG documents, and chart logic all assume this specific schema 
(product categories, cities, reviews, etc.).

**Why this was a deliberate choice:** A tool that works shallowly across 
*any* uploaded dataset is a fundamentally different and harder problem 
than one that works deeply and accurately on a known domain. Generic 
dataset support requires dynamic schema detection, adaptive agent 
prompting, and column-meaning inference - genuinely complex AI problems 
that dedicated products (e.g. Code Interpreter-style tools) invest 
significant engineering effort into solving well.

**Future enhancement:** Extend PulseIQ to support arbitrary uploaded 
datasets via:
- Automatic schema/column-type detection on upload
- Dynamic prompt construction based on detected schema (rather than 
  hardcoded column names)
- Adaptive chart selection based on column types present
- A generalized RAG ingestion step for any uploaded unstructured text

This was deliberately scoped out in favor of building deep, verifiable, 
domain-specific accuracy within the project timeline.