from __future__ import annotations

import json
import logging

from utils.relevance_scorer import rank_articles
from services.career_impact_service import generate_career_impacts_batch
from services.personalization_service import apply_topic_filter, apply_seniority_filter

logger = logging.getLogger(__name__)


def rank_and_prepare(
    raw_articles: list[dict],
    device_id: str,
    skills: list[str],
    keywords: list[str],
    max_articles: int = 50,
    preferred_topics: list[str] | None = None,
    blocked_topics: list[str] | None = None,
    seniority: str = "mid",
) -> list[dict]:
    """Rank articles by relevance, apply personalization, stamp with device_id."""
    ranked = rank_articles(raw_articles, skills, keywords)

    ranked = apply_topic_filter(ranked, preferred_topics or [], blocked_topics or [])
    ranked = apply_seniority_filter(ranked, seniority)
    ranked.sort(key=lambda a: a.get("relevance_score", 0), reverse=True)

    result = []
    for article in ranked[:max_articles]:
        article["device_id"] = device_id
        if "source_type" not in article:
            article["source_type"] = "unknown"
        if "source_trust_score" not in article:
            article["source_trust_score"] = 0.5
        result.append(article)
    return result


async def rank_and_enrich(
    raw_articles: list[dict],
    device_id: str,
    skills: list[str],
    keywords: list[str],
    max_articles: int = 50,
    enrich_top_n: int = 5,
    preferred_topics: list[str] | None = None,
    blocked_topics: list[str] | None = None,
    seniority: str = "mid",
) -> list[dict]:
    """Rank + personalize + generate career impact cards for top articles."""
    ranked = rank_and_prepare(
        raw_articles, device_id, skills, keywords, max_articles,
        preferred_topics, blocked_topics, seniority,
    )

    try:
        top_articles = ranked[:enrich_top_n]
        impacts = await generate_career_impacts_batch(top_articles, skills, keywords, enrich_top_n)
        for article, impact in zip(top_articles, impacts):
            article["career_why"] = impact.get("why_it_matters", "")
            article["career_who"] = impact.get("who_should_care", "")
            article["career_action"] = impact.get("action_next", "")
    except Exception as e:
        logger.warning(f"Batch career enrichment failed: {e}")

    return ranked
