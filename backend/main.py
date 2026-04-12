import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from database import init_db
from config.settings import settings
from api.routes_resume import router as resume_router
from api.routes_news import router as news_router
from api.routes_bookmarks import router as bookmarks_router
from api.routes_preferences import router as preferences_router
from services.scheduler_service import run_daily_job

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    import models  # noqa: F401 — register all ORM models before create_all()
    init_db()
    logger.info("Database initialized.")

    scheduler.add_job(
        run_daily_job,
        trigger=CronTrigger(
            hour=settings.daily_fetch_hour,
            minute=settings.daily_fetch_minute,
            timezone=settings.scheduler_timezone,
        ),
        id="daily_news_job",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(
        f"Scheduler started — daily job at "
        f"{settings.daily_fetch_hour:02d}:{settings.daily_fetch_minute:02d} "
        f"({settings.scheduler_timezone})"
    )

    yield

    scheduler.shutdown()
    logger.info("Scheduler shut down.")


app = FastAPI(
    title="Newsume AI API",
    description="An AI that reads your resume and delivers personalized news",
    version="2.0.0",
    lifespan=lifespan,
)

app.include_router(resume_router)
app.include_router(news_router)
app.include_router(bookmarks_router)
app.include_router(preferences_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=True)
