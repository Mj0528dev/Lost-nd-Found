from backend.models import ValidationError

def validate_registration_data(data: dict):
    """
    Validates registration data for user-friendly error messages.
    Raises ValidationError if invalid.
    """
    if not data:
        raise ValidationError("Missing registration data. Provide JSON body with 'username' and 'password'.")

    username = data.get("username")
    password = data.get("password")

    if not username:
        raise ValidationError("Username is required. Choose a unique identifier for login.")

    if not password:
        raise ValidationError("Password is required. Make sure to include a secure password.")

    if len(password) < 6:
        raise ValidationError("Password too short. Minimum 6 characters required.")
