from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from repositories.bookmark_repo import add_bookmark, remove_bookmark, get_bookmarks
from repositories.news_repo import get_article_by_id

router = APIRouter(prefix="/bookmarks", tags=["Bookmarks"])


class BookmarkRequest(BaseModel):
    article_id: int
    note: str = ""


@router.post("/{device_id}")
def create_bookmark(device_id: str, body: BookmarkRequest, db: Session = Depends(get_db)):
    bm = add_bookmark(db, device_id, body.article_id, body.note)
    return {"status": "success", "bookmark_id": bm.id}


@router.delete("/{device_id}/{article_id}")
def delete_bookmark(device_id: str, article_id: int, db: Session = Depends(get_db)):
    removed = remove_bookmark(db, device_id, article_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Bookmark not found.")
    return {"status": "success"}


@router.get("/{device_id}")
def list_bookmarks(device_id: str, db: Session = Depends(get_db)):
    bookmarks = get_bookmarks(db, device_id)
    result = []
    for bm in bookmarks:
        article = get_article_by_id(db, bm.article_id)
        result.append({
            "bookmark_id": bm.id,
            "article_id": bm.article_id,
            "note": bm.note,
            "created_at": str(bm.created_at),
            "article": {
                "title": article.title if article else "",
                "url": article.url if article else "",
                "source_name": article.source_name if article else "",
            } if article else None,
        })
    return {"count": len(result), "bookmarks": result}
