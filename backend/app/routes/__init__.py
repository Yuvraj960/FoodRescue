from app.routes.auth import auth_bp
from app.routes.food import food_bp
from app.routes.reservations import reservations_bp
from app.routes.provider import provider_bp
from app.routes.analytics import analytics_bp
from app.routes.notifications import notifications_bp
from app.routes.admin import admin_bp

def register_routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(food_bp)
    app.register_blueprint(reservations_bp)
    app.register_blueprint(provider_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(admin_bp)
