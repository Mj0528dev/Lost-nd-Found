from flask import Flask, request, jsonify
from models import (
    create_lost_item,
    create_found_item,
    create_claim,
    get_pending_claims,
    update_claim,
    verify_claim
)

app = Flask(__name__)

# LOST ITEM REPORT
@app.route("/lost", methods=["POST"])
def report_lost_item():
    data = request.json or {}

    user_id = data.get("user_id")
    category = data.get("category")
    last_seen_location = data.get("last_seen_location")
    lost_datetime = data.get("lost_datetime")
    public_description = data.get("public_description")
    private_details = data.get("private_details")  # optional

    required_fields = {
        "user_id": user_id,
        "category": category,
        "last_seen_location": last_seen_location,
        "lost_datetime": lost_datetime,
        "public_description": public_description
    }

    missing_fields = [
        field for field, value in required_fields.items() if not value
    ]

    if missing_fields:
        return jsonify({
            "error": "Missing required fields",
            "missing_fields": missing_fields
        }), 400

    create_lost_item(
        user_id = user_id,
        category = category,
        last_seen_location = last_seen_location,
        lost_datetime = lost_datetime,
        public_description = public_description,
        private_details = private_details
    )

    return jsonify({"message": "Lost item reported successfully"}), 201

# FOUND ITEM REPORT
@app.route("/found", methods=["POST"])
def report_found_item():
    data = request.json or {}

    user_id = data.get("user_id")
    category = data.get("category")
    found_location = data.get("found_location")
    found_datetime = data.get("found_datetime")
    public_description = data.get("public_description")  # optional

    required_fields = {
        "user_id": user_id,
        "category": category,
        "found_location": found_location,
        "found_datetime": found_datetime
    }

    missing_fields = [
        field for field, value in required_fields.items() if not value
    ]

    if missing_fields:
        return jsonify({
            "error": "Missing required fields",
            "missing_fields": missing_fields
        }), 400

    create_found_item(
        user_id = user_id,
        category = category,
        found_location = found_location,
        found_datetime = found_datetime,
        public_description = public_description
    )

    return jsonify({"message": "Found item reported successfully"}), 201

# SUBMIT CLAIM FOR FOUND ITEM
@app.route("/claim", methods=["POST"])
def submit_claim():
    data = request.json or {}

    user_id = data.get("user_id")
    found_item_id = data.get("found_item_id")

    # hard validation (blocking)
    missing = [k for k, v in {
        "user_id": user_id,
        "found_item_id": found_item_id
    }.items() if not v]

    if missing:
        return jsonify({
            "error": "Missing required fields",
            "missing_fields": missing
        }), 400

    # delegate everything else
    claim_id, warnings = create_claim(data)

    return jsonify({
        "message": "Claim submitted and pending verification",
        "claim_id": claim_id,
        "warnings": warnings  # soft validation
    }), 201

# ADMIN VIEW PENDING CLAIMS
@app.route("/admin/claims", methods=["GET"])
def view_pending_claims():
    return jsonify(get_pending_claims()), 200

@app.route("/claims/<int:claim_id>", methods=["PATCH"])
def patch_claim(claim_id):
    data = request.get_json()

    if not data:
        return {"error": "No data provided"}, 400

    return update_claim(claim_id, data)

@app.route("/admin/claims/<int:claim_id>/verify", methods=["POST"])
def admin_verify_claim(claim_id):
    data = request.get_json()

    decision = data.get("decision")
    admin_username = data.get("admin_username")

    if not decision or not admin_username:
        return {"error": "decision and admin_username are required"}, 400

    return verify_claim(claim_id, decision, admin_username)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
