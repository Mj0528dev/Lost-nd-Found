import sqlite3
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from backend.models.base import get_db_connection

DB_PATH = "database.db" 

# User Helper Functions
def hash_password(password: str) -> str:
    """Hash a password using werkzeug."""
    return generate_password_hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    """Check a password against its hash."""
    return check_password_hash(password_hash, password)


def create_user(username: str, password: str, role: str = "user"):
    """Add a user to the users table safely and handle duplicates."""
    try:
        hashed_password = hash_password(password)
        
        # Use context manager to safely open/close connection
        with sqlite3.connect(DB_PATH, timeout=10) as conn:
            c = conn.cursor()
            
            # Try inserting user
            try:
                c.execute(
                    """
                    INSERT INTO users (username, password_hash, role, created_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (username, hashed_password, role, datetime.now(timezone.utc).isoformat())
                )
                conn.commit()
                return {"message": "User created successfully"}
            
            except sqlite3.IntegrityError:
                # This happens if the username already exists
                return {"error": "Username already exists"}
    
    except sqlite3.OperationalError as e:
        # Handle rare DB lock or other operational errors
        return {"error": f"Database error: {str(e)}"}
    
    except Exception as e:
        # Catch-all for unexpected errors
        return {"error": f"Unexpected error: {str(e)}"}
    
def get_user(username: str):
    """Fetch a user by username. Returns dict or None."""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT id, username, password_hash, role, created_at FROM users WHERE username = ?", (username,))
        row = c.fetchone()
        if row:
            return {
                "id": row[0],
                "username": row[1],
                "password_hash": row[2],
                "role": row[3],
                "created_at": row[4]
            }
        return None

def create_default_admin():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if cursor.fetchone() is None:
        password_hash = hash_password("adminpassword")
        cursor.execute(
            "INSERT INTO users (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
            ("admin", password_hash, "admin", datetime.now(timezone.utc).isoformat())
        )
        conn.commit()
    conn.close()
