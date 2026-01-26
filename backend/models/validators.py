class ValidationError(Exception):
    """Custom exception for validation errors."""
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

def require_fields(data, required_fields):
    missing = [
        f for f in required_fields
        if f not in data or data[f] in (None, "", [])
    ]
    if missing:
        raise ValidationError(
            f"Missing required fields: {', '.join(missing)}",
            400
        )

def validate_int(value, field_name):
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValidationError(
            f"{field_name} must be an integer",
            400
        )

def validate_found_item_id(item_id):
    return validate_int(item_id, "found_item_id")

def validate_claim_decision(decision):
    if decision not in {"approved", "rejected"}:
        raise ValidationError("Invalid decision", 400)