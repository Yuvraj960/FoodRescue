import uuid
from datetime import datetime
from app.extensions import db

class ReservationStatus:
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    EXPIRED = "EXPIRED"

    ALL = [PENDING, APPROVED, REJECTED, CANCELLED, COMPLETED, EXPIRED]


def generate_pickup_code():
    # Returns an easy-to-read, 6-character code like "FR-8492"
    return f"FR-{uuid.uuid4().hex[:6].upper()}"


class Reservation(db.Model):
    __tablename__ = "reservations"

    id = db.Column(db.Integer, primary_key=True)
    food_listing_id = db.Column(db.Integer, db.ForeignKey("food_listings.id", ondelete="CASCADE"), nullable=False, index=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(30), default=ReservationStatus.PENDING, nullable=False, index=True)

    reserved_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    pickup_code = db.Column(db.String(20), default=generate_pickup_code, unique=True, nullable=False)
    pickup_time = db.Column(db.DateTime, nullable=True)

    notes = db.Column(db.Text, nullable=True)  # recipient note/requirement
    provider_notes = db.Column(db.Text, nullable=True)  # provider remarks/rejection note

    pickup_record = db.relationship("Pickup", backref="reservation", uselist=False, cascade="all, delete-orphan")

    def to_dict(self, include_listing=True, include_recipient=True):
        data = {
            "id": self.id,
            "food_listing_id": self.food_listing_id,
            "recipient_id": self.recipient_id,
            "quantity": self.quantity,
            "status": self.status,
            "reserved_at": self.reserved_at.isoformat() if self.reserved_at else None,
            "pickup_code": self.pickup_code,
            "pickup_time": self.pickup_time.isoformat() if self.pickup_time else None,
            "notes": self.notes,
            "provider_notes": self.provider_notes
        }

        if include_listing and self.food_listing:
            data["listing"] = self.food_listing.to_dict(include_provider=True)

        if include_recipient and self.recipient:
            data["recipient"] = {
                "id": self.recipient.id,
                "name": self.recipient.name,
                "email": self.recipient.email,
                "phone": self.recipient.phone,
                "organization_name": self.recipient.organization.name if self.recipient.organization else None,
                "org_type": self.recipient.organization.org_type if self.recipient.organization else None
            }

        return data


class Pickup(db.Model):
    __tablename__ = "pickups"

    id = db.Column(db.Integer, primary_key=True)
    reservation_id = db.Column(db.Integer, db.ForeignKey("reservations.id", ondelete="CASCADE"), nullable=False, unique=True)
    collected_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    verified_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "reservation_id": self.reservation_id,
            "collected_at": self.collected_at.isoformat() if self.collected_at else None,
            "verified_by_user_id": self.verified_by_user_id,
            "notes": self.notes
        }
