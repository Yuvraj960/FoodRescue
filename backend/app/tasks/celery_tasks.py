import logging
from app.tasks.celery_app import celery_app
from app.extensions import db

logger = logging.getLogger(__name__)

@celery_app.task(name="app.tasks.celery_tasks.check_expired_listings_task")
def check_expired_listings_task():
    """Periodic Celery task: checks and expires food listings."""
    # Lazy import to avoid circular dependencies with Flask app context
    from app import create_app
    from app.services.expiration_service import process_expired_listings

    app = create_app()
    with app.app_context():
        logger.info("Celery running check_expired_listings_task...")
        result = process_expired_listings()
        logger.info(f"Processed expired listings: {result}")
        return result


@celery_app.task(name="app.tasks.celery_tasks.match_recipients_task")
def match_recipients_task(listing_id):
    """Celery task triggered upon listing creation to match recipients."""
    from app import create_app
    from app.services.matching_service import match_recipients_for_listing

    app = create_app()
    with app.app_context():
        logger.info(f"Celery matching recipients for listing {listing_id}...")
        count = match_recipients_for_listing(listing_id)
        logger.info(f"Matched and notified {count} recipients")
        return count


@celery_app.task(name="app.tasks.celery_tasks.generate_daily_impact_task")
def generate_daily_impact_task():
    """Celery task: aggregates daily platform impact report."""
    from datetime import date
    from app import create_app
    from app.models.impact import ImpactRecord
    from app.services.impact_service import get_impact_summary

    app = create_app()
    with app.app_context():
        summary = get_impact_summary()
        today = date.today()
        record = ImpactRecord.query.filter_by(record_date=today).first()
        if not record:
            record = ImpactRecord(record_date=today)
            db.session.add(record)

        record.meals_rescued = summary["meals_rescued"]
        record.listings_completed = summary["completed_listings"]
        record.active_providers_count = summary["active_providers"]
        record.active_recipients_count = summary["participating_orgs"]
        record.carbon_saved_kg = summary["carbon_saved_kg"]

        db.session.commit()
        return summary
