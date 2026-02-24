import re


def clean_text(text: str) -> str:
    """Remove excessive whitespace and non-printable characters."""
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\x20-\x7E\n]", "", text)
    return text.strip()


def truncate(text: str, max_chars: int = 8000) -> str:
    """Truncate text to max_chars to stay within LLM context limits."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n[... truncated ...]"


def keyword_density(text: str, keyword: str) -> float:
    """Return keyword occurrences / total words as a percentage."""
    words = text.lower().split()
    if not words:
        return 0.0
    kw_lower = keyword.lower()
    count = sum(1 for w in words if kw_lower in w)
    return round(count / len(words) * 100, 2)
