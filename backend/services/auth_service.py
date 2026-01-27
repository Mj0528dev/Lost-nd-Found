from backend.helpers.user_helpers import create_user
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
