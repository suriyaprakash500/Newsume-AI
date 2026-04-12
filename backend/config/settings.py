from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    news_api_key: str = ""
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    fcm_server_key: str = ""  # FCM legacy server key (lightweight, no SDK needed)

    database_url: str = "sqlite:///./resume_news.db"
    scheduler_timezone: str = "Asia/Kolkata"
    daily_fetch_hour: int = 9
    daily_fetch_minute: int = 0

    host: str = "0.0.0.0"
    port: int = 8000

    class Config:
        env_file = ".env"


settings = Settings()
