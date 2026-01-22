import json
import sqlite3
import hashlib
import os   
from datetime import datetime, timezone
from services.claim_scoring import compute_claim_score


DataBase = "database.db"

# Function to get a database connection
def get_db_connection():
    conn = sqlite3.connect(DataBase)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize the database and create tables if they don't exist
# NOTE: For production with multiple processes, use database migrations (Alembic, Flyway)
# to ensure table creation runs only once and safely.
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # USERS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TEXT NOT NULL
        );
    """)

    # LOST ITEMS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lost_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            item_type TEXT NOT NULL,
            color TEXT,
            brand TEXT,
            last_seen_location TEXT NOT NULL,
            last_seen_datetime TEXT NOT NULL,
            public_description TEXT,
            private_details TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'published',
            created_at TEXT NOT NULL
        );
    """)

    # FOUND ITEMS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS found_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            item_type TEXT NOT NULL,
            color TEXT,
            brand TEXT,
            found_location TEXT NOT NULL,
            found_datetime TEXT NOT NULL,
            public_description TEXT,
            status TEXT NOT NULL DEFAULT 'published',
            created_at TEXT NOT NULL
        );
    """)

    # CLAIMS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS claims (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            found_item_id INTEGER NOT NULL,
            claimed_category TEXT,
            claimed_item_type TEXT,
            claimed_brand TEXT,
            claimed_color TEXT,
            claimed_location TEXT,
            claimed_private_details TEXT,
            score INTEGER,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (found_item_id) REFERENCES found_items(id)
        );
    """)

    # ADMINS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
    """)

    # AUDIT LOGS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            entity_id INTEGER NOT NULL,
            performed_by TEXT NOT NULL,
            timestamp TEXT NOT NULL
        );
    """)

    # ADMIN ACTIONS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin_actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_username TEXT NOT NULL,
            claim_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            notes TEXT,
            timestamp TEXT NOT NULL
        );
    """)

    conn.commit()
    conn.close()

def create_lost_item(data):
    """Create a lost item record with error handling."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO lost_items (
                category,
                item_type,
                last_seen_location,
                last_seen_datetime,
                public_description,
                private_details,
                status,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["category"],
            data.get("item_type", "Unknown"),
            data["last_seen_location"],
            data["last_seen_datetime"],
            data["public_description"],
            data.get("private_details"),
            "published",
            datetime.now(timezone.utc).isoformat()
        ))

        conn.commit()
        return {"message": "Lost item created successfully", "item_id": cursor.lastrowid}

    except Exception as e:
        return {"error": str(e)}

    finally:
        conn.close()

def create_found_item(data):
    """Create a found item record with error handling."""
    try:
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
        return {"message": "Found item created successfully", "item_id": cursor.lastrowid}

    except Exception as e:
        return {"error": str(e)}

    finally:
        conn.close()

def get_published_found_items():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, category, item_type, color, brand,
               found_location, found_datetime, public_description
        FROM found_items
        WHERE status = 'published'
        ORDER BY created_at DESC
    """)

    # Convert rows to dicts explicitly for consistency
    items = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return items

def get_found_item_by_id(item_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM found_items WHERE id = ?
    """, (item_id,))

    row = cursor.fetchone()
    conn.close()

    return dict(row) if row else None

def create_claim(data):
    conn = get_db_connection()
    cursor = conn.cursor()

    found_item = get_found_item_by_id(data["found_item_id"])
    if not found_item:
        return {"error": "Found item not found"}, 404

    score = compute_claim_score(data, found_item)

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
            # Convert dicts, lists, and other complex types to JSON strings
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            fields.append(key)
            placeholders.append("?")
            values.append(value)
    
    # Make sure score is primitive
    if isinstance(score, dict):
        score = score.get("score_value", 0)
    
    # Add score, status, created_at
    fields.extend(["score", "status", "created_at"])
    placeholders.extend(["?", "?", "?"])
    values.extend([score, "pending", datetime.now(timezone.utc).isoformat()])

    # Construct and execute the INSERT query
    query = f"""
        INSERT INTO claims ({", ".join(fields)})
        VALUES ({", ".join(placeholders)})
    """

    cursor.execute(query, values)
    conn.commit()
    conn.close()

    return {
        "message": "Claim submitted successfully",
        "score": score
    }, 201

def get_pending_claims():
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

    # Convert rows to dicts explicitly for consistency
    return [dict(row) for row in rows]

def update_claim_status(claim_id, new_status):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE claims
        SET status = ?
        WHERE id = ?
    """, (new_status, claim_id))

    conn.commit()
    conn.close()

def log_action(action, entity_type, entity_id, performed_by):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO audit_logs (
            action, entity_type, entity_id,
            performed_by, timestamp
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        action,
        entity_type,
        entity_id,
        performed_by,
        datetime.now(timezone.utc).isoformat()
    ))

    conn.commit()
    conn.close()

def update_claim(claim_id, data):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    ALLOWED_CLAIM_FIELDS = {
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
        if key in ALLOWED_CLAIM_FIELDS:
            updates.append(f"{key} = ?")
            values.append(value)

    if not updates:
        conn.close()
        return {"error": "No valid fields to update"}, 400

    values.append(claim_id)

    query = f"""
        UPDATE claims
        SET {", ".join(updates)}
        WHERE id = ?
    """

    cursor.execute(query, values)
    conn.commit()
    conn.close()

    return {"message": "Claim updated successfully"}, 200

def verify_claim(claim_id, decision, admin_username):
    if decision not in {"approved", "rejected"}:
        return {"error": "Invalid decision"}, 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Ensure claim exists and is pending
    cursor.execute(
        "SELECT status FROM claims WHERE id = ?",
        (claim_id,)
    )
    row = cursor.fetchone()

    if not row:
        conn.close()
        return {"error": "Claim not found"}, 404

    # Convert to dict explicitly for consistency (safe regardless of row_factory)
    row_dict = dict(row) if row else None
    
    if row_dict["status"] != "pending":
        conn.close()
        return {"error": "Claim already processed"}, 400

    # Update claim status
    cursor.execute(
        "UPDATE claims SET status = ? WHERE id = ?",
        (decision, claim_id)
    )

    # Log admin action
    cursor.execute("""
        INSERT INTO audit_logs (
            action,
            entity_type,
            entity_id,
            performed_by,
            timestamp
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        decision,
        "claim",
        claim_id,
        admin_username,
        datetime.now(timezone.utc).isoformat()
    ))

    conn.commit()
    conn.close()

    return {"message": f"Claim {decision} successfully"}, 200

def hash_password(password: str) -> str:
    """Return a salted hash of the password.
    
    NOTE: SHA-256 + salt is suitable for learning/development.
    For production, use bcrypt or Argon2 for better security against brute-force attacks.
    Example: bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    """
    salt = os.urandom(16).hex()
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}${hashed}"

def verify_password(password: str, stored_hash: str) -> bool:
    """Verify a password against stored hash.
    
    NOTE: This uses SHA-256. For production, use bcrypt or Argon2.
    Example: bcrypt.checkpw(password.encode(), stored_hash)
    """
    try:
        salt, hashed = stored_hash.split("$")
        return hashlib.sha256((salt + password).encode()).hexdigest() == hashed
    except ValueError:
        return False

def create_user(username: str, password: str, role: str = "user"):
    """Add a user safely, handle duplicate usernames."""
    try:
        conn = sqlite3.connect(DataBase)
        c = conn.cursor()

        password_hash = hash_password(password)

        c.execute(
            "INSERT INTO users (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
            (username, password_hash, role, datetime.now(timezone.utc).isoformat())
        )
        conn.commit()
        return {"message": f"User '{username}' created successfully", "username": username, "role": role}

    except sqlite3.IntegrityError:
        return {"error": f"Username '{username}' already exists"} 

    except Exception as e:
        return {"error": str(e)} 

    finally:
        conn.close() 

def get_user(username: str):
    """Fetch a user record by username."""
    conn = get_db_connection()  # Use get_db_connection() for consistency with row_factory
    c = conn.cursor()
    c.execute(
        "SELECT id, username, password_hash, role, created_at FROM users WHERE username = ?",
        (username,)
    )
    user = c.fetchone()
    conn.close()
    return dict(user) if user else None


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully")