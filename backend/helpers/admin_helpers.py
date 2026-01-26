from datetime import datetime, timezone
from models.base import get_db_connection  

# --- General audit logging ---
def log_audit_action(action: str, entity_type: str, entity_id: int, performed_by: str) -> dict:
    """Logs any action for audit purposes (not limited to admins)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO audit_logs (action, entity_type, entity_id, performed_by, timestamp)
        VALUES (?, ?, ?, ?, ?)
        """,
        (action, entity_type, entity_id, performed_by, datetime.now(timezone.utc).isoformat())
    )
    conn.commit()
    conn.close()
    return {"message": f"Action '{action}' logged for {entity_type} {entity_id} by {performed_by}."}
