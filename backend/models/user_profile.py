from sqlalchemy import Column, String, Text, DateTime, Integer
from sqlalchemy.sql import func

from database import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), default="")
    email = Column(String(255), default="")
    skills = Column(Text, default="[]")
    certifications = Column(Text, default="[]")
    experience = Column(Text, default="[]")
    education = Column(Text, default="[]")
    keywords = Column(Text, default="[]")
    raw_text = Column(Text, default="")
    resume_filename = Column(String(255), default="")
    version = Column(Integer, default=1)
    fcm_token = Column(String(512), default="")

    # Personalization preferences
    preferred_topics = Column(Text, default="[]")
    blocked_topics = Column(Text, default="[]")
    seniority_level = Column(String(50), default="mid")

    # Notification preferences
    notify_enabled = Column(Integer, default=1)
    quiet_hour_start = Column(Integer, default=22)
    quiet_hour_end = Column(Integer, default=7)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
