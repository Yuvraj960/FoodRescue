import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler(daemon=True)

def init_scheduler(app):
    """
    Initializes a resilient local background scheduler that periodically
    checks for expired food listings and handles automated notifications.
    This runs seamlessly during local development on Windows without requiring
    an external Redis server, while Celery is also available for production.
    """
    if not app.config.get("ENABLE_LOCAL_SCHEDULER", True):
        return

    def run_expiration_check():
        with app.app_context():
            try:
                from app.services.expiration_service import process_expired_listings
                res = process_expired_listings()
                if res.get("expired_listings", 0) > 0:
                    logger.info(f"[Scheduler] Auto-expired listings: {res}")
            except Exception as e:
                logger.error(f"[Scheduler] Error running expiration check: {e}")

    # Run every 60 seconds
    scheduler.add_job(
        func=run_expiration_check,
        trigger=IntervalTrigger(seconds=60),
        id="auto_expire_food_job",
        name="Check and expire food listings every 60s",
        replace_existing=True
    )

    if not scheduler.running:
        scheduler.start()
        logger.info("[Scheduler] Local background scheduler started successfully.")
