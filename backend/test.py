import sys
from datetime import datetime, timezone

from backend.models.base import init_db, get_db_connection
from backend.models.items import create_found_item, get_found_item_by_id
from backend.models.claims import create_claim, verify_claim
from backend.models.audit import log_action
from backend.helpers.claim_validation import validate_claim_data
from backend.services.claim_scoring import compute_claim_score
from backend.helpers.user_helpers import create_default_admin


# ==================================================
# SIMPLE TEST UTILITIES
# ==================================================

def fail(msg):
    print(f"[FAIL] {msg}")
    sys.exit(1)

def pass_test(msg):
    print(f"[PASS] {msg}")


# ==================================================
# 0️⃣ DATABASE CLEANUP
# ==================================================

print("\n--- DATABASE CLEANUP ---")
try:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = OFF;")

    tables = [
        "users",
        "admins",
        "lost_items",
        "found_items",
        "claims",
        "audit_logs",
        "admin_actions"
    ]

    for table in tables:
        cursor.execute(f"DELETE FROM {table};")
        cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}';")

    cursor.execute("PRAGMA foreign_keys = ON;")
    conn.commit()
    conn.close()

    pass_test("Database cleanup completed")

except Exception as e:
    fail(f"Database cleanup failed → {e}")


# ==================================================
# 1️⃣ DATABASE INIT
# ==================================================

print("\n--- DATABASE INITIALIZATION ---")
try:
    init_db()
    create_default_admin()
    pass_test("Database initialized + default admin created")
except Exception as e:
    fail(f"Database init failed → {e}")


# ==================================================
# 2️⃣ TABLE CHECK
# ==================================================

print("\n--- TABLE CHECK ---")
try:
    conn = get_db_connection()
    cursor = conn.cursor()

    required_tables = [
        "users",
        "admins",
        "lost_items",
        "found_items",
        "claims",
        "audit_logs",
        "admin_actions"
    ]

    for table in required_tables:
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table,)
        )
        if not cursor.fetchone():
            fail(f"Missing table: {table}")

    conn.close()
    pass_test("All required tables exist")

except Exception as e:
    fail(f"Table check failed → {e}")


# ==================================================
# 3️⃣ CREATE FOUND ITEM
# ==================================================

print("\n--- FOUND ITEM CREATION ---")
try:
    result = create_found_item({
        "category": "Electronics",
        "item_type": "Phone",
        "color": "Black",
        "brand": "Samsung",
        "found_location": "Library",
        "found_datetime": datetime.now(timezone.utc).isoformat(),
        "public_description": "Black Samsung phone near the entrance"
    })

    found_item_id = result.get("item_id")
    if not found_item_id:
        fail("Found item ID not returned")

    pass_test(f"Found item created (id={found_item_id})")

except Exception as e:
    fail(f"Create found item failed → {e}")


# ==================================================
# 4️⃣ GET FOUND ITEM
# ==================================================

print("\n--- FOUND ITEM RETRIEVAL ---")
try:
    item = get_found_item_by_id(found_item_id)

    if not item:
        fail("Found item not retrieved")

    if item["item_type"] != "Phone":
        fail("Found item data mismatch")

    pass_test("Found item retrieved correctly")

except Exception as e:
    fail(f"Get found item failed → {e}")


# ==================================================
# 5️⃣ CLAIM VALIDATION
# ==================================================

print("\n--- CLAIM VALIDATION ---")

valid_claim = {
    "found_item_id": found_item_id,
    "claimed_category": "Electronics",
    "claimed_item_type": "Phone",
    "claimed_color": "Black",
    "receipt": True,
    "description": "Lost my Samsung phone",
    "amount": 1000
}

errors = validate_claim_data(valid_claim)
if errors:
    fail(f"Unexpected validation errors → {errors}")

pass_test("Valid claim passed validation")

print("\n--- CLAIM VALIDATION (NEGATIVE CASE) ---")

invalid_claim = {
    "amount": 6000,
    "description": "",
    "receipt": None
}

errors = validate_claim_data(invalid_claim)

expected_errors = [
    "No receipt uploaded",
    "Unusually high claim amount",
    "Missing description"
]

for err in expected_errors:
    if err not in errors:
        fail(f"Expected error missing → {err}")

pass_test("Invalid claim returned expected validation errors")


# ==================================================
# 6️⃣ CLAIM SCORING
# ==================================================

print("\n--- CLAIM SCORING ---")
try:
    score = compute_claim_score(valid_claim, item)

    total = score.get("total")
    if not isinstance(total, (int, float)):
        fail("Score total is not numeric")

    pass_test(f"Claim score computed (total={total})")

except Exception as e:
    fail(f"Claim scoring failed → {e}")


# ==================================================
# 7️⃣ CREATE CLAIM
# ==================================================

print("\n--- CLAIM CREATION ---")
try:
    result, status = create_claim({
        "found_item_id": found_item_id,
        "claimed_category": "Electronics",
        "claimed_item_type": "Phone",
        "claimed_brand": "Samsung",
        "claimed_color": "Black",
        "claimed_private_details": "Cracked screen"
    })

    if status != 201:
        fail(f"Claim creation failed → {result}")

    claim_id = result.get("claim_id")
    if not claim_id:
        fail("Claim ID not returned")

    pass_test(f"Claim created (id={claim_id})")

except Exception as e:
    fail(f"Create claim failed → {e}")


# ==================================================
# 8️⃣ VERIFY CLAIM (ADMIN)
# ==================================================

print("\n--- CLAIM VERIFICATION ---")
try:
    result, status = verify_claim(
        claim_id=claim_id,
        decision="approved",
        admin_username="admin"
    )

    if status != 200:
        fail(f"Verify claim failed → {result}")

    pass_test("Claim verified successfully")

except Exception as e:
    fail(f"Verify claim crashed → {e}")


# ==================================================
# 9️⃣ AUDIT LOGGING
# ==================================================

print("\n--- AUDIT LOGGING ---")
try:
    log_action(
        action="TEST_RUN",
        entity_type="claim",
        entity_id=claim_id,
        performed_by="test_runner",
        notes="Phase 3 integration test"
    )

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM audit_logs WHERE entity_id=?",
        (claim_id,)
    )
    count = cursor.fetchone()[0]
    conn.close()

    if count == 0:
        fail("Audit log not written")

    pass_test("Audit log written")

except Exception as e:
    fail(f"Audit logging failed → {e}")


print("\n✅ ALL PHASE 3 TESTS PASSED SUCCESSFULLY")