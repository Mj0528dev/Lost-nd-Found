from flask import Flask, request, jsonify
from datetime import timedelta
from helpers.user_helpers import create_user, get_user, verify_password, create_default_admin 
from flask_jwt_extended import JWTManager, create_access_token, get_jwt, jwt_required, get_jwt_identity
from models import (
    create_lost_item,
    create_found_item,
    get_published_found_items,
    create_claim,
    get_pending_claims,
    update_claim_status,
    verify_claim,
    init_db,
    ValidationError,
    require_fields,
    validate_found_item_id,
    validate_claim_decision,
)
from functools import wraps
from flask_jwt_extended import get_jwt

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims.get("role") != "admin":
            return jsonify({"error": "Admin access required"}), 403
        return fn(*args, **kwargs)
    return wrapper


app = Flask(__name__)

# JWT CONFIG
JWT_SECRET = "dev-secret-change-later"
JWT_ALGORITHM = "HS256"
JWT_EXP_MINUTES = 60

app.config["JWT_SECRET_KEY"] = JWT_SECRET
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=JWT_EXP_MINUTES)

jwt = JWTManager(app)

# REGISTER ROUTE
@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    username = data.get("username")
    password = data.get("password")
    role = data.get("role", "user")  # default role

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    result = create_user(username, password, role)

    if result.get("message"):
        # Successful registration → issue JWT
        access_token = create_access_token(
            identity=username,  # must be a string
            additional_claims={"role": role}  # store role in claims
        )
        return jsonify({
            "token": access_token,
            "message": f"User {username} registered successfully"
        }), 201
    else:
        return jsonify(result), 400

# LOGIN ROUTE
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user = get_user(username)

    if not user or not verify_password(password, user["password_hash"]):
        return jsonify({"error": "Invalid username or password"}), 401

    access_token = create_access_token(
        identity=username,
        additional_claims={"role": user["role"]}
    )
    return jsonify({
        "token": access_token,
        "message": f"User {username} logged in successfully"
    }), 200

# LOST ITEM REPORT
@app.route("/api/lost", methods=["POST"])
@jwt_required()
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

    try:
        require_fields(data, ["category", "last_seen_location", "lost_datetime", "public_description"])
    except ValidationError as ve:
        return jsonify({"error": ve.message}), ve.status_code

    create_lost_item({
        "category": category,
        "last_seen_location": last_seen_location,
        "lost_datetime": lost_datetime,
        "public_description": public_description,
        "private_details": private_details
    })

    return jsonify({"message": "Lost item reported successfully"}), 201

# FOUND ITEM REPORT / LISTING
@app.route("/api/found", methods=["GET", "POST"])
@jwt_required()
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

        try:
            require_fields(data, ["category", "found_location", "found_datetime"])
        except ValidationError as ve:
            return jsonify({"error": ve.message}), ve.status_code

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
@app.route("/api/claim", methods=["POST"])
@jwt_required()
def submit_claim():
    data = request.json or {}

    # Check for required fields
    try:
        require_fields(data, ["found_item_id"])
        validate_found_item_id(data["found_item_id"])
    except ValidationError as ve:
        return jsonify({"error": ve.message}), ve.status_code

    # Create claim
    identity = get_jwt_identity()
    data["claimed_by"] = identity
    claim_result, status = create_claim(data)

    return jsonify(claim_result), status 

# ADMIN VIEW PENDING CLAIMS
@app.route("/api/admin/claims", methods=["GET"])
@jwt_required()
@admin_required
def view_pending_claims():
    return jsonify(get_pending_claims()), 200

@app.route("/api/admin/claims/<int:claim_id>/verify", methods=["POST"])
@jwt_required()
@admin_required
def admin_verify_claim(claim_id):
    data = request.get_json() or {}

    try:
        require_fields(data, ["decision", "admin_username"])
        validate_claim_decision(data["decision"])
    except ValidationError as ve:
        return jsonify({"error": ve.message}), ve.status_code

    admin_username = get_jwt_identity()

    result, status = verify_claim(
        claim_id=claim_id,
        decision=data["decision"],
        admin_username=admin_username
    )

    return jsonify(result), status

if __name__ == "__main__":
    init_db()
    create_default_admin()  
    app.run(debug=True, host="0.0.0.0", port=5000)
