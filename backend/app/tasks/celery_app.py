import os
from celery import Celery
from celery.schedules import crontab

def make_celery(app_name=__name__):
    broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
    result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    
    celery = Celery(
        app_name,
        broker=broker_url,
        backend=result_backend,
        include=["app.tasks.celery_tasks"]
    )
    
    celery.conf.update(
        timezone="UTC",
        enable_utc=True,
        beat_schedule={
            "check-expired-listings-every-minute": {
                "task": "app.tasks.celery_tasks.check_expired_listings_task",
                "schedule": 60.0,  # Run every minute
            },
            "generate-daily-impact-report": {
                "task": "app.tasks.celery_tasks.generate_daily_impact_task",
                "schedule": crontab(hour=0, minute=0),  # Run at midnight
            }
        }
    )
    return celery

celery_app = make_celery("foodrescue")
