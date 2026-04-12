from __future__ import annotations

import json
import logging
import asyncio

from database import SessionLocal
from repositories.user_profile_repo import get_all_profiles
from repositories.news_repo import save_articles, delete_old_articles
from services.source_aggregator import aggregate_all_sources
from services.news_fetcher import build_search_queries
from services.news_ranker import rank_and_enrich
from services.notification_service import send_push_notification

logger = logging.getLogger(__name__)


async def daily_news_job():
    """Fetch, rank, enrich, and store personalized news for all user profiles."""
    logger.info("Starting daily news fetch job...")
    db = SessionLocal()
    try:
        profiles = get_all_profiles(db)
        if not profiles:
            logger.info("No user profiles found. Skipping.")
            return

        for profile in profiles:
            try:
                await _process_profile(db, profile)
            except Exception as e:
                logger.error(f"Error processing profile {profile.device_id}: {e}")
    finally:
        db.close()
    logger.info("Daily news fetch job completed.")


async def _process_profile(db, profile):
    skills = json.loads(profile.skills or "[]")
    keywords = json.loads(profile.keywords or "[]")
    preferred = json.loads(profile.preferred_topics or "[]")
    blocked = json.loads(profile.blocked_topics or "[]")
    seniority = profile.seniority_level or "mid"

    queries = build_search_queries(skills, keywords)
    raw_articles = await aggregate_all_sources(queries)

    if not raw_articles:
        logger.info(f"No articles fetched for {profile.device_id}")
        return

    ranked = await rank_and_enrich(
        raw_articles, profile.device_id, skills, keywords,
        preferred_topics=preferred, blocked_topics=blocked, seniority=seniority,
    )
    saved = save_articles(db, ranked)
    delete_old_articles(db, profile.device_id)

    logger.info(f"Saved {len(saved)} new articles for {profile.device_id}")

    if saved and profile.fcm_token:
        top_title = saved[0].title if saved else "New articles available"
        send_push_notification(
            fcm_token=profile.fcm_token,
            title="Your Daily Tech News",
            body=f"{len(saved)} new articles: {top_title}",
            data={"action": "open_news"},
            device_id=profile.device_id,
            notify_enabled=bool(profile.notify_enabled),
            quiet_start=profile.quiet_hour_start or 22,
            quiet_end=profile.quiet_hour_end or 7,
        )


def run_daily_job():
    """Synchronous wrapper for APScheduler."""
    asyncio.run(daily_news_job())
