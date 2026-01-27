from backend.helpers.user_helpers import get_user, verify_password, create_user
from backend.models.validators import ValidationError 
from backend.helpers.validate_register import validate_registration_data
from flask_jwt_extended import create_access_token

def register_user(data: dict):
    """
    Handles registration logic:
    - Validates input
    - Creates user
    - Returns token and message
    """
    # Validate input
    validate_registration_data(data)

    username = data.get("username")
    password = data.get("password")
    role = data.get("role", "user")

    result = create_user(username, password, role)

    if result.get("message"):
        # Successfully created user → issue token
        token = create_access_token(identity=username, additional_claims={"role": role})
        return {"token": token, "message": result["message"]}, 201

    # If create_user returned an error (e.g., username exists)
    raise ValidationError(result.get("error", "Registration failed"))

def login_user(data: dict):
    """
    Handles login logic:
    - Checks username & password
    - Returns JWT token if valid
    """
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
