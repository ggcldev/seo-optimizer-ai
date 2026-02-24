"""
Keyword and content analysis using YAKE and lightweight NER.
"""
import re
import yake

from utils import keyword_density

# Lazy-load models (cached after first call)
_kw_extractor = None


def _get_yake():
    global _kw_extractor
    if _kw_extractor is None:
        _kw_extractor = yake.KeywordExtractor(
            lan="en", n=3, dedupLim=0.7, top=15, features=None
        )
    return _kw_extractor


def _extract_entities(text: str) -> list[str]:
    """
    Lightweight named-entity extraction using capitalized phrase patterns.
    Finds proper nouns and multi-word capitalized phrases (e.g. company names,
    place names, product names) without requiring spaCy.
    """
    # Match sequences of 1-4 capitalized words (not at sentence start)
    # e.g. "Google Search Console", "United States", "Neil Patel"
    pattern = r'(?<=[.!?]\s|,\s|;\s|\n)([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})'
    matches = re.findall(pattern, text)

    # Also match mid-sentence capitalized phrases (more reliable indicator)
    mid_pattern = r'(?<=\s)([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})'
    matches += re.findall(mid_pattern, text)

    # Deduplicate and filter noise
    stop_phrases = {
        "The", "This", "That", "These", "Those", "There", "Here",
        "However", "Therefore", "Moreover", "Furthermore", "Additionally",
        "Meanwhile", "Nevertheless", "Although", "Because", "Since",
        "While", "Where", "When", "Which", "What", "How", "Why",
        "According", "Also", "Another", "Before", "After", "During",
    }
    seen = set()
    entities = []
    for m in matches:
        m_clean = m.strip()
        if m_clean and m_clean not in seen and m_clean.split()[0] not in stop_phrases:
            seen.add(m_clean)
            entities.append(m_clean)
        if len(entities) >= 30:
            break

    return entities


def analyze_content(text: str, keyword: str) -> dict:
    """
    Run full keyword + entity analysis on a page's body text.

    Returns:
        {
            "word_count": int,
            "keyword_density": float,          # percentage
            "entities": list[str],             # unique named entities
            "top_keywords_yake": list[str],    # YAKE top-10 keyphrases
            "semantic_keywords": list[str],    # YAKE extended (top 11-20)
        }
    """
    if not text.strip():
        return {
            "word_count": 0,
            "keyword_density": 0.0,
            "entities": [],
            "top_keywords_yake": [],
            "semantic_keywords": [],
        }

    word_count = len(text.split())
    density = keyword_density(text, keyword)

    # Named entities via pattern matching
    entities = _extract_entities(text)

    # YAKE keywords — top 10 primary, next 10 as "semantic"
    kw_extractor = _get_yake()
    yake_kws = kw_extractor.extract_keywords(text)
    top_keywords_yake = [kw for kw, _score in yake_kws[:10]]
    semantic_keywords = [kw for kw, _score in yake_kws[10:20]]

    return {
        "word_count": word_count,
        "keyword_density": density,
        "entities": entities,
        "top_keywords_yake": top_keywords_yake,
        "semantic_keywords": semantic_keywords,
    }


def compute_gaps(your: dict, serp_pages: list[dict]) -> dict:
    """
    Compare your page analysis against SERP competitor analyses.

    Args:
        your:       analyze_content() result for your page.
        serp_pages: list of analyze_content() results for each SERP competitor.

    Returns:
        {
            "word_count_gap": int,          # your - serp_avg (negative = you're short)
            "keyword_density_gap": float,
            "serp_avg_word_count": int,
            "serp_top_word_count": int,
            "missing_entities": list[str],
            "missing_keywords": list[str],
        }
    """
    if not serp_pages:
        return {}

    serp_word_counts = [p["word_count"] for p in serp_pages if p["word_count"] > 0]
    serp_avg_wc = int(sum(serp_word_counts) / len(serp_word_counts)) if serp_word_counts else 0
    serp_top_wc = max(serp_word_counts) if serp_word_counts else 0

    serp_densities = [p["keyword_density"] for p in serp_pages if p["keyword_density"] > 0]
    serp_avg_density = round(sum(serp_densities) / len(serp_densities), 2) if serp_densities else 0.0

    # Aggregate all SERP entities and keywords
    all_serp_entities: set[str] = set()
    all_serp_keywords: set[str] = set()
    for p in serp_pages:
        all_serp_entities.update(e.lower() for e in p.get("entities", []))
        all_serp_keywords.update(k.lower() for k in p.get("top_keywords_yake", []))
        all_serp_keywords.update(k.lower() for k in p.get("semantic_keywords", []))

    your_entities = {e.lower() for e in your.get("entities", [])}
    your_keywords = {k.lower() for k in your.get("top_keywords_yake", [])}
    your_keywords.update(k.lower() for k in your.get("semantic_keywords", []))

    missing_entities = sorted(all_serp_entities - your_entities)[:20]
    missing_keywords = sorted(all_serp_keywords - your_keywords)[:20]

    return {
        "word_count_gap": your["word_count"] - serp_avg_wc,
        "keyword_density_gap": round(your["keyword_density"] - serp_avg_density, 2),
        "serp_avg_word_count": serp_avg_wc,
        "serp_top_word_count": serp_top_wc,
        "missing_entities": missing_entities,
        "missing_keywords": missing_keywords,
    }
