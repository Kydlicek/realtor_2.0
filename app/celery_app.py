# celery_app.py
from celery import Celery
from celery.schedules import crontab

# Initialize Celery
app = Celery(
    "tasks",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)

# Update Celery configuration
app.conf.update(
    result_expires=3600,  # Results expire after 1 hour
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Celery Beat schedule
app.conf.beat_schedule = {
    # Run scrapers every 15 minutes
    "start-all-scrapers-every-15min": {
        "task": "tasks.start_all_scrapers",
        "schedule": crontab(minute="*/15"),  # Every 15 minutes
    },

    # # Calculate financials every hour
    # "calculate-financials-every-hour": {
    #     "task": "tasks.calculate_financials_for_all_listings",
    #     "schedule": crontab(minute=0, hour="*/1"),  # Every hour at minute 0
    # },
}