"""
Agent 2 — Gap Analyzer
Takes the audit result and produces a prioritized list of specific, actionable edits.
"""
import json
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence

from utils import truncate

GAP_PROMPT = PromptTemplate(
    input_variables=["keyword", "audit", "missing_keywords", "missing_entities"],
    template="""You are an expert SEO content strategist.

Target keyword: {keyword}

CONTENT AUDIT RESULT:
{audit}

MISSING KEYWORDS (found in competitors, absent from your page):
{missing_keywords}

MISSING ENTITIES (named entities found in competitors, absent from your page):
{missing_entities}

Your job: produce a precise, prioritized list of edits the writer should make.
Rules:
- Do NOT suggest a full rewrite.
- Each edit must be specific (say exactly WHAT to add/change and WHERE).
- Include approximate word targets where relevant.
- Limit to the 8 most impactful edits.

Return ONLY valid JSON:
{{
  "edits": [
    {{
      "priority": <int 1-8>,
      "type": "add_heading|expand_section|add_keywords|add_entities|restructure|other",
      "location": "<where in the page: intro / section title / after H2 X / etc.>",
      "action": "<exactly what to do, e.g. Add H2: 'Best SEO Tools in the Philippines 2025'>",
      "rationale": "<why this matters for ranking>"
    }}
  ]
}}

Return ONLY the JSON object, no markdown fences, no explanation."""
)


def run_gap_analysis(llm, keyword: str, audit: dict, gaps: dict) -> dict:
    """
    Run the Gap Analyzer agent.

    Returns a dict with an "edits" list.
    Falls back to {"edits": [], "raw_output": ..., "parse_error": True} on failure.
    """
    audit_str = json.dumps(audit, indent=2)
    missing_kws = ", ".join(gaps.get("missing_keywords", [])[:15])
    missing_ents = ", ".join(gaps.get("missing_entities", [])[:15])

    chain = GAP_PROMPT | llm
    raw = chain.invoke({
        "keyword": keyword,
        "audit": truncate(audit_str, 3000),
        "missing_keywords": missing_kws or "none detected",
        "missing_entities": missing_ents or "none detected",
    }).content

    try:
        clean = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        return json.loads(clean)
    except json.JSONDecodeError:
        return {"edits": [], "raw_output": raw, "parse_error": True}
