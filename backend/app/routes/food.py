from datetime import datetime
from dateutil import parser
from flask import Blueprint, request, jsonify, g
from app.extensions import db
from app.models.food_listing import FoodListing, FoodCategory, FoodListingStatus, DietaryType
from app.models.reservation import Reservation, ReservationStatus
from app.models.notification import Notification, NotificationType
from app.utils.auth import jwt_required, roles_required
from app.services.matching_service import match_recipients_for_listing
from app.services.expiration_service import process_expired_listings

food_bp = Blueprint("food", __name__, url_prefix="/api/food")

@food_bp.route("", methods=["GET"])
def list_food():
    # Process any expired listings before listing to ensure freshest state
    process_expired_listings()

    query = FoodListing.query

    # Search filter
    search = request.args.get("search", "").strip()
    if search:
        query = query.filter(
            (FoodListing.title.ilike(f"%{search}%")) |
            (FoodListing.description.ilike(f"%{search}%")) |
            (FoodListing.location.ilike(f"%{search}%"))
        )

    # Category filter
    category_id = request.args.get("category_id")
    if category_id:
        try:
            query = query.filter(FoodListing.category_id == int(category_id))
        except ValueError:
            pass

    # Dietary filter (Vegetarian, Non-Vegetarian, Vegan, Bakery, etc.)
    dietary_type = request.args.get("dietary_type", "").strip().upper()
    if dietary_type and dietary_type != "ALL":
        query = query.filter(FoodListing.dietary_type == dietary_type)

    # City filter
    city = request.args.get("city", "").strip()
    if city and city != "all":
        query = query.filter(FoodListing.city.ilike(f"%{city}%"))

    # Status filter
    status = request.args.get("status", "").strip().upper()
    only_active = request.args.get("only_active", "true").lower() == "true"

    if status:
        query = query.filter(FoodListing.status == status)
    elif only_active:
        now = datetime.utcnow()
        query = query.filter(
            FoodListing.status.in_(FoodListingStatus.ACTIVE_STATUSES),
            FoodListing.expiry_time > now,
            FoodListing.remaining_quantity > 0
        )

    # Order by nearest expiry time first
    query = query.order_by(FoodListing.expiry_time.asc())
    listings = query.all()

    return jsonify([l.to_dict() for l in listings]), 200


@food_bp.route("/<int:listing_id>", methods=["GET"])
def get_food(listing_id):
    # Process expired listings
    process_expired_listings()

    listing = FoodListing.query.get(listing_id)
    if not listing:
        return jsonify({"error": "Food listing not found"}), 404

    data = listing.to_dict()
    # Also attach approved reservations count or details if provider
    return jsonify(data), 200


@food_bp.route("", methods=["POST"])
@jwt_required
@roles_required("provider", "admin")
def create_food():
    data = request.get_json() or {}

    title = data.get("title", "").strip()
    category_id = data.get("category_id")
    quantity = data.get("quantity")
    unit = data.get("unit", "portions").strip()
    location = data.get("location", "").strip()
    city = data.get("city", "").strip()
    expiry_time_str = data.get("expiry_time")
    pickup_start_str = data.get("pickup_start")
    pickup_end_str = data.get("pickup_end")
    dietary_type = data.get("dietary_type", DietaryType.VEGETARIAN).strip().upper()

    if not title or not category_id or not quantity or not expiry_time_str or not location or not city:
        return jsonify({"error": "Title, category, quantity, location, city, and expiry time are required"}), 400

    try:
        quantity = int(quantity)
        if quantity <= 0:
            return jsonify({"error": "Quantity must be greater than zero"}), 400
    except ValueError:
        return jsonify({"error": "Quantity must be a valid integer"}), 400

    category = FoodCategory.query.get(category_id)
    if not category:
        return jsonify({"error": "Invalid food category"}), 400

    try:
        expiry_time = parser.parse(expiry_time_str)
        pickup_start = parser.parse(pickup_start_str) if pickup_start_str else datetime.utcnow()
        pickup_end = parser.parse(pickup_end_str) if pickup_end_str else expiry_time
        prepared_at = parser.parse(data.get("prepared_at")) if data.get("prepared_at") else None
    except Exception as e:
        return jsonify({"error": f"Invalid date/time format: {str(e)}"}), 400

    if expiry_time <= datetime.utcnow():
        return jsonify({"error": "Expiry time must be in the future"}), 400

    if dietary_type not in DietaryType.ALL:
        dietary_type = DietaryType.VEGETARIAN

    listing = FoodListing(
        provider_id=g.current_user.id,
        organization_id=g.current_user.organization_id,
        category_id=category_id,
        title=title,
        description=data.get("description", "").strip(),
        dietary_type=dietary_type,
        allergen_info=data.get("allergen_info", "").strip(),
        quantity=quantity,
        remaining_quantity=quantity,
        unit=unit or "portions",
        prepared_at=prepared_at,
        expiry_time=expiry_time,
        pickup_start=pickup_start,
        pickup_end=pickup_end,
        location=location,
        city=city,
        status=FoodListingStatus.AVAILABLE
    )

    db.session.add(listing)
    db.session.commit()

    # Rule-based matching: notify eligible recipients
    matched_count = match_recipients_for_listing(listing.id)

    return jsonify({
        "message": "Food listing created successfully",
        "listing": listing.to_dict(),
        "matched_recipients_notified": matched_count
    }), 201


@food_bp.route("/<int:listing_id>", methods=["PUT"])
@jwt_required
def update_food(listing_id):
    listing = FoodListing.query.get(listing_id)
    if not listing:
        return jsonify({"error": "Food listing not found"}), 404

    # Verify ownership or admin
    if listing.provider_id != g.current_user.id and g.current_user.role != "admin":
        return jsonify({"error": "Unauthorized to update this listing"}), 403

    data = request.get_json() or {}

    if "title" in data:
        listing.title = data["title"].strip()
    if "description" in data:
        listing.description = data["description"].strip()
    if "dietary_type" in data and data["dietary_type"] in DietaryType.ALL:
        listing.dietary_type = data["dietary_type"]
    if "allergen_info" in data:
        listing.allergen_info = data["allergen_info"].strip()
    if "location" in data:
        listing.location = data["location"].strip()
    if "city" in data:
        listing.city = data["city"].strip()
    if "status" in data and data["status"] in FoodListingStatus.ALL:
        listing.status = data["status"]

    if "expiry_time" in data:
        try:
            listing.expiry_time = parser.parse(data["expiry_time"])
        except Exception:
            pass

    db.session.commit()
    return jsonify({"message": "Food listing updated", "listing": listing.to_dict()}), 200


@food_bp.route("/<int:listing_id>", methods=["DELETE"])
@jwt_required
def delete_food(listing_id):
    listing = FoodListing.query.get(listing_id)
    if not listing:
        return jsonify({"error": "Food listing not found"}), 404

    if listing.provider_id != g.current_user.id and g.current_user.role != "admin":
        return jsonify({"error": "Unauthorized to delete this listing"}), 403

    listing.status = FoodListingStatus.CANCELLED

    # Cancel any pending reservations
    for res in listing.reservations:
        if res.status in [ReservationStatus.PENDING, ReservationStatus.APPROVED]:
            res.status = ReservationStatus.CANCELLED
            notif = Notification(
                user_id=res.recipient_id,
                title="Listing Cancelled by Provider",
                message=f"The listing '{listing.title}' was cancelled by the provider. Your reservation {res.pickup_code} has been cancelled.",
                notification_type=NotificationType.RESERVATION,
                reference_id=listing.id
            )
            db.session.add(notif)

    db.session.commit()
    return jsonify({"message": "Food listing cancelled successfully"}), 200
