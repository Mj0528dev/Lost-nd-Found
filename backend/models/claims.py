from datetime import datetime, timezone
from .audit import log_action
from .items import get_found_item_by_id
from backend.services.claim_scoring import compute_claim_score
from .base import get_db_connection
from .validators import (
    ValidationError,
    require_fields,
    validate_int,
    validate_found_item_id,
    validate_claim_decision
)
import json

# CREATE CLAIM
def create_claim(data):
    """Create a claim with score computation and validation."""
    try:
        require_fields(data, ["found_item_id"])
        validate_found_item_id(data["found_item_id"])

        found_item = get_found_item_by_id(data["found_item_id"])
        if not found_item:
            return {"error": "Found item not found"}, 404

        score = compute_claim_score(data, found_item)
        if isinstance(score, dict):
            score = score.get("total", 0) 
            
        ALLOWED_FIELDS = {
            "found_item_id",
            "claimed_category",
            "claimed_item_type",
            "claimed_brand",
            "claimed_color",
            "claimed_location",
            "claimed_private_details"
        }

        fields, placeholders, values = [], [], []

        for key, value in data.items():
            if key in ALLOWED_FIELDS:
                if isinstance(value, (dict, list)):
                    value = json.dumps(value)
                fields.append(key)
                placeholders.append("?")
                values.append(value)

        fields.extend(["score", "status", "created_at"])
        placeholders.extend(["?", "?", "?"])
        values.extend([score, "pending", datetime.now(timezone.utc).isoformat()])

        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = f"INSERT INTO claims ({', '.join(fields)}) VALUES ({', '.join(placeholders)})"
            cursor.execute(query, values)
            claim_id = cursor.lastrowid

        # Log creation action
        log_action("create", "claim", claim_id, data.get("claimed_by", "system"))

        return {
            "message": "Claim submitted successfully", 
            "score": score,
            "claim_id": claim_id
        }, 201

    except ValidationError as ve:
        return {"error": ve.message}, ve.status_code

    except Exception as e:
        return {"error": f"Database error: {str(e)}"}

# GET PENDING CLAIMS
def get_pending_claims():
    """Return all pending claims with found item info."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT
            c.id AS claim_id,
            c.found_item_id,
            c.claimed_category,
            c.claimed_item_type,
            c.claimed_brand,
            c.claimed_color,
            c.claimed_location,
            c.claimed_private_details,
            c.score,
            c.status,
            c.created_at,

            f.category AS found_category,
            f.item_type AS found_item_type,
            f.brand AS found_brand,
            f.color AS found_color,
            f.found_location,
            f.public_description
        FROM claims c
        JOIN found_items f ON c.found_item_id = f.id
        WHERE c.status = 'pending'
        ORDER BY c.created_at ASC
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]

# UPDATE CLAIM STATUS
def update_claim_status(claim_id, new_status):
    """Update status of a claim with validation."""
    try:
        validate_int(claim_id, "claim_id")

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM claims WHERE id = ?", (claim_id,))
            if not cursor.fetchone():
                return {"error": "Claim not found"}, 404

            cursor.execute("UPDATE claims SET status = ? WHERE id = ?", (new_status, claim_id))

        log_action("update_status", "claim", claim_id, "system")
        return {"message": "Claim status updated"}, 200

    except ValidationError as ve:
        return {"error": ve.message}, ve.status_code

# UPDATE CLAIM
def update_claim(claim_id, data):
    """Update claim fields with validation."""
    try:
        validate_int(claim_id, "claim_id")

        ALLOWED_FIELDS = {
            "claimed_category",
            "claimed_item_type",
            "claimed_brand",
            "claimed_color",
            "claimed_location",
            "claimed_private_details",
            "status"
        }

        updates = []
        values = []

        for key, value in data.items():
            if key in ALLOWED_FIELDS:
                updates.append(f"{key} = ?")
                values.append(value)

        if not updates:
            return {"error": "No valid fields to update"}, 400

        values.append(claim_id)

        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = f"UPDATE claims SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, values)

        log_action("update", "claim", claim_id, "system")
        return {"message": "Claim updated successfully"}, 200

    except ValidationError as ve:
        return {"error": ve.message}, ve.status_code

# VERIFY CLAIM
def verify_claim(claim_id, decision, admin_username):
    """Approve or reject a claim and log the action."""
    try:
        validate_int(claim_id, "claim_id")
        validate_claim_decision(decision)

        with get_db_connection() as conn:
            cursor = conn.cursor()
            row = cursor.execute("SELECT status FROM claims WHERE id = ?", (claim_id,)).fetchone()
            if not row:
                return {"error": "Claim not found"}, 404
            if row["status"] != "pending":
                return {"error": "Claim already processed"}, 400

            cursor.execute("UPDATE claims SET status = ? WHERE id = ?", (decision, claim_id))

        log_action(decision, "claim", claim_id, admin_username)
        return {"message": f"Claim {decision} successfully"}, 200

    except ValidationError as ve:
        return {"error": ve.message}, ve.status_code

    except Exception as e:
        return {"error": f"Database error: {str(e)}"}
