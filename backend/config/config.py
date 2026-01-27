from datetime import timedelta

class Config:
    JWT_SECRET_KEY = "dev-secret-change-later"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=60)
