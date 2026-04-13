# actions/news_reader.py — ALBEDO News Reader
# Fetches latest news by category from free APIs.

import requests
from datetime import datetime


def _fetch_news_api(query: str, country: str = "us", category: str = "general") -> str:
    """Fetch news using Gemini web search (no API key needed)."""
    from actions.web_search import web_search
    return web_search({"query": f"latest {query} news {category} {datetime.now().strftime('%Y')}"})


def news_reader(
    parameters: dict,
    response=None,
    player=None,
    session_memory=None,
    speak=None,
) -> str:
    """
    News Reader — Fetch latest news by category.

    parameters:
        category : general | technology | business | sports | entertainment | science | health
        country  : us | uk | eg | sa | ae | tr | etc.
        query    : Specific topic to search for
    """
    params = parameters or {}
    category = params.get("category", "general").lower().strip()
    country = params.get("country", "us").lower().strip()
    query = params.get("query", "")

    if player:
        player.write_log(f"[News] {category}")

    if query:
        return _fetch_news_api(query, country, category)

    return _fetch_news_api(f"top {category} news", country, category)
