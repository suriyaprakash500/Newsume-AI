from sqlalchemy import Column, String, Text, DateTime, Integer, Float
from sqlalchemy.sql import func

from database import Base


class NewsArticle(Base):
    __tablename__ = "news_articles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(255), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, default="")
    url = Column(String(1000), nullable=False)
    image_url = Column(String(1000), default="")
    source_name = Column(String(255), default="")
    source_type = Column(String(50), default="api")
    source_trust_score = Column(Float, default=0.5)
    author = Column(String(255), default="")
    published_at = Column(String(100), default="")
    relevance_score = Column(Float, default=0.0)
    matched_skills = Column(Text, default="[]")
    career_why = Column(Text, default="")
    career_who = Column(Text, default="")
    career_action = Column(Text, default="")
    fetched_at = Column(DateTime, server_default=func.now())


class ArticleReadState(Base):
    __tablename__ = "article_read_states"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(255), nullable=False, index=True)
    article_id = Column(Integer, nullable=False, index=True)
    read_at = Column(DateTime, server_default=func.now())
