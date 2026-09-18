import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "foodrescue-secret-key-2026-super-secure")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "foodrescue-jwt-secret-key-2026")
    JWT_EXPIRATION_HOURS = int(os.environ.get("JWT_EXPIRATION_HOURS", 24))
    
    # Database configuration
    # Supports SQLite with WAL mode by default, or PostgreSQL via DATABASE_URL
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, 'foodrescue.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Robust SQLite connect arguments
    if SQLALCHEMY_DATABASE_URI.startswith("sqlite"):
        SQLALCHEMY_ENGINE_OPTIONS = {
            "connect_args": {
                "check_same_thread": False,
                "timeout": 30
            },
            "pool_pre_ping": True
        }
    else:
        SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_size": 10,
            "max_overflow": 20,
            "pool_pre_ping": True
        }

    # Celery & Redis configuration
    CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    
    # Impact benchmarks
    CO2_SAVED_PER_MEAL_KG = float(os.environ.get("CO2_SAVED_PER_MEAL_KG", 2.5))
    
    # Local background scheduler fallback toggle
    ENABLE_LOCAL_SCHEDULER = os.environ.get("ENABLE_LOCAL_SCHEDULER", "true").lower() == "true"


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'test_foodrescue.db')}"
    ENABLE_LOCAL_SCHEDULER = False


class ProductionConfig(Config):
    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig
}
