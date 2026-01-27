from backend.models.validators import ValidationError

def validate_registration_data(data: dict) -> dict:
    """
    Validates registration input data.
    
    Args:
        data (dict): JSON payload from client

    Returns:
        dict: Cleaned data with 'username', 'password', and 'role'

    Raises:
        ValidationError: if JSON is missing or required fields are absent
    """
    if not data:
        raise ValidationError(
            message="Request body is required.",
            status_code=400
        )
    
    username = data.get("username")
    password = data.get("password")
    role = data.get("role", "user")  # default to 'user'

    if not username or not password:
        raise ValidationError(
            message="Username and password are required.",
            status_code=400
        )
    
    # Return cleaned dict for direct consumption by create_user()
    return {
        "username": username.strip(),
        "password": password,
        "role": role
    }