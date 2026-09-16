from datetime import datetime
from app.extensions import db

class FoodListingStatus:
    AVAILABLE = "AVAILABLE"
    PARTIALLY_RESERVED = "PARTIALLY_RESERVED"
    FULLY_RESERVED = "FULLY_RESERVED"
    EXPIRED = "EXPIRED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

    ACTIVE_STATUSES = [AVAILABLE, PARTIALLY_RESERVED]
    ALL = [AVAILABLE, PARTIALLY_RESERVED, FULLY_RESERVED, EXPIRED, COMPLETED, CANCELLED]


class DietaryType:
    VEGETARIAN = "VEGETARIAN"
    NON_VEGETARIAN = "NON_VEGETARIAN"
    VEGAN = "VEGAN"
    BAKERY = "BAKERY"
    OTHER = "OTHER"
    ALL = [VEGETARIAN, NON_VEGETARIAN, VEGAN, BAKERY, OTHER]


class FoodCategory(db.Model):
    __tablename__ = "food_categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    icon = db.Column(db.String(50), nullable=True)  # e.g. "Salad", "Utensils", "Cake"
    default_dietary = db.Column(db.String(30), default=DietaryType.VEGETARIAN, nullable=False)

    listings = db.relationship("FoodListing", backref="category", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "default_dietary": self.default_dietary
        }


class FoodListing(db.Model):
    __tablename__ = "food_listings"

    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey("food_categories.id", ondelete="RESTRICT"), nullable=False, index=True)

    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Dietary information prominently tracked
    dietary_type = db.Column(db.String(30), default=DietaryType.VEGETARIAN, nullable=False, index=True)
    allergen_info = db.Column(db.String(255), nullable=True)  # e.g., "Contains dairy, gluten"
    is_perishable = db.Column(db.Boolean, default=True, nullable=False)

    quantity = db.Column(db.Integer, nullable=False)
    remaining_quantity = db.Column(db.Integer, nullable=False, index=True)
    unit = db.Column(db.String(30), default="portions", nullable=False)  # portions, meals, kg, boxes

    prepared_at = db.Column(db.DateTime, nullable=True)
    expiry_time = db.Column(db.DateTime, nullable=False, index=True)
    pickup_start = db.Column(db.DateTime, nullable=False)
    pickup_end = db.Column(db.DateTime, nullable=False)

    location = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False, index=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

    status = db.Column(db.String(30), default=FoodListingStatus.AVAILABLE, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    reservations = db.relationship("Reservation", backref="food_listing", lazy="dynamic", cascade="all, delete-orphan")

    def to_dict(self, include_provider=True):
        now = datetime.utcnow()
        is_expired = self.expiry_time <= now if self.expiry_time else False
        
        data = {
            "id": self.id,
            "provider_id": self.provider_id,
            "organization_id": self.organization_id,
            "category_id": self.category_id,
            "category": self.category.to_dict() if self.category else None,
            "title": self.title,
            "description": self.description,
            "dietary_type": self.dietary_type,
            "allergen_info": self.allergen_info,
            "is_perishable": self.is_perishable,
            "quantity": self.quantity,
            "remaining_quantity": self.remaining_quantity,
            "unit": self.unit,
            "prepared_at": self.prepared_at.isoformat() if self.prepared_at else None,
            "expiry_time": self.expiry_time.isoformat() if self.expiry_time else None,
            "pickup_start": self.pickup_start.isoformat() if self.pickup_start else None,
            "pickup_end": self.pickup_end.isoformat() if self.pickup_end else None,
            "location": self.location,
            "city": self.city,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "status": self.status,
            "is_expired": is_expired,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

        if include_provider and self.provider:
            data["provider_name"] = self.provider.name
            data["organization_name"] = self.organization.name if self.organization else None
            data["provider_phone"] = self.provider.phone

        return data
