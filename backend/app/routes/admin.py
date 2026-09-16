from flask import Blueprint, jsonify, request, g
from app.extensions import db
from app.models.user import User, Organization
from app.models.food_listing import FoodListing, FoodListingStatus
from app.models.reservation import Reservation
from app.utils.auth import jwt_required, roles_required

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")

@admin_bp.route("/users", methods=["GET"])
@jwt_required
@roles_required("admin")
def list_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify([u.to_dict() for u in users]), 200

@admin_bp.route("/users/<int:user_id>/verify", methods=["PUT"])
@jwt_required
@roles_required("admin")
def verify_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.is_verified = not user.is_verified
    if user.organization:
        user.organization.is_verified = user.is_verified

    db.session.commit()
    return jsonify({
        "message": f"User verification status updated to {user.is_verified}",
        "user": user.to_dict()
    }), 200

@admin_bp.route("/listings/<int:listing_id>", methods=["DELETE"])
@jwt_required
@roles_required("admin")
def admin_delete_listing(listing_id):
    listing = FoodListing.query.get(listing_id)
    if not listing:
        return jsonify({"error": "Listing not found"}), 404

    listing.status = FoodListingStatus.CANCELLED
    db.session.commit()
    return jsonify({"message": "Listing removed by admin"}), 200

@admin_bp.route("/stats", methods=["GET"])
@jwt_required
@roles_required("admin")
def admin_stats():
    total_users = User.query.count()
    providers_count = User.query.filter_by(role="provider").count()
    recipients_count = User.query.filter_by(role="recipient").count()
    total_orgs = Organization.query.count()
    total_listings = FoodListing.query.count()
    total_reservations = Reservation.query.count()

    return jsonify({
        "total_users": total_users,
        "providers_count": providers_count,
        "recipients_count": recipients_count,
        "total_organizations": total_orgs,
        "total_listings": total_listings,
        "total_reservations": total_reservations
    }), 200
