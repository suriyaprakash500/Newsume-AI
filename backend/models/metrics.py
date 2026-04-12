from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.sql import func

from database import Base


class UserMetric(Base):
    __tablename__ = "user_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(255), nullable=False, index=True)
    event_type = Column(String(100), nullable=False)
    event_data = Column(String(500), default="")
    created_at = Column(DateTime, server_default=func.now())
