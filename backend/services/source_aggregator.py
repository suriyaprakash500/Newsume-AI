from __future__ import annotations

import hashlib
import logging

from config.sources import SOURCES
from services.hn_fetcher import fetch_hn_top_stories, search_hn_algolia
from services.rss_fetcher import fetch_all_rss_feeds
from services.news_fetcher import fetch_tech_news_for_queries

logger = logging.getLogger(__name__)


async def aggregate_all_sources(search_queries: list[str]) -> list[dict]:
    """
    Fetch from all configured sources in priority order with dedup.
    Returns combined, deduplicated article list.
    """
    all_articles: list[dict] = []

    hn_top = await _safe_fetch("Hacker News Top", fetch_hn_top_stories, 30)
    all_articles.extend(hn_top)

    hn_search = await _safe_fetch(
        "Hacker News Algolia", search_hn_algolia, search_queries
    )
    all_articles.extend(hn_search)

    rss_articles = await _safe_fetch("RSS Feeds", fetch_all_rss_feeds)
    all_articles.extend(rss_articles)

    api_articles = await _safe_fetch(
        "NewsAPI", fetch_tech_news_for_queries, search_queries
    )
    for a in api_articles:
        a["source_type"] = "newsapi"
    all_articles.extend(api_articles)

    deduped = _deduplicate(all_articles)
    _stamp_trust_scores(deduped)

    logger.info(
        f"Aggregated {len(all_articles)} raw -> {len(deduped)} after dedup "
        f"from {_count_sources(deduped)} sources"
    )
    return deduped


async def _safe_fetch(label: str, fetch_fn, *args):
    try:
        return await fetch_fn(*args)
    except Exception as e:
        logger.error(f"{label} fetch failed: {e}")
        return []


def _deduplicate(articles: list[dict]) -> list[dict]:
    """Deduplicate by URL hash and title hash."""
    seen: set[str] = set()
    result = []
    for article in articles:
        url_hash = _hash(article.get("url", ""))
        title_hash = _hash(article.get("title", "").lower().strip())
        if url_hash in seen or title_hash in seen:
            continue
        seen.add(url_hash)
        seen.add(title_hash)
        result.append(article)
    return result


def _stamp_trust_scores(articles: list[dict]):
    """Attach source_trust_score from config."""
    source_name_to_trust = {v["name"]: v["trust_score"] for v in SOURCES.values()}
    for article in articles:
        name = article.get("source_name", "")
        article["source_trust_score"] = source_name_to_trust.get(name, 0.5)


def _hash(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()


def _count_sources(articles: list[dict]) -> int:
    return len({a.get("source_name", "") for a in articles})
