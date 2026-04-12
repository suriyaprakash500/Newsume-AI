from __future__ import annotations

import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from config.sources import PAGE_SIZE
from database import get_db
from repositories.news_repo import (
    get_unread_articles,
    get_articles_for_device,
    mark_articles_read,
    get_unread_count,
    save_articles,
)
from repositories.user_profile_repo import get_profile_by_device
from services.source_aggregator import aggregate_all_sources
from services.news_fetcher import build_search_queries
from services.news_ranker import rank_and_enrich
from services.career_impact_service import generate_daily_digest

router = APIRouter(prefix="/news", tags=["News"])


def _serialize_article(a) -> dict:
    return {
        "id": a.id,
        "title": a.title,
        "description": a.description,
        "url": a.url,
        "image_url": a.image_url,
        "source_name": a.source_name,
        "source_type": a.source_type or "",
        "source_trust_score": a.source_trust_score or 0.5,
        "author": a.author,
        "published_at": a.published_at,
        "relevance_score": a.relevance_score,
        "matched_skills": json.loads(a.matched_skills or "[]"),
        "career_why": a.career_why or "",
        "career_who": a.career_who or "",
        "career_action": a.career_action or "",
    }


@router.get("/{device_id}")
def get_news_unread(
    device_id: str,
    limit: int = Query(default=PAGE_SIZE, le=50),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    """Get next batch of unread articles (offset-based pagination)."""
    articles = get_unread_articles(db, device_id, limit, offset)
    unread_total = get_unread_count(db, device_id)
    return {
        "count": len(articles),
        "unread_total": unread_total,
        "articles": [_serialize_article(a) for a in articles],
    }


@router.get("/{device_id}/all")
def get_news_all(
    device_id: str,
    limit: int = Query(default=PAGE_SIZE, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    """Get all articles (including read), traditional pagination."""
    articles = get_articles_for_device(db, device_id, limit, offset)
    return {
        "count": len(articles),
        "articles": [_serialize_article(a) for a in articles],
    }


class MarkReadRequest(BaseModel):
    article_ids: List[int]


@router.post("/{device_id}/mark-read")
def mark_read(device_id: str, body: MarkReadRequest, db: Session = Depends(get_db)):
    """Mark specific articles as read/seen."""
    mark_articles_read(db, device_id, body.article_ids)
    return {"status": "success", "marked": len(body.article_ids)}


@router.post("/{device_id}/refresh")
async def refresh_news(device_id: str, db: Session = Depends(get_db)):
    """Fetch from all sources, rank, enrich, and store new articles."""
    profile = get_profile_by_device(db, device_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found. Upload resume first.")

    skills = json.loads(profile.skills or "[]")
    keywords = json.loads(profile.keywords or "[]")
    preferred = json.loads(profile.preferred_topics or "[]")
    blocked = json.loads(profile.blocked_topics or "[]")
    seniority = profile.seniority_level or "mid"

    queries = build_search_queries(skills, keywords)
    raw_articles = await aggregate_all_sources(queries)
    ranked = await rank_and_enrich(
        raw_articles, device_id, skills, keywords,
        preferred_topics=preferred, blocked_topics=blocked, seniority=seniority,
    )
    saved = save_articles(db, ranked)

    return {"status": "success", "new_articles": len(saved)}


@router.get("/{device_id}/digest")
async def get_daily_digest(device_id: str, db: Session = Depends(get_db)):
    """Generate a 2-minute daily career digest from recent articles."""
    profile = get_profile_by_device(db, device_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")

    skills = json.loads(profile.skills or "[]")
    articles = get_unread_articles(db, device_id, limit=10)

    article_dicts = [
        {"title": a.title, "description": a.description} for a in articles
    ]
    digest = await generate_daily_digest(article_dicts, skills)
    return {"status": "success", "digest": digest}
