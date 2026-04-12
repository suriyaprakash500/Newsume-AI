import httpx

from config.settings import settings

_NEWS_API_BASE = "https://newsapi.org/v2"


async def fetch_tech_news_for_queries(queries: list[str], max_per_query: int = 10) -> list[dict]:
    """
    Fetch articles from NewsAPI for each query term.
    Deduplicates by URL across all queries.
    """
    if not settings.news_api_key:
        return []

    seen_urls: set[str] = set()
    all_articles: list[dict] = []

    async with httpx.AsyncClient(timeout=30.0) as client:
        for query in queries[:10]:
            params = {
                "q": query,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": max_per_query,
                "apiKey": settings.news_api_key,
            }
            try:
                resp = await client.get(f"{_NEWS_API_BASE}/everything", params=params)
                resp.raise_for_status()
                data = resp.json()
            except (httpx.HTTPError, Exception):
                continue

            for raw in data.get("articles", []):
                url = raw.get("url", "")
                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)
                all_articles.append({
                    "title": raw.get("title", ""),
                    "description": raw.get("description", ""),
                    "url": url,
                    "image_url": raw.get("urlToImage", "") or "",
                    "source_name": (raw.get("source") or {}).get("name", ""),
                    "author": raw.get("author", "") or "",
                    "published_at": raw.get("publishedAt", ""),
                })

    return all_articles


def build_search_queries(skills: list[str], keywords: list[str]) -> list[str]:
    """Build effective search queries from user profile terms."""
    priority_terms = skills[:5] + keywords[:3]
    queries = []
    for term in priority_terms:
        if term.strip():
            queries.append(f"{term.strip()} technology")
    if not queries:
        queries = ["latest technology news"]
    return queries
