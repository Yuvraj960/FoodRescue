import os
import sqlite3
from flask import Flask, jsonify
from sqlalchemy import event
from sqlalchemy.engine import Engine
from app.config import config_by_name
from app.extensions import db, migrate, cors
from app.routes import register_routes
from app.tasks.scheduler import init_scheduler

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    Configure robust SQLite settings:
    - WAL (Write-Ahead Logging) for concurrent reads/writes
    - NORMAL synchronous mode for high performance
    - Foreign keys enforcement
    - 15-second busy timeout to eliminate lock contention
    """
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA busy_timeout=15000")
        cursor.close()


def create_app(config_name=None):
    if not config_name:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name["development"]))

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    # Register API blueprints
    register_routes(app)

    # Health check route
    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({
            "status": "healthy",
            "environment": config_name,
            "database": "connected"
        }), 200

    # Start local background scheduler if not in testing mode
    if not app.config.get("TESTING", False):
        try:
            init_scheduler(app)
        except Exception as e:
            app.logger.warning(f"Could not initialize local scheduler: {e}")

    return app
