from datetime import datetime, timezone
from .base import get_db_connection
from .validators import ValidationError, require_fields, validate_int

def log_action(action: str, entity_type: str, entity_id: int, performed_by: str, notes: str = None):
    """
    Logs an action in the audit_logs table.

    Parameters:
        action (str): The action performed (e.g., "create", "update", "approve").
        entity_type (str): The type of entity affected (e.g., "claim", "found_item").
        entity_id (int): The ID of the entity.
        performed_by (str): Username or identifier of the person performing the action.

    Returns:
        dict: Success message or error message with optional status_code.
    """
    try:
        # Validate required fields
        require_fields(
            {
                "action": action,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "performed_by": performed_by
            },
            ["action", "entity_type", "entity_id", "performed_by"]
        )

        # Validate entity_id is an integer
        validate_int(entity_id, "entity_id")

        # Insert into audit_logs
        """Log an action performed on an entity."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO audit_logs (action, entity_type, entity_id, performed_by, timestamp, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (action, entity_type, entity_id, performed_by, datetime.utcnow().isoformat(), notes))


        conn.commit()
        conn.close()

        return {"message": "Action logged successfully"}

    except ValidationError as ve:
        return {"error": ve.message}, ve.status_code

    except Exception as e:
        return {"error": f"Database error: {str(e)}"}