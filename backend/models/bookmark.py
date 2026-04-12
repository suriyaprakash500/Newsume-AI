from sqlalchemy import Column, String, Text, DateTime, Integer
from sqlalchemy.sql import func

from database import Base


class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(255), nullable=False, index=True)
    article_id = Column(Integer, nullable=False)
    note = Column(Text, default="")
    created_at = Column(DateTime, server_default=func.now())
