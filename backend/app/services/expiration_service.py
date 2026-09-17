from datetime import datetime
from app.extensions import db
from app.models.food_listing import FoodListing, FoodListingStatus
from app.models.reservation import Reservation, ReservationStatus
from app.models.notification import Notification, NotificationType

def process_expired_listings():
    """
    Finds food listings past their expiry time, marks them EXPIRED,
    cancels pending reservations, and issues notifications.
    """
    now = datetime.utcnow()
    
    # Query listings that are still active but past expiry
    expired_listings = FoodListing.query.filter(
        FoodListing.status.in_([FoodListingStatus.AVAILABLE, FoodListingStatus.PARTIALLY_RESERVED]),
        FoodListing.expiry_time <= now
    ).all()
    
    expired_count = len(expired_listings)
    affected_reservations_count = 0

    for listing in expired_listings:
        listing.status = FoodListingStatus.EXPIRED

        # Notify provider
        provider_notification = Notification(
            user_id=listing.provider_id,
            title="Listing Expired",
            message=f"Your food listing '{listing.title}' has expired and is no longer available for reservations.",
            notification_type=NotificationType.EXPIRY,
            reference_id=listing.id
        )
        db.session.add(provider_notification)

        # Cancel any pending unfulfilled reservations
        pending_reservations = Reservation.query.filter(
            Reservation.food_listing_id == listing.id,
            Reservation.status.in_([ReservationStatus.PENDING, ReservationStatus.APPROVED])
        ).all()

        for res in pending_reservations:
            res.status = ReservationStatus.EXPIRED
            affected_reservations_count += 1

            recipient_notification = Notification(
                user_id=res.recipient_id,
                title="Reservation Expired",
                message=f"The listing '{listing.title}' has reached its expiration time. Reservation {res.pickup_code} is now closed.",
                notification_type=NotificationType.EXPIRY,
                reference_id=listing.id
            )
            db.session.add(recipient_notification)

    if expired_count > 0:
        db.session.commit()

    return {
        "expired_listings": expired_count,
        "affected_reservations": affected_reservations_count,
        "processed_at": now.isoformat()
    }
