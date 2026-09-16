from datetime import datetime
from app.extensions import db

class NotificationType:
    MATCH = "MATCH"
    RESERVATION = "RESERVATION"
    EXPIRY = "EXPIRY"
    REMINDER = "REMINDER"
    SYSTEM = "SYSTEM"


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(30), default=NotificationType.SYSTEM, nullable=False)
    reference_id = db.Column(db.Integer, nullable=True)  # listing_id or reservation_id
    is_read = db.Column(db.Boolean, default=False, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "message": self.message,
            "notification_type": self.notification_type,
            "reference_id": self.reference_id,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
