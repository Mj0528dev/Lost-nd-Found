import sqlite3
import os

DataBase = os.path.join(os.path.dirname(__file__), "database.db")

# Function to get a database connection
def get_db_connection():
    conn = sqlite3.connect(DataBase)
    conn.row_factory = sqlite3.Row
    return conn

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
            timestamp TEXT NOT NULL,
            notes TEXT 
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

