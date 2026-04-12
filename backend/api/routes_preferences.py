from __future__ import annotations

import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from repositories.user_profile_repo import get_profile_by_device, upsert_profile
from repositories.metrics_repo import get_retention_stats, log_event
from repositories.news_repo import get_articles_for_device
from services.skill_gap_service import generate_skill_gap_report
from services.personalization_service import VALID_TOPICS, VALID_SENIORITY

router = APIRouter(prefix="/preferences", tags=["Preferences"])


class PreferencesRequest(BaseModel):
    preferred_topics: Optional[List[str]] = None
    blocked_topics: Optional[List[str]] = None
    seniority_level: Optional[str] = None
    notify_enabled: Optional[bool] = None
    quiet_hour_start: Optional[int] = None
    quiet_hour_end: Optional[int] = None


@router.get("/topics")
def list_available_topics():
    return {"topics": VALID_TOPICS, "seniority_levels": VALID_SENIORITY}


@router.get("/{device_id}")
def get_preferences(device_id: str, db: Session = Depends(get_db)):
    profile = get_profile_by_device(db, device_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")
    return {
        "preferred_topics": json.loads(profile.preferred_topics or "[]"),
        "blocked_topics": json.loads(profile.blocked_topics or "[]"),
        "seniority_level": profile.seniority_level or "mid",
        "notify_enabled": bool(profile.notify_enabled),
        "quiet_hour_start": profile.quiet_hour_start,
        "quiet_hour_end": profile.quiet_hour_end,
    }


@router.put("/{device_id}")
def update_preferences(
    device_id: str, body: PreferencesRequest, db: Session = Depends(get_db)
):
    profile = get_profile_by_device(db, device_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")

    data = {}
    if body.preferred_topics is not None:
        data["preferred_topics"] = json.dumps(body.preferred_topics)
    if body.blocked_topics is not None:
        data["blocked_topics"] = json.dumps(body.blocked_topics)
    if body.seniority_level is not None:
        if body.seniority_level not in VALID_SENIORITY:
            raise HTTPException(status_code=400, detail=f"Invalid seniority. Use: {VALID_SENIORITY}")
        data["seniority_level"] = body.seniority_level
    if body.notify_enabled is not None:
        data["notify_enabled"] = 1 if body.notify_enabled else 0
    if body.quiet_hour_start is not None:
        data["quiet_hour_start"] = body.quiet_hour_start
    if body.quiet_hour_end is not None:
        data["quiet_hour_end"] = body.quiet_hour_end

    if not data:
        raise HTTPException(status_code=400, detail="No fields to update.")

    upsert_profile(db, device_id, data)
    return {"status": "success"}


@router.get("/{device_id}/metrics")
def get_metrics(device_id: str, db: Session = Depends(get_db)):
    """Retention metrics for the user over last 7 days."""
    stats = get_retention_stats(db, device_id)
    return {"device_id": device_id, "metrics": stats}


@router.post("/{device_id}/track")
def track_event(device_id: str, event_type: str, db: Session = Depends(get_db)):
    """Track a user event for retention metrics."""
    allowed = {"digest_open", "article_click", "news_refresh", "bookmark_add", "app_open"}
    if event_type not in allowed:
        raise HTTPException(status_code=400, detail=f"Invalid event. Use: {allowed}")
    log_event(db, device_id, event_type)
    return {"status": "success"}


@router.get("/{device_id}/skill-gap")
async def get_skill_gap(device_id: str, db: Session = Depends(get_db)):
    """Weekly skill-gap report based on user profile vs trending news."""
    profile = get_profile_by_device(db, device_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")

    skills = json.loads(profile.skills or "[]")
    seniority = profile.seniority_level or "mid"
    articles = get_articles_for_device(db, device_id, limit=30)
    article_dicts = [{"title": a.title, "description": a.description} for a in articles]

    report = await generate_skill_gap_report(skills, seniority, article_dicts)
    return {"status": "success", "report": report}
