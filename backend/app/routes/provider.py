from flask import Blueprint, request, jsonify, g
from app.extensions import db
from app.models.food_listing import FoodListing, FoodListingStatus
from app.models.reservation import Reservation, ReservationStatus
from app.models.notification import Notification, NotificationType
from app.utils.auth import jwt_required, roles_required

provider_bp = Blueprint("provider", __name__, url_prefix="/api")

@provider_bp.route("/provider/listings", methods=["GET"])
@jwt_required
@roles_required("provider", "admin")
def get_provider_listings():
    listings = FoodListing.query.filter_by(provider_id=g.current_user.id).order_by(FoodListing.created_at.desc()).all()
    results = []
    for l in listings:
        d = l.to_dict()
        d["pending_reservations_count"] = Reservation.query.filter_by(food_listing_id=l.id, status=ReservationStatus.PENDING).count()
        d["approved_reservations_count"] = Reservation.query.filter_by(food_listing_id=l.id, status=ReservationStatus.APPROVED).count()
        d["completed_reservations_count"] = Reservation.query.filter_by(food_listing_id=l.id, status=ReservationStatus.COMPLETED).count()
        results.append(d)
    return jsonify(results), 200


@provider_bp.route("/provider/reservations", methods=["GET"])
@jwt_required
@roles_required("provider", "admin")
def get_provider_reservations():
    # Join with FoodListing to only get reservations for provider's listings
    reservations = Reservation.query.join(FoodListing, FoodListing.id == Reservation.food_listing_id)\
        .filter(FoodListing.provider_id == g.current_user.id)\
        .order_by(Reservation.reserved_at.desc()).all()

    return jsonify([r.to_dict() for r in reservations]), 200


@provider_bp.route("/reservations/<int:reservation_id>/approve", methods=["PUT"])
@jwt_required
@roles_required("provider", "admin")
def approve_reservation(reservation_id):
    reservation = Reservation.query.get(reservation_id)
    if not reservation:
        return jsonify({"error": "Reservation not found"}), 404

    listing = reservation.food_listing
    if listing.provider_id != g.current_user.id and g.current_user.role != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    if reservation.status != ReservationStatus.PENDING:
        return jsonify({"error": f"Cannot approve reservation in '{reservation.status}' state"}), 400

    reservation.status = ReservationStatus.APPROVED

    # Notify recipient
    notif = Notification(
        user_id=reservation.recipient_id,
        title="Reservation Approved!",
        message=f"Your reservation for '{listing.title}' ({reservation.quantity} {listing.unit}) has been approved. Please collect it using Pickup Code: {reservation.pickup_code}.",
        notification_type=NotificationType.RESERVATION,
        reference_id=listing.id
    )
    db.session.add(notif)
    db.session.commit()

    return jsonify({
        "message": "Reservation approved successfully",
        "reservation": reservation.to_dict()
    }), 200


@provider_bp.route("/reservations/<int:reservation_id>/reject", methods=["PUT"])
@jwt_required
@roles_required("provider", "admin")
def reject_reservation(reservation_id):
    data = request.get_json() or {}
    reason = data.get("reason", "Provider unable to fulfill request at this time").strip()

    try:
        reservation = db.session.query(Reservation).filter_by(id=reservation_id).with_for_update().first()
        if not reservation:
            return jsonify({"error": "Reservation not found"}), 404

        listing = db.session.query(FoodListing).filter_by(id=reservation.food_listing_id).with_for_update().first()

        if listing.provider_id != g.current_user.id and g.current_user.role != "admin":
            return jsonify({"error": "Unauthorized"}), 403

        if reservation.status not in [ReservationStatus.PENDING, ReservationStatus.APPROVED]:
            return jsonify({"error": f"Cannot reject reservation in '{reservation.status}' state"}), 400

        # Atomically return quantity to remaining pool
        if listing.status != FoodListingStatus.EXPIRED:
            listing.remaining_quantity += reservation.quantity
            if listing.remaining_quantity == listing.quantity:
                listing.status = FoodListingStatus.AVAILABLE
            else:
                listing.status = FoodListingStatus.PARTIALLY_RESERVED

        reservation.status = ReservationStatus.REJECTED
        reservation.provider_notes = reason

        # Notify recipient
        notif = Notification(
            user_id=reservation.recipient_id,
            title="Reservation Request Declined",
            message=f"Your reservation for '{listing.title}' was declined by the provider. Reason: {reason}",
            notification_type=NotificationType.RESERVATION,
            reference_id=listing.id
        )
        db.session.add(notif)
        db.session.commit()

        return jsonify({
            "message": "Reservation rejected and inventory restored",
            "reservation": reservation.to_dict(),
            "remaining_quantity": listing.remaining_quantity
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Rejection failed: {str(e)}"}), 500
