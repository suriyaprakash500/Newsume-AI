from __future__ import annotations

from sqlalchemy.orm import Session

from models.news_article import NewsArticle, ArticleReadState
from config.sources import PAGE_SIZE


def get_article_by_id(db: Session, article_id: int) -> NewsArticle | None:
    return db.query(NewsArticle).filter(NewsArticle.id == article_id).first()


def save_articles(db: Session, articles: list[dict]) -> list[NewsArticle]:
    saved = []
    for article_data in articles:
        existing = (
            db.query(NewsArticle)
            .filter(
                NewsArticle.device_id == article_data["device_id"],
                NewsArticle.url == article_data["url"],
            )
            .first()
        )
        if existing:
            continue
        article = NewsArticle(**article_data)
        db.add(article)
        saved.append(article)
    db.commit()
    return saved


def get_unread_articles(
    db: Session, device_id: str, limit: int = PAGE_SIZE, offset: int = 0
) -> list[NewsArticle]:
    """Return unread articles for a device, offset-based pagination by relevance."""
    read_ids_subq = (
        db.query(ArticleReadState.article_id)
        .filter(ArticleReadState.device_id == device_id)
        .subquery()
    )
    return (
        db.query(NewsArticle)
        .filter(
            NewsArticle.device_id == device_id,
            NewsArticle.id.notin_(read_ids_subq),
        )
        .order_by(NewsArticle.relevance_score.desc(), NewsArticle.fetched_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def get_articles_for_device(
    db: Session, device_id: str, limit: int = 50, offset: int = 0
) -> list[NewsArticle]:
    return (
        db.query(NewsArticle)
        .filter(NewsArticle.device_id == device_id)
        .order_by(NewsArticle.relevance_score.desc(), NewsArticle.fetched_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def mark_articles_read(db: Session, device_id: str, article_ids: list[int]):
    for aid in article_ids:
        exists = (
            db.query(ArticleReadState)
            .filter(
                ArticleReadState.device_id == device_id,
                ArticleReadState.article_id == aid,
            )
            .first()
        )
        if not exists:
            db.add(ArticleReadState(device_id=device_id, article_id=aid))
    db.commit()


def mark_all_unread_as_read(db: Session, device_id: str):
    unread = get_unread_articles(db, device_id, limit=1000)
    if unread:
        mark_articles_read(db, device_id, [a.id for a in unread])


def get_unread_count(db: Session, device_id: str) -> int:
    read_ids_subq = (
        db.query(ArticleReadState.article_id)
        .filter(ArticleReadState.device_id == device_id)
        .subquery()
    )
    return (
        db.query(NewsArticle)
        .filter(
            NewsArticle.device_id == device_id,
            NewsArticle.id.notin_(read_ids_subq),
        )
        .count()
    )


def delete_old_articles(db: Session, device_id: str, keep_count: int = 200):
    subquery = (
        db.query(NewsArticle.id)
        .filter(NewsArticle.device_id == device_id)
        .order_by(NewsArticle.fetched_at.desc())
        .limit(keep_count)
        .subquery()
    )
    db.query(NewsArticle).filter(
        NewsArticle.device_id == device_id,
        NewsArticle.id.notin_(subquery),
    ).delete(synchronize_session=False)
    db.commit()
