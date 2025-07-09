from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()


class Config(object):
    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

    access_token_expiration = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 60))
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=access_token_expiration)

    refresh_token_expiration = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", 30))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=refresh_token_expiration)
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = eval(
        os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS", "False")
    )     
    CACHE_TYPE = "RedisCache" 
    CACHE_DEFAULT_TIMEOUT =  300
    # Email configuration
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = eval(os.getenv("MAIL_USE_TLS", "True"))
    MAIL_USE_SSL = eval(os.getenv("MAIL_USE_SSL", "False"))
