import logging
import httpx

logger = logging.getLogger(__name__)

_HN_FIREBASE = "https://hacker-news.firebaseio.com/v0"
_HN_ALGOLIA = "https://hn.algolia.com/api/v1"


async def fetch_hn_top_stories(max_items: int = 30) -> list[dict]:
    """Fetch top stories from HN Firebase API (no auth, no limits)."""
    articles = []
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(f"{_HN_FIREBASE}/topstories.json")
            resp.raise_for_status()
            story_ids = resp.json()[:max_items]

            for sid in story_ids:
                try:
                    item_resp = await client.get(f"{_HN_FIREBASE}/item/{sid}.json")
                    item = item_resp.json()
                    if not item or item.get("type") != "story" or not item.get("url"):
                        continue
                    articles.append(_hn_item_to_article(item))
                except Exception:
                    continue
    except Exception as e:
        logger.error(f"HN Firebase fetch failed: {e}")
    return articles


async def search_hn_algolia(queries: list[str], max_per_query: int = 10) -> list[dict]:
    """Search HN via Algolia for keyword-based stories (no auth, no limits)."""
    seen_urls: set[str] = set()
    articles = []

    async with httpx.AsyncClient(timeout=20.0) as client:
        for query in queries[:5]:
            try:
                params = {
                    "query": query,
                    "tags": "story",
                    "hitsPerPage": max_per_query,
                }
                resp = await client.get(f"{_HN_ALGOLIA}/search", params=params)
                resp.raise_for_status()
                data = resp.json()

                for hit in data.get("hits", []):
                    url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"
                    if url in seen_urls:
                        continue
                    seen_urls.add(url)
                    articles.append({
                        "title": hit.get("title", ""),
                        "description": hit.get("story_text", "")[:300] if hit.get("story_text") else "",
                        "url": url,
                        "image_url": "",
                        "source_name": "Hacker News",
                        "source_type": "hn_algolia",
                        "author": hit.get("author", ""),
                        "published_at": hit.get("created_at", ""),
                    })
            except Exception as e:
                logger.warning(f"HN Algolia search failed for '{query}': {e}")
                continue
    return articles


def _hn_item_to_article(item: dict) -> dict:
    return {
        "title": item.get("title", ""),
        "description": "",
        "url": item.get("url", ""),
        "image_url": "",
        "source_name": "Hacker News",
        "source_type": "hacker_news",
        "author": item.get("by", ""),
        "published_at": "",
    }
