from datetime import datetime
from flask import Blueprint, request, jsonify, g
from app.extensions import db
from app.models.food_listing import FoodListing, FoodListingStatus
from app.models.reservation import Reservation, ReservationStatus, Pickup, generate_pickup_code
from app.models.notification import Notification, NotificationType
from app.utils.auth import jwt_required

reservations_bp = Blueprint("reservations", __name__, url_prefix="/api")

@reservations_bp.route("/food/<int:listing_id>/reserve", methods=["POST"])
@jwt_required
def reserve_food(listing_id):
    data = request.get_json() or {}
    quantity = data.get("quantity")
    notes = data.get("notes", "").strip()

    if not quantity:
        return jsonify({"error": "Reservation quantity is required"}), 400

    try:
        quantity = int(quantity)
        if quantity <= 0:
            return jsonify({"error": "Quantity must be greater than zero"}), 400
    except ValueError:
        return jsonify({"error": "Quantity must be a valid integer"}), 400

    try:
        # Transaction with row-level lock where supported
        # For SQLite, it guarantees transaction isolation
        listing = db.session.query(FoodListing).filter(FoodListing.id == listing_id).with_for_update().first()

        if not listing:
            return jsonify({"error": "Food listing not found"}), 404

        # Check if expired
        now = datetime.utcnow()
        if listing.expiry_time <= now:
            listing.status = FoodListingStatus.EXPIRED
            db.session.commit()
            return jsonify({"error": "Cannot reserve: Food listing has expired"}), 400

        # Check status
        if listing.status not in [FoodListingStatus.AVAILABLE, FoodListingStatus.PARTIALLY_RESERVED]:
            return jsonify({"error": f"Cannot reserve: Food listing status is {listing.status}"}), 400

        # Concurrency safety: Verify remaining stock
        if quantity > listing.remaining_quantity:
            return jsonify({
                "error": f"Requested quantity ({quantity}) exceeds available portions ({listing.remaining_quantity})",
                "remaining_quantity": listing.remaining_quantity
            }), 409

        # Deduct remaining inventory atomically
        listing.remaining_quantity -= quantity
        if listing.remaining_quantity == 0:
            listing.status = FoodListingStatus.FULLY_RESERVED
        else:
            listing.status = FoodListingStatus.PARTIALLY_RESERVED

        # Create Reservation
        pickup_code = generate_pickup_code()
        reservation = Reservation(
            food_listing_id=listing.id,
            recipient_id=g.current_user.id,
            quantity=quantity,
            status=ReservationStatus.PENDING,
            pickup_code=pickup_code,
            notes=notes
        )
        db.session.add(reservation)

        # Notify Food Provider
        org_name = g.current_user.organization.name if g.current_user.organization else g.current_user.name
        notif = Notification(
            user_id=listing.provider_id,
            title="New Food Reservation Request",
            message=f"{org_name} has requested {quantity} {listing.unit} of '{listing.title}'. Pickup Code: {pickup_code}.",
            notification_type=NotificationType.RESERVATION,
            reference_id=listing.id
        )
        db.session.add(notif)

        db.session.commit()

        return jsonify({
            "message": "Reservation submitted successfully",
            "reservation": reservation.to_dict(),
            "remaining_quantity": listing.remaining_quantity,
            "listing_status": listing.status
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Reservation failed due to error: {str(e)}"}), 500


@reservations_bp.route("/reservations", methods=["GET"])
@jwt_required
def get_my_reservations():
    status = request.args.get("status")
    query = Reservation.query.filter_by(recipient_id=g.current_user.id)

    if status:
        query = query.filter_by(status=status.upper())

    reservations = query.order_by(Reservation.reserved_at.desc()).all()
    return jsonify([r.to_dict() for r in reservations]), 200


@reservations_bp.route("/reservations/<int:reservation_id>", methods=["GET"])
@jwt_required
def get_reservation(reservation_id):
    reservation = Reservation.query.get(reservation_id)
    if not reservation:
        return jsonify({"error": "Reservation not found"}), 404

    # Allow recipient, provider of listing, or admin
    listing = reservation.food_listing
    if (reservation.recipient_id != g.current_user.id and 
        listing.provider_id != g.current_user.id and 
        g.current_user.role != "admin"):
        return jsonify({"error": "Unauthorized access to reservation"}), 403

    return jsonify(reservation.to_dict()), 200


@reservations_bp.route("/reservations/<int:reservation_id>/cancel", methods=["PUT"])
@jwt_required
def cancel_reservation(reservation_id):
    try:
        reservation = db.session.query(Reservation).filter_by(id=reservation_id).with_for_update().first()
        if not reservation:
            return jsonify({"error": "Reservation not found"}), 404

        listing = db.session.query(FoodListing).filter_by(id=reservation.food_listing_id).with_for_update().first()

        # Only recipient, provider, or admin can cancel
        is_recipient = (reservation.recipient_id == g.current_user.id)
        is_provider = (listing.provider_id == g.current_user.id)
        is_admin = (g.current_user.role == "admin")

        if not (is_recipient or is_provider or is_admin):
            return jsonify({"error": "Unauthorized to cancel this reservation"}), 403

        if reservation.status not in [ReservationStatus.PENDING, ReservationStatus.APPROVED]:
            return jsonify({"error": f"Cannot cancel reservation with status '{reservation.status}'"}), 400

        # Atomically restore inventory to listing if not expired
        if listing.status != FoodListingStatus.EXPIRED:
            listing.remaining_quantity += reservation.quantity
            if listing.remaining_quantity == listing.quantity:
                listing.status = FoodListingStatus.AVAILABLE
            else:
                listing.status = FoodListingStatus.PARTIALLY_RESERVED

        reservation.status = ReservationStatus.CANCELLED

        # Notify recipient or provider depending on who cancelled
        if is_recipient:
            notif = Notification(
                user_id=listing.provider_id,
                title="Reservation Cancelled by Recipient",
                message=f"Recipient cancelled reservation {reservation.pickup_code} ({reservation.quantity} {listing.unit} restored).",
                notification_type=NotificationType.RESERVATION,
                reference_id=listing.id
            )
            db.session.add(notif)
        else:
            notif = Notification(
                user_id=reservation.recipient_id,
                title="Reservation Cancelled by Provider",
                message=f"Your reservation {reservation.pickup_code} for '{listing.title}' was cancelled by the provider.",
                notification_type=NotificationType.RESERVATION,
                reference_id=listing.id
            )
            db.session.add(notif)

        db.session.commit()
        return jsonify({
            "message": "Reservation cancelled and inventory restored",
            "reservation": reservation.to_dict(),
            "remaining_quantity": listing.remaining_quantity
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Cancellation failed: {str(e)}"}), 500


@reservations_bp.route("/reservations/<int:reservation_id>/pickup", methods=["PUT"])
@jwt_required
def confirm_pickup(reservation_id):
    data = request.get_json() or {}
    pickup_code = data.get("pickup_code", "").strip().upper()
    notes = data.get("notes", "").strip()

    try:
        reservation = db.session.query(Reservation).filter_by(id=reservation_id).with_for_update().first()
        if not reservation:
            return jsonify({"error": "Reservation not found"}), 404

        listing = db.session.query(FoodListing).filter_by(id=reservation.food_listing_id).with_for_update().first()

        is_provider = (listing.provider_id == g.current_user.id)
        is_recipient = (reservation.recipient_id == g.current_user.id)
        is_admin = (g.current_user.role == "admin")

        if not (is_provider or is_recipient or is_admin):
            return jsonify({"error": "Unauthorized"}), 403

        if reservation.status != ReservationStatus.APPROVED:
            return jsonify({"error": f"Reservation must be APPROVED before pickup can be completed. Current status: {reservation.status}"}), 400

        # Validate pickup code if provided by provider verifying recipient
        if is_provider and pickup_code and pickup_code != reservation.pickup_code:
            return jsonify({"error": "Invalid pickup code provided"}), 400

        reservation.status = ReservationStatus.COMPLETED
        reservation.pickup_time = datetime.utcnow()

        # Create or update pickup record
        pickup = Pickup(
            reservation_id=reservation.id,
            collected_at=datetime.utcnow(),
            verified_by_user_id=g.current_user.id,
            notes=notes
        )
        db.session.add(pickup)

        # Check if all reservations for this listing are now COMPLETED and remaining_quantity == 0
        if listing.remaining_quantity == 0:
            non_completed = Reservation.query.filter(
                Reservation.food_listing_id == listing.id,
                Reservation.status.in_([ReservationStatus.PENDING, ReservationStatus.APPROVED])
            ).count()
            if non_completed == 0:
                listing.status = FoodListingStatus.COMPLETED

        # Create notification
        recipient_name = reservation.recipient.name if reservation.recipient else "Recipient"
        notif = Notification(
            user_id=listing.provider_id if is_recipient else reservation.recipient_id,
            title="Pickup Completed Successfully!",
            message=f"Pickup for '{listing.title}' ({reservation.quantity} {listing.unit}) has been confirmed completed. Thank you for rescuing food!",
            notification_type=NotificationType.RESERVATION,
            reference_id=listing.id
        )
        db.session.add(notif)

        db.session.commit()
        return jsonify({
            "message": "Pickup confirmed completed successfully",
            "reservation": reservation.to_dict(),
            "pickup": pickup.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Pickup confirmation failed: {str(e)}"}), 500
