from datetime import datetime, date
from app.extensions import db

class ImpactRecord(db.Model):
    __tablename__ = "impact_records"

    id = db.Column(db.Integer, primary_key=True)
    record_date = db.Column(db.Date, default=date.today, unique=True, nullable=False, index=True)
    meals_rescued = db.Column(db.Integer, default=0, nullable=False)
    listings_completed = db.Column(db.Integer, default=0, nullable=False)
    active_providers_count = db.Column(db.Integer, default=0, nullable=False)
    active_recipients_count = db.Column(db.Integer, default=0, nullable=False)
    carbon_saved_kg = db.Column(db.Float, default=0.0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "record_date": self.record_date.isoformat() if self.record_date else None,
            "meals_rescued": self.meals_rescued,
            "listings_completed": self.listings_completed,
            "active_providers_count": self.active_providers_count,
            "active_recipients_count": self.active_recipients_count,
            "carbon_saved_kg": round(self.carbon_saved_kg, 2),
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
