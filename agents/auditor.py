"""
Agent 1 — Content Auditor
Analyzes your page vs SERP top-10 and returns a structured audit JSON.
"""
import json
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from utils import truncate

AUDIT_PROMPT = PromptTemplate(
    input_variables=["keyword", "your_page", "serp_summary", "gaps"],
    template="""You are an expert SEO content auditor.

Target keyword: {keyword}

YOUR PAGE DATA:
{your_page}

SERP TOP-10 SUMMARY:
{serp_summary}

COMPUTED GAPS:
{gaps}

Analyze the page and return ONLY valid JSON in this exact structure:
{{
  "overall_score": <int 0-100>,
  "metrics": {{
    "word_count": {{"yours": <int>, "serp_avg": <int>, "serp_top": <int>, "status": "ok|low|very_low"}},
    "keyword_density": {{"yours": <float>, "serp_avg": <float>, "status": "ok|low|high"}},
    "heading_coverage": {{"yours": <int count>, "serp_avg": <float>, "status": "ok|low"}},
    "entity_coverage": {{"missing_count": <int>, "status": "ok|gaps"}}
  }},
  "gaps": [
    "<specific gap description 1>",
    "<specific gap description 2>"
  ],
  "strengths": [
    "<what the page already does well>"
  ]
}}

Return ONLY the JSON object, no markdown fences, no explanation."""
)


def run_audit(llm, keyword: str, your_page: dict, serp_pages: list[dict], gaps: dict) -> dict:
    """
    Run the Content Auditor agent.

    Returns a dict matching the audit JSON schema above.
    Falls back to a minimal dict on parse errors.
    """
    # Summarise SERP into compact text to stay within context
    serp_lines = []
    for i, p in enumerate(serp_pages[:10], 1):
        serp_lines.append(
            f"[{i}] {p.get('url','')} | WC:{p.get('word_count',0)} | "
            f"H2s:{len(p.get('h2s',[]))} | KW density:{p.get('keyword_density',0)}%"
        )
    serp_summary = "\n".join(serp_lines)

    your_page_str = (
        f"URL: {your_page.get('url','')}\n"
        f"Title: {your_page.get('title','')}\n"
        f"H1: {your_page.get('h1','')}\n"
        f"H2s: {', '.join(your_page.get('h2s',[]))}\n"
        f"Word count: {your_page.get('word_count',0)}\n"
        f"Keyword density: {your_page.get('keyword_density',0)}%\n"
        f"Top keywords: {', '.join(your_page.get('top_keywords_yake',[]))}\n"
        f"Semantic keywords: {', '.join(your_page.get('semantic_keywords',[]))}"
    )

    gaps_str = json.dumps(gaps, indent=2)

    chain = LLMChain(llm=llm, prompt=AUDIT_PROMPT)
    raw = chain.run(
        keyword=keyword,
        your_page=truncate(your_page_str, 3000),
        serp_summary=truncate(serp_summary, 2000),
        gaps=truncate(gaps_str, 1000),
    )

    try:
        # Strip any accidental markdown fences
        clean = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        return json.loads(clean)
    except json.JSONDecodeError:
        return {"raw_output": raw, "parse_error": True}
