from flask import Blueprint, jsonify
from app.services.impact_service import get_impact_summary, get_monthly_impact, get_category_distribution

analytics_bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")

@analytics_bp.route("/impact", methods=["GET"])
def impact_stats():
    stats = get_impact_summary()
    return jsonify(stats), 200

@analytics_bp.route("/monthly", methods=["GET"])
def monthly_stats():
    monthly = get_monthly_impact()
    return jsonify(monthly), 200

@analytics_bp.route("/categories", methods=["GET"])
def category_distribution():
    categories = get_category_distribution()
    return jsonify(categories), 200
