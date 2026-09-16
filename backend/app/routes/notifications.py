from flask import Blueprint, jsonify, g
from app.extensions import db
from app.models.notification import Notification
from app.utils.auth import jwt_required

notifications_bp = Blueprint("notifications", __name__, url_prefix="/api/notifications")

@notifications_bp.route("", methods=["GET"])
@jwt_required
def get_notifications():
    notifications = Notification.query.filter_by(user_id=g.current_user.id).order_by(Notification.created_at.desc()).limit(50).all()
    return jsonify([n.to_dict() for n in notifications]), 200

@notifications_bp.route("/unread-count", methods=["GET"])
@jwt_required
def get_unread_count():
    count = Notification.query.filter_by(user_id=g.current_user.id, is_read=False).count()
    return jsonify({"unread_count": count}), 200

@notifications_bp.route("/<int:notif_id>/read", methods=["PUT"])
@jwt_required
def mark_read(notif_id):
    notif = Notification.query.get(notif_id)
    if not notif or notif.user_id != g.current_user.id:
        return jsonify({"error": "Notification not found"}), 404

    notif.is_read = True
    db.session.commit()
    return jsonify({"message": "Notification marked as read"}), 200

@notifications_bp.route("/read-all", methods=["PUT"])
@jwt_required
def mark_all_read():
    Notification.query.filter_by(user_id=g.current_user.id, is_read=False).update({"is_read": True})
    db.session.commit()
    return jsonify({"message": "All notifications marked as read"}), 200
