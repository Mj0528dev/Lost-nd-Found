from backend.helpers.user_helpers import get_user, verify_password, create_user
from backend.models import ValidationError
from flask_jwt_extended import create_access_token

# Simple in-memory revoked tokens store
revoked_tokens = set()

def register_user(data: dict):
    """Handles user registration"""
    from backend.helpers.validate_register import validate_registration_data

    validate_registration_data(data)

    username = data.get("username")
    password = data.get("password")
    role = data.get("role", "user")

    result = create_user(username, password, role)  # from helpers

    if result.get("message"):
        token = create_access_token(identity=username, additional_claims={"role": role})
        return {"token": token, "message": result["message"]}, 201

    raise ValidationError(result.get("error", "Registration failed"))

def login_user(data: dict):
    """Handles login"""
    if not data:
        raise ValidationError("Missing login data. Provide JSON body with 'username' and 'password'.")

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        raise ValidationError("Username and password are required for login.")

    user = get_user(username)
    if not user or not verify_password(password, user["password_hash"]):
        raise ValidationError("Invalid username or password. Please check your credentials.")

    token = create_access_token(identity=user["username"], additional_claims={"role": user["role"]})
    return {"token": token, "message": "Login successful"}, 200

def refresh_token(identity):
    """Generate a new access token"""
    new_access_token = create_access_token(identity=identity)
    return {"token": new_access_token, "message": "Access token refreshed"}, 200

def logout_token(jti: str):
    """Revoke a JWT"""
    if not jti:
        raise ValidationError("No token provided to revoke.")
    revoked_tokens.add(jti)
    return {"message": "Logout successful, token revoked"}, 200

def is_token_revoked(jti: str) -> bool:
    return jti in revoked_tokens