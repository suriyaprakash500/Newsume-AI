import logging
import xml.etree.ElementTree as ET

import httpx

from config.sources import SOURCES

logger = logging.getLogger(__name__)


async def fetch_all_rss_feeds(max_per_feed: int = 15) -> list[dict]:
    """Fetch articles from all configured RSS sources."""
    rss_sources = {k: v for k, v in SOURCES.items() if v["type"] == "rss"}
    all_articles = []

    async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
        for source_key, source_config in rss_sources.items():
            try:
                articles = await _fetch_single_rss(
                    client, source_config, max_per_feed
                )
                all_articles.extend(articles)
            except Exception as e:
                logger.warning(f"RSS fetch failed for {source_config['name']}: {e}")
                continue

    return all_articles


async def _fetch_single_rss(
    client: httpx.AsyncClient, source_config: dict, max_items: int
) -> list[dict]:
    resp = await client.get(
        source_config["feed_url"],
        headers={"User-Agent": "ResumeNewsBot/1.0"},
    )
    resp.raise_for_status()

    root = ET.fromstring(resp.text)
    articles = []

    for item in root.iter("item"):
        if len(articles) >= max_items:
            break

        title = _text(item, "title")
        link = _text(item, "link")
        if not title or not link:
            continue

        description = _text(item, "description")
        if description:
            description = _strip_html(description)[:300]

        articles.append({
            "title": title,
            "description": description,
            "url": link,
            "image_url": _extract_image(item),
            "source_name": source_config["name"],
            "source_type": "rss",
            "author": _text(item, "dc:creator") or _text(item, "author") or "",
            "published_at": _text(item, "pubDate") or "",
        })

    return articles


def _text(element: ET.Element, tag: str) -> str:
    namespaces = {
        "dc": "http://purl.org/dc/elements/1.1/",
        "media": "http://search.yahoo.com/mrss/",
        "content": "http://purl.org/rss/1.0/modules/content/",
    }
    for prefix, uri in namespaces.items():
        if tag.startswith(f"{prefix}:"):
            local = tag.split(":", 1)[1]
            el = element.find(f"{{{uri}}}{local}")
            return el.text.strip() if el is not None and el.text else ""
    el = element.find(tag)
    return el.text.strip() if el is not None and el.text else ""


def _extract_image(item: ET.Element) -> str:
    media_ns = "http://search.yahoo.com/mrss/"
    media_el = item.find(f"{{{media_ns}}}content")
    if media_el is not None:
        return media_el.get("url", "")
    enclosure = item.find("enclosure")
    if enclosure is not None and "image" in (enclosure.get("type", "")):
        return enclosure.get("url", "")
    return ""


def _strip_html(text: str) -> str:
    import re
    clean = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\s+", " ", clean).strip()
