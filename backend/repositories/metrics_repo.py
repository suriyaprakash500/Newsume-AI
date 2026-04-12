from sqlalchemy.orm import Session
from sqlalchemy import func as sql_func
from datetime import datetime, timedelta

from models.metrics import UserMetric


def log_event(db: Session, device_id: str, event_type: str, event_data: str = ""):
    db.add(UserMetric(device_id=device_id, event_type=event_type, event_data=event_data))
    db.commit()


def get_event_count(
    db: Session, device_id: str, event_type: str, since_days: int = 7
) -> int:
    cutoff = datetime.utcnow() - timedelta(days=since_days)
    return (
        db.query(UserMetric)
        .filter(
            UserMetric.device_id == device_id,
            UserMetric.event_type == event_type,
            UserMetric.created_at >= cutoff,
        )
        .count()
    )


def get_retention_stats(db: Session, device_id: str) -> dict:
    now = datetime.utcnow()
    return {
        "digest_opens_7d": get_event_count(db, device_id, "digest_open", 7),
        "article_clicks_7d": get_event_count(db, device_id, "article_click", 7),
        "refreshes_7d": get_event_count(db, device_id, "news_refresh", 7),
        "bookmarks_7d": get_event_count(db, device_id, "bookmark_add", 7),
        "active_days_7d": _active_days(db, device_id, 7),
    }


def _active_days(db: Session, device_id: str, days: int) -> int:
    cutoff = datetime.utcnow() - timedelta(days=days)
    result = (
        db.query(sql_func.count(sql_func.distinct(sql_func.date(UserMetric.created_at))))
        .filter(
            UserMetric.device_id == device_id,
            UserMetric.created_at >= cutoff,
        )
        .scalar()
    )
    return result or 0
