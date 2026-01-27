import os
from datetime import timedelta


class Config:
    """
    Base configuration.
    Used for development unless overridden.
    """

    # Core Flask
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")
    TESTING = False

    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-jwt-secret")

    # Explicit token behavior (NO defaults)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)

    JWT_ALGORITHM = "HS256"

    # Safer defaults
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"