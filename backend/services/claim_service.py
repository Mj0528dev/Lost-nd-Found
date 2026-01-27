from backend.models import (
    create_claim,
    ValidationError,
    require_fields,
    validate_found_item_id,
)

def submit_claim(data: dict, claimed_by: str) -> tuple:
    """
    Validates and creates a claim.
    
    Args:
        data (dict): Raw input data from route
        claimed_by (str): username from JWT

    Returns:
        tuple: (result dict, HTTP status)
    """
    require_fields(data, ["found_item_id"])
    validate_found_item_id(data["found_item_id"])
    
    data["claimed_by"] = claimed_by
    result, status = create_claim(data)
    
    return result, status
