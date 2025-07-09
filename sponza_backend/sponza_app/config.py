from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()


class Config(object):
    # Security keys
    SECRET_KEY = os.getenv("SECRET_KEY", "your_default_secret_key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your_default_jwt_secret_key")

    # JWT expiration
    access_token_expiration = int(
        os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 60)
    )  # in seconds
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=access_token_expiration)

    refresh_token_expiration = int(
        os.getenv("JWT_REFRESH_TOKEN_EXPIRES", 30)
    )  # in days
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=refresh_token_expiration)

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "SQLALCHEMY_DATABASE_URI", "sqlite:///sponza.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = (
        os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS", "False").lower() == "true"
    )

    # Caching
    CACHE_TYPE = os.getenv("CACHE_TYPE", "RedisCache")
    CACHE_DEFAULT_TIMEOUT = int(os.getenv("CACHE_DEFAULT_TIMEOUT", 300))

    # Email configuration
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "your_email@gmail.com")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "your_app_password")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True").lower() == "true"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "False").lower() == "true"
