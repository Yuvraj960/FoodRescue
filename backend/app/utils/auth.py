from functools import wraps
from datetime import datetime, timedelta
import jwt
from flask import request, jsonify, current_app, g
from app.models.user import User

def create_access_token(user):
    payload = {
        "sub": user.id,
        "email": user.email,
        "role": user.role,
        "name": user.name,
        "org_id": user.organization_id,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=current_app.config.get("JWT_EXPIRATION_HOURS", 24))
    }
    secret = current_app.config.get("JWT_SECRET_KEY", "foodrescue-jwt-secret-key-2026")
    return jwt.encode(payload, secret, algorithm="HS256")


def decode_token(token):
    secret = current_app.config.get("JWT_SECRET_KEY", "foodrescue-jwt-secret-key-2026")
    try:
        return jwt.decode(token, secret, algorithms=["HS256"])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Authorization token is missing or malformed"}), 401
        
        token = auth_header.split(" ")[1]
        payload = decode_token(token)
        if not payload:
            return jsonify({"error": "Token is invalid or expired"}), 401
        
        user = User.query.get(payload["sub"])
        if not user or not user.is_active:
            return jsonify({"error": "User not found or inactive"}), 401
        
        g.current_user = user
        return f(*args, **kwargs)
    return decorated


def roles_required(*roles):
    def decorator(f):
        @wraps(f)
        @jwt_required
        def decorated(*args, **kwargs):
            if g.current_user.role not in roles and g.current_user.role != "admin":
                return jsonify({"error": f"Forbidden: Requires role {roles}"}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator
