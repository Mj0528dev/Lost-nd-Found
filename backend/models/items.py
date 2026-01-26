from datetime import datetime, timezone
from .base import get_db_connection
from .validators import ValidationError, require_fields, validate_int
from .audit import log_action
from typing import Optional, Dict, Any

# Lost Items
def create_lost_item(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a lost item record with validation and logging."""
    try:
        # Validate required fields
        require_fields(data, ["category", "last_seen_location", "last_seen_datetime"])

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO lost_items (
                category, item_type, last_seen_location,
                last_seen_datetime, public_description, private_details,
                status, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["category"],
            data.get("item_type", "Unknown"),
            data["last_seen_location"],
            data["last_seen_datetime"],
            data.get("public_description"),
            data.get("private_details"),
            "published",
            datetime.now(timezone.utc).isoformat()
        ))

        conn.commit()
        item_id = cursor.lastrowid

        # Log creation
        log_action("create", "lost_item", item_id, data.get("reported_by", "system"))

        return {"message": "Lost item created successfully", "item_id": item_id}

    except ValidationError as ve:
        return {"error": ve.message}

    except Exception as e:
        return {"error": f"Database error: {str(e)}"}

    finally:
        conn.close()

# Found Items
def create_found_item(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a found item record with validation and logging."""
    try:
        require_fields(data, ["category", "found_location", "found_datetime"])

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO found_items (
                category, item_type, color, brand,
                found_location, found_datetime,
                public_description, status, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["category"],
            data.get("item_type", "Unknown"),
            data.get("color"),
            data.get("brand"),
            data["found_location"],
            data["found_datetime"],
            data.get("public_description"),
            "published",
            datetime.now(timezone.utc).isoformat()
        ))

        conn.commit()
        item_id = cursor.lastrowid

        # Log creation
        log_action("create", "found_item", item_id, data.get("reported_by", "system"))

        return {"message": "Found item created successfully", "item_id": item_id}

    except ValidationError as ve:
        return {"error": ve.message}

    except Exception as e:
        return {"error": f"Database error: {str(e)}"}

    finally:
        conn.close()

# Get Found Items
def get_published_found_items() -> list[Dict[str, Any]]:
    """Return all published found items."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, category, item_type, color, brand,
               found_location, found_datetime, public_description
        FROM found_items
        WHERE status = 'published'
        ORDER BY created_at DESC
    """)

    items = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return items

# Get Found Item by ID
def get_found_item_by_id(item_id: int) -> Optional[Dict[str, Any]]:
    """Return a found item by ID. Validates ID type."""
    try:
        validate_int(item_id, "item_id")

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM found_items WHERE id = ?", (item_id,))
        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    finally:
        conn.close()
