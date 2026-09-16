from flask import Blueprint, request, jsonify, g
from app.extensions import db
from app.models.user import User, Organization, UserRole, UserPreference
from app.models.food_listing import FoodCategory
from app.utils.auth import create_access_token, jwt_required

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    name = data.get("name", "").strip()
    role = data.get("role", UserRole.RECIPIENT)
    
    if not email or not password or not name:
        return jsonify({"error": "Email, password, and name are required"}), 400
    
    if role not in UserRole.CHOICES:
        return jsonify({"error": f"Invalid role. Must be one of {UserRole.CHOICES}"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "An account with this email already exists"}), 409

    org_id = None
    org_name = data.get("organization_name", "").strip()
    org_type = data.get("organization_type", "other").strip()
    address = data.get("address", "").strip()
    city = data.get("city", "").strip()
    phone = data.get("phone", "").strip()

    if org_name:
        org = Organization(
            name=org_name,
            org_type=org_type or ("restaurant" if role == UserRole.PROVIDER else "ngo"),
            address=address or "Not specified",
            city=city or "Chandigarh",
            phone=phone,
            email=email,
            is_verified=(role == UserRole.ADMIN)  # Admin auto-verified
        )
        db.session.add(org)
        db.session.flush()
        org_id = org.id

    user = User(
        email=email,
        name=name,
        role=role,
        phone=phone,
        address=address,
        city=city or "Chandigarh",
        organization_id=org_id,
        is_verified=(role == UserRole.ADMIN)
    )
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    # Create default recipient preferences
    if role == UserRole.RECIPIENT:
        pref = UserPreference(
            user_id=user.id,
            city=city or "Chandigarh",
            preferred_category_ids=[],
            dietary_filter="all"
        )
        db.session.add(pref)

    db.session.commit()

    token = create_access_token(user)
    return jsonify({
        "message": "User registered successfully",
        "token": token,
        "user": user.to_dict()
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401

    if not user.is_active:
        return jsonify({"error": "Account is inactive. Contact administrator."}), 403

    token = create_access_token(user)
    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": user.to_dict()
    }), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required
def get_me():
    return jsonify({
        "user": g.current_user.to_dict(),
        "preference": g.current_user.preference.to_dict() if g.current_user.preference else None
    }), 200


@auth_bp.route("/preferences", methods=["GET"])
@jwt_required
def get_preferences():
    pref = g.current_user.preference
    if not pref:
        pref = UserPreference(user_id=g.current_user.id, city=g.current_user.city)
        db.session.add(pref)
        db.session.commit()
    return jsonify(pref.to_dict()), 200


@auth_bp.route("/preferences", methods=["PUT"])
@jwt_required
def update_preferences():
    pref = g.current_user.preference
    if not pref:
        pref = UserPreference(user_id=g.current_user.id)
        db.session.add(pref)

    data = request.get_json() or {}
    if "preferred_category_ids" in data:
        pref.preferred_category_ids = data["preferred_category_ids"]
    if "city" in data:
        pref.city = data["city"].strip()
    if "dietary_filter" in data:
        pref.dietary_filter = data["dietary_filter"].strip()
    if "notify_new_listings" in data:
        pref.notify_new_listings = bool(data["notify_new_listings"])
    if "notify_pickup_reminders" in data:
        pref.notify_pickup_reminders = bool(data["notify_pickup_reminders"])

    db.session.commit()
    return jsonify({"message": "Preferences updated", "preference": pref.to_dict()}), 200


@auth_bp.route("/categories", methods=["GET"])
def get_categories():
    categories = FoodCategory.query.all()
    return jsonify([c.to_dict() for c in categories]), 200
