from backend.models import (
    create_lost_item,
    create_found_item,
    get_published_found_items,
    ValidationError,
    require_fields,
)
from datetime import datetime

def submit_lost_item(data: dict) -> tuple:
    """
    Validates and submits a lost item.
    
    Args:
        data (dict): Raw input data from route

    Returns:
        tuple: (result dict, HTTP status)
    """
    # Required fields
    require_fields(data, ["category", "last_seen_location", "lost_datetime", "public_description"])
    
    # Optional: you could normalize datetime here if needed
    # Example: ensure lost_datetime is a string in ISO format
    if isinstance(data.get("lost_datetime"), str):
        try:
            datetime.fromisoformat(data["lost_datetime"])
        except ValueError:
            raise ValidationError("Invalid datetime format for lost_datetime", 400)
    
    create_lost_item(data)
    return {"message": "Lost item reported successfully"}, 201


def submit_found_item(data: dict) -> tuple:
    """
    Validates and submits a found item.
    
    Args:
        data (dict): Raw input data from route

    Returns:
        tuple: (result dict, HTTP status)
    """
    require_fields(data, ["category", "found_location", "found_datetime"])
    
    # Optional: normalize datetime
    if isinstance(data.get("found_datetime"), str):
        try:
            datetime.fromisoformat(data["found_datetime"])
        except ValueError:
            raise ValidationError("Invalid datetime format for found_datetime", 400)
    
    create_found_item(data)
    return {"message": "Found item reported successfully"}, 201


def get_found_items() -> tuple:
    """
    Returns published found items. No validation needed.
    
    Returns:
        tuple: (list of items, HTTP status)
    """
    return get_published_found_items(), 200
