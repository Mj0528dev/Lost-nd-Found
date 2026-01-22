import requests
import sqlite3
from helpers.user_helpers import init_db, DB_PATH

# ----------------------------
# Initialize DB before tests
# ----------------------------
init_db()

BASE_URL = "http://127.0.0.1:5000/api"

# ----------------------------
# Helper to reset test users
# ----------------------------
def reset_users():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE username LIKE 'testuser%' OR username LIKE 'admin%'")
    conn.commit()
    conn.close()
    print("Test users cleared.")

# ----------------------------
# Phase 2: API Integration & Auth Tests
# ----------------------------
def test_register_users():
    reset_users()  # ensure clean start

    users = [
        {"username": "testuser1", "password": "pass123", "role": "user"},
        {"username": "admin1", "password": "adminpass", "role": "admin"}
    ]

    for user in users:
        resp = requests.post(f"{BASE_URL}/register", json=user)
        print(f"{user['username']}: {resp.status_code}, {resp.json()}")

def test_login_users():
    users = [
        {"username": "testuser1", "password": "pass123"},
        {"username": "admin1", "password": "adminpass"}
    ]

    for user in users:
        resp = requests.post(f"{BASE_URL}/login", json=user)
        print(f"{user['username']} login: {resp.status_code}, {resp.json()}")


if __name__ == "__main__":
    print("=== Phase 2: API Integration & Auth Tests ===\n")
    test_register_users()
    print("\n--- Login Users ---")
    test_login_users()
