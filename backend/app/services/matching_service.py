from app.extensions import db
from app.models.user import User, UserRole, UserPreference
from app.models.food_listing import FoodListing
from app.models.notification import Notification, NotificationType

def match_recipients_for_listing(listing_id):
    """
    Rule-based recipient matching:
    Identifies recipients whose preferences (city or dietary category)
    match the newly posted listing, and dispatches notifications.
    """
    listing = FoodListing.query.get(listing_id)
    if not listing:
        return 0

    # Query active recipients
    recipients = User.query.filter_by(role=UserRole.RECIPIENT, is_active=True).all()
    matched_count = 0

    for recipient in recipients:
        pref = recipient.preference
        matched = False

        if pref:
            # Match by city
            if pref.city and pref.city.lower() == listing.city.lower():
                matched = True
            
            # Match by category preference
            if pref.preferred_category_ids and listing.category_id in pref.preferred_category_ids:
                matched = True
            
            # Match by dietary filter
            if pref.dietary_filter and pref.dietary_filter.upper() == listing.dietary_type.upper():
                matched = True
        else:
            # Default: match if user city matches listing city
            if recipient.city and recipient.city.lower() == listing.city.lower():
                matched = True

        if matched:
            notif = Notification(
                user_id=recipient.id,
                title="Matching Food Available Nearby!",
                message=f"Surplus food matching your preferences: '{listing.title}' ({listing.quantity} {listing.unit}, {listing.dietary_type}) is available at {listing.location}, {listing.city}.",
                notification_type=NotificationType.MATCH,
                reference_id=listing.id
            )
            db.session.add(notif)
            matched_count += 1

    if matched_count > 0:
        db.session.commit()

    return matched_count
