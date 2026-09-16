from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

class UserRole:
    PROVIDER = "provider"
    RECIPIENT = "recipient"
    ADMIN = "admin"
    CHOICES = [PROVIDER, RECIPIENT, ADMIN]


class Organization(db.Model):
    __tablename__ = "organizations"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    org_type = db.Column(db.String(50), nullable=False)  # restaurant, canteen, bakery, caterer, ngo, shelter, etc.
    description = db.Column(db.Text, nullable=True)
    address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False, index=True)
    contact_person = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    users = db.relationship("User", backref="organization", lazy="dynamic")
    food_listings = db.relationship("FoodListing", backref="organization", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "org_type": self.org_type,
            "description": self.description,
            "address": self.address,
            "city": self.city,
            "contact_person": self.contact_person,
            "phone": self.phone,
            "email": self.email,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=UserRole.RECIPIENT, index=True)
    phone = db.Column(db.String(30), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(100), nullable=True, index=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    reservations = db.relationship("Reservation", backref="recipient", lazy="dynamic", foreign_keys="Reservation.recipient_id")
    listings_created = db.relationship("FoodListing", backref="provider", lazy="dynamic", foreign_keys="FoodListing.provider_id")
    notifications = db.relationship("Notification", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    preference = db.relationship("UserPreference", backref="user", uselist=False, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self, include_org=True):
        data = {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "role": self.role,
            "phone": self.phone,
            "address": self.address,
            "city": self.city,
            "organization_id": self.organization_id,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
        if include_org and self.organization:
            data["organization"] = self.organization.to_dict()
        else:
            data["organization"] = None
        return data


class UserPreference(db.Model):
    __tablename__ = "user_preferences"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    preferred_category_ids = db.Column(db.JSON, default=list, nullable=False)  # e.g. [1, 3]
    city = db.Column(db.String(100), nullable=True)
    dietary_filter = db.Column(db.String(50), nullable=True)  # all, veg, vegan, non-veg
    notify_new_listings = db.Column(db.Boolean, default=True, nullable=False)
    notify_pickup_reminders = db.Column(db.Boolean, default=True, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "preferred_category_ids": self.preferred_category_ids or [],
            "city": self.city,
            "dietary_filter": self.dietary_filter or "all",
            "notify_new_listings": self.notify_new_listings,
            "notify_pickup_reminders": self.notify_pickup_reminders
        }
