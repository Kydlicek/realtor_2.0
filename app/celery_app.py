# celery_app.py
from celery import Celery
from celery.schedules import crontab

# Initialize Celery app
app = Celery("tasks", broker="redis://redis:6379/0", backend="redis://redis:6379/0")

# Update Celery configuration
app.conf.update(
    result_expires=3600,  # Results expire after 1 hour
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Change this line - don't use "app" as a prefix
app.autodiscover_tasks(["tasks"])

# Celery Beat schedule
app.conf.beat_schedule = {
    # Run scrapers every 15 minutes
    "start-all-scrapers-every-15min": {
        "task": "tasks.start_all_scrapers",
        "schedule": crontab(minute="*/15"),  # Every 15 minutes
    },
}
