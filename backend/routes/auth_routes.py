from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token

from backend.helpers.response import success_response, error_response
from backend.models import ValidationError
from backend.helpers.user_helpers import get_user, verify_password
from backend.services.auth_service import register_user

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    try:
        result, status = register_user(data)
        return jsonify(success_response(result)), status
    except ValidationError as ve:
        return jsonify(error_response("VALIDATION_ERROR", ve.message)), 400


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

