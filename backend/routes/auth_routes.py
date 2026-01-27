from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token

from backend.helpers.response import success_response, error_response
from backend.models import ValidationError
from backend.helpers.validate_register import validate_registration_data
from backend.helpers.user_helpers import create_user, get_user, verify_password

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        user_data = validate_registration_data(request.get_json())
        result = create_user(**user_data)
        
        if result.get("message"):
            # create JWT token
            token = create_access_token(
                identity=user_data["username"],
                additional_claims={"role": user_data["role"]}
            )
            return jsonify(success_response({"token": token, "message": result["message"]})), 201
        
        return jsonify(error_response("CONFLICT", result.get("error", "Registration failed"))), 400

    except ValidationError as ve:
        return jsonify(error_response("VALIDATION_ERROR", ve.message)), ve.status_code
    

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    user = get_user(data.get("username"))

    if not user or not verify_password(data.get("password"), user["password_hash"]):
        return jsonify(
            error_response("AUTH_FAILED", "Invalid username or password")
        ), 401


    token = create_access_token(
        identity=user["username"],
        additional_claims={"role": user["role"]}
    )

    return jsonify(
        success_response({
            "token": token,
            "message": "Login successful"
        })
    ), 200

