from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "stayagg",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    beat_schedule={
        "sync-calendars-every-hour": {
            "task": "app.workers.tasks.sync_all_calendars",
            "schedule": 3600.0,
        },
        "scrape-listings-daily": {
            "task": "app.workers.tasks.scrape_all_platforms",
            "schedule": 86400.0,
        },
    },
)
