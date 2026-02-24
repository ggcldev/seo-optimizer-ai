"""
Google SERP fetcher using googlesearch-python.
Makes real HTTP requests to google.com and returns the top N organic URLs.

Note: Google may rate-limit high-volume usage. For production with heavy use,
swap to SerpAPI (100 free searches/month) by setting SERPAPI_KEY in secrets.toml
and uncommenting the serpapi branch below.
"""
import time
from googlesearch import search


# Maps short location codes to Google gl/hl params
LOCATION_MAP = {
    "ph": {"gl": "ph", "hl": "tl"},
    "us": {"gl": "us", "hl": "en"},
    "uk": {"gl": "gb", "hl": "en"},
    "au": {"gl": "au", "hl": "en"},
    "global": {"gl": "", "hl": "en"},
}


def get_serp_urls(keyword: str, location: str = "ph", n: int = 10) -> list[str]:
    """
    Return up to `n` organic Google SERP URLs for the given keyword.

    Args:
        keyword:  The search query / target keyword.
        location: Short location code (ph, us, uk, au, global).
        n:        Number of results to return.

    Returns:
        List of URLs (deduplicated, no ads).
    """
    loc = LOCATION_MAP.get(location, LOCATION_MAP["global"])

    urls: list[str] = []
    try:
        results = search(
            keyword,
            num_results=n + 3,       # fetch a few extra to cover any filtered results
            lang=loc["hl"],
            region=loc["gl"] or None,
            sleep_interval=1,        # polite delay between requests
            safe=None,
        )
        for url in results:
            if url and url not in urls:
                urls.append(url)
            if len(urls) >= n:
                break
    except Exception as e:
        raise RuntimeError(
            f"Google SERP fetch failed: {e}\n"
            "If you're being rate-limited, wait a few minutes or add a SERPAPI_KEY "
            "to secrets.toml and update this file to use the serpapi branch."
        )

    return urls


# ── Optional: SerpAPI branch (more reliable for production) ──────────────────
# Uncomment and set SERPAPI_KEY in .streamlit/secrets.toml to use this instead.
#
# import streamlit as st
# import requests
#
# def get_serp_urls(keyword: str, location: str = "ph", n: int = 10) -> list[str]:
#     loc = LOCATION_MAP.get(location, LOCATION_MAP["global"])
#     params = {
#         "q": keyword,
#         "gl": loc["gl"],
#         "hl": loc["hl"],
#         "num": n,
#         "api_key": st.secrets["SERPAPI_KEY"],
#     }
#     resp = requests.get("https://serpapi.com/search.json", params=params, timeout=15)
#     resp.raise_for_status()
#     data = resp.json()
#     return [r["link"] for r in data.get("organic_results", [])[:n]]
