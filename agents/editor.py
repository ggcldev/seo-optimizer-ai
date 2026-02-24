"""
Agent 3 — Content Editor
Applies the recommended edits to the original text with minimal changes.
Returns the full optimized text (not just the diff).
"""
import json
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from utils import truncate

EDITOR_PROMPT = PromptTemplate(
    input_variables=["keyword", "original_text", "edits"],
    template="""You are an expert SEO content editor. Your task is to apply specific, targeted edits to an existing page. You must NOT rewrite the page.

Target keyword: {keyword}

EDITS TO APPLY (in priority order):
{edits}

ORIGINAL PAGE TEXT:
{original_text}

Instructions:
- Apply ONLY the listed edits.
- Preserve the original text, tone, and structure everywhere else.
- When adding headings, use Markdown format (## for H2, ### for H3).
- When expanding sections, insert new sentences/paragraphs in the most natural location.
- Return the COMPLETE updated page text (not a summary, not a diff — the full text).
- Do not add a preamble or explanation — output only the page text."""
)


def run_edit(llm, keyword: str, original_text: str, edits_result: dict) -> str:
    """
    Run the Content Editor agent.

    Returns the optimized page text as a string.
    Falls back to original_text on failure.
    """
    edits = edits_result.get("edits", [])
    if not edits:
        return original_text

    edits_str = "\n".join(
        f"{e['priority']}. [{e['type'].upper()}] {e['action']} "
        f"(location: {e['location']})"
        for e in sorted(edits, key=lambda x: x.get("priority", 99))
    )

    chain = LLMChain(llm=llm, prompt=EDITOR_PROMPT)
    result = chain.run(
        keyword=keyword,
        edits=edits_str,
        original_text=truncate(original_text, 6000),
    )

    return result.strip() if result.strip() else original_text
