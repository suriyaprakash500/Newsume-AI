from sqlalchemy.orm import Session

from models.bookmark import Bookmark


def add_bookmark(db: Session, device_id: str, article_id: int, note: str = "") -> Bookmark:
    existing = (
        db.query(Bookmark)
        .filter(Bookmark.device_id == device_id, Bookmark.article_id == article_id)
        .first()
    )
    if existing:
        existing.note = note
        db.commit()
        db.refresh(existing)
        return existing

    bm = Bookmark(device_id=device_id, article_id=article_id, note=note)
    db.add(bm)
    db.commit()
    db.refresh(bm)
    return bm


def remove_bookmark(db: Session, device_id: str, article_id: int) -> bool:
    deleted = (
        db.query(Bookmark)
        .filter(Bookmark.device_id == device_id, Bookmark.article_id == article_id)
        .delete()
    )
    db.commit()
    return deleted > 0


def get_bookmarks(db: Session, device_id: str) -> list[Bookmark]:
    return (
        db.query(Bookmark)
        .filter(Bookmark.device_id == device_id)
        .order_by(Bookmark.created_at.desc())
        .all()
    )
