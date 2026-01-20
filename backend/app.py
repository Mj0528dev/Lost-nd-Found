from flask import Flask, request, jsonify
from models import (
    create_lost_item,
    create_found_item,
    create_claim,
    get_pending_claims,
    get_published_found_items,
    update_claim,
    verify_claim
)

app = Flask(__name__)

# LOST ITEM REPORT
@app.route("/lost", methods=["POST"])
def report_lost_item():
    data = request.json or {}

    category = data.get("category")
    last_seen_location = data.get("last_seen_location")
    lost_datetime = data.get("lost_datetime")
    public_description = data.get("public_description")
    private_details = data.get("private_details")  # optional

    required_fields = {
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

    create_lost_item({
        "category": category,
        "last_seen_location": last_seen_location,
        "lost_datetime": lost_datetime,
        "public_description": public_description,
        "private_details": private_details
    })

    return jsonify({"message": "Lost item reported successfully"}), 201

# FOUND ITEM REPORT / LISTING
@app.route("/found", methods=["GET", "POST"])
def found_items():

    # POST method
    if request.method == "POST":
        data = request.get_json() or {}

        category = data.get("category")
        found_location = data.get("found_location")
        found_datetime = data.get("found_datetime")
        public_description = data.get("public_description")  # optional

        required_fields = {
            "category": category,
            "found_location": found_location,
            "found_datetime": found_datetime
        }

        missing_fields = [f for f, v in required_fields.items() if not v]
        if missing_fields:
            return jsonify({
                "error": "Missing required fields",
                "missing_fields": missing_fields
            }), 400

        create_found_item({
            "category": category,
            "found_location": found_location,
            "found_datetime": found_datetime,
            "public_description": public_description
        })

        return jsonify({"message": "Found item reported successfully"}), 201

    # GET method
    items = get_published_found_items()
    return jsonify(items), 200

# SUBMIT CLAIM FOR FOUND ITEM
@app.route("/claim", methods=["POST"])
def submit_claim():
    data = request.json or {}

    # Check for required fields
    missing = [k for k in ("found_item_id",) if not data.get(k)]
    if missing:
        return jsonify({"error": "Missing required fields", "missing_fields": missing}), 400

    # Create claim
    claim_result, status = create_claim(data)
    return jsonify(claim_result), status


# ADMIN VIEW PENDING CLAIMS
@app.route("/admin/claims", methods=["GET"])
def view_pending_claims():
    return jsonify(get_pending_claims()), 200

@app.route("/claims/<int:claim_id>", methods=["PATCH"])
def patch_claim(claim_id):
    data = request.get_json()

    # Validate input
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Update claim
    result, status = update_claim(claim_id, data)

    return jsonify(result), status

@app.route("/admin/claims/<int:claim_id>/verify", methods=["POST"])
def admin_verify_claim(claim_id):
    data = request.get_json()

    decision = data.get("decision")
    admin_username = data.get("admin_username")

    if not decision or not admin_username:
        return {"error": "decision and admin_username are required"}, 400

    return verify_claim(claim_id, decision, admin_username)

if __name__ == "__main__":
    from models import init_db
    init_db()  # create tables if they don't exist
    app.run(debug=True, host="0.0.0.0", port=5000)
