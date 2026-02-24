"""
Page scraper using curl_cffi + BeautifulSoup.
Extracts title, H1, H2s, body text, and word count from a URL.
"""
from curl_cffi import requests as curl_requests
from bs4 import BeautifulSoup

from utils import clean_text


# CSS selectors for noise elements to strip before extracting body text
_NOISE_SELECTORS = [
    "nav", "header", "footer", "aside",
    ".nav", ".header", ".footer", ".sidebar", ".menu",
    "#nav", "#header", "#footer", "#sidebar",
    "script", "style", "noscript", "iframe",
    ".cookie-banner", ".ad", ".advertisement",
]


def fetch_page(url: str) -> dict:
    """
    Fetch a page and extract structured content.

    Returns:
        {
            "url": str,
            "title": str,
            "h1": str,
            "h2s": list[str],
            "body_text": str,
            "word_count": int,
            "error": str | None,
        }
    """
    result = {
        "url": url,
        "title": "",
        "h1": "",
        "h2s": [],
        "body_text": "",
        "word_count": 0,
        "error": None,
    }

    try:
        resp = curl_requests.get(url, impersonate="chrome", timeout=15)
        resp.raise_for_status()
        page = BeautifulSoup(resp.text, "html.parser")
    except Exception as e:
        result["error"] = str(e)
        return result

    try:
        result["title"] = page.find("title").get_text() or ""
    except Exception:
        pass

    try:
        result["h1"] = page.find("h1").get_text() or ""
    except Exception:
        pass

    try:
        result["h2s"] = [el.get_text() for el in page.find_all("h2") if el.get_text(strip=True)]
    except Exception:
        pass

    # Strip noise elements before extracting body text
    for selector in _NOISE_SELECTORS:
        try:
            for el in page.select(selector):
                el.decompose()
        except Exception:
            pass

    try:
        body = page.find("body")
        raw_text = body.get_text() if body else page.get_text()
        result["body_text"] = clean_text(raw_text)
        result["word_count"] = len(result["body_text"].split())
    except Exception as e:
        result["error"] = str(e)

    return result


def fetch_pages_parallel(urls: list[str], max_workers: int = 4) -> list[dict]:
    """Fetch multiple pages concurrently."""
    from concurrent.futures import ThreadPoolExecutor, as_completed

    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(fetch_page, url): url for url in urls}
        for future in as_completed(future_to_url):
            results.append(future.result())
    return results
