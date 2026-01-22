import sqlite3
from datetime import datetime, timezone

DB_PATH = "database.db"

def log_admin_action(admin_username: str, claim_id: int, action: str, notes: str = ""):
    """
    Logs an admin action for audit purposes.
    action: 'approved', 'rejected', 'manual_override', etc.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO audit_logs (action, entity_type, entity_id, performed_by, timestamp)
        VALUES (?, ?, ?, ?, ?)
        """,
        (action, "claim", claim_id, admin_username, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()
    return {"message": f"Action '{action}' logged for claim {claim_id} by {admin_username}."}

def get_admin_logs(admin_username: str = None):
    """Retrieve admin actions; filter by username if provided."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if admin_username:
        c.execute("SELECT * FROM audit_logs WHERE performed_by = ?", (admin_username,))
    else:
        c.execute("SELECT * FROM audit_logs")
    logs = c.fetchall()
    conn.close()
    return logs
