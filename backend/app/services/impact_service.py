from datetime import datetime, timedelta
from sqlalchemy import func, extract
from flask import current_app
from app.extensions import db
from app.models.food_listing import FoodListing, FoodListingStatus, FoodCategory
from app.models.reservation import Reservation, ReservationStatus
from app.models.user import User, UserRole, Organization
from app.models.impact import ImpactRecord

def get_impact_summary():
    """
    Computes real-time platform impact metrics:
    - Meals rescued
    - Total listings
    - Successful pickups
    - Active providers
    - Participating recipient organizations
    - Carbon emissions avoided (kg CO2e)
    """
    co2_factor = current_app.config.get("CO2_SAVED_PER_MEAL_KG", 2.5)

    # Total meals rescued through completed reservations
    meals_rescued_res = db.session.query(func.coalesce(func.sum(Reservation.quantity), 0)).filter(
        Reservation.status == ReservationStatus.COMPLETED
    ).scalar()

    total_listings = FoodListing.query.count()
    completed_listings = FoodListing.query.filter_by(status=FoodListingStatus.COMPLETED).count()
    completed_pickups = Reservation.query.filter_by(status=ReservationStatus.COMPLETED).count()

    active_providers = db.session.query(func.count(func.distinct(FoodListing.provider_id))).scalar()
    participating_orgs = Organization.query.count()

    total_carbon_saved = round(meals_rescued_res * co2_factor, 1)

    return {
        "meals_rescued": int(meals_rescued_res),
        "total_listings": total_listings,
        "completed_listings": completed_listings,
        "successful_pickups": completed_pickups,
        "active_providers": active_providers,
        "participating_orgs": participating_orgs,
        "carbon_saved_kg": total_carbon_saved,
        "co2_factor_per_meal": co2_factor
    }


def get_monthly_impact():
    """
    Returns monthly rescued meals distribution over the current / recent months.
    """
    now = datetime.utcnow()
    # Query completed reservations grouped by month
    results = db.session.query(
        extract("year", Reservation.reserved_at).label("yr"),
        extract("month", Reservation.reserved_at).label("mo"),
        func.sum(Reservation.quantity).label("total_meals")
    ).filter(
        Reservation.status == ReservationStatus.COMPLETED
    ).group_by("yr", "mo").order_by("yr", "mo").all()

    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    monthly_data = []

    for r in results:
        m_idx = int(r.mo) - 1
        label = f"{month_names[m_idx]} {int(r.yr)}"
        monthly_data.append({
            "label": label,
            "month": int(r.mo),
            "year": int(r.yr),
            "meals": int(r.total_meals or 0)
        })

    # If empty or fewer than 4 months, provide past 4 months baseline
    if len(monthly_data) < 4:
        for i in range(3, -1, -1):
            target_date = now - timedelta(days=i*30)
            label = f"{month_names[target_date.month - 1]} {target_date.year}"
            if not any(d["label"] == label for d in monthly_data):
                monthly_data.append({
                    "label": label,
                    "month": target_date.month,
                    "year": target_date.year,
                    "meals": 0
                })

    return monthly_data


def get_category_distribution():
    """
    Returns meal count distribution across food categories for pie/donut charts.
    """
    results = db.session.query(
        FoodCategory.name,
        func.coalesce(func.sum(FoodListing.quantity), 0)
    ).join(FoodListing, FoodListing.category_id == FoodCategory.id, isouter=True)\
     .group_by(FoodCategory.name).all()

    return [{"category": r[0], "quantity": int(r[1])} for r in results]
