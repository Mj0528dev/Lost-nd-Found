from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from backend.services.auth_service import register_user, login_user, refresh_token, logout_token
from backend.helpers.response import success_response, error_response
from backend.models import ValidationError

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
    data = request.get_json() or {}
    try:
        result, status = login_user(data)
        return jsonify(success_response(result)), status
    except ValidationError as ve:
        return jsonify(error_response("VALIDATION_ERROR", ve.message)), 401

@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    try:
        identity = get_jwt_identity()
        result, status = refresh_token(identity)
        return jsonify(success_response(result)), status
    except ValidationError as ve:
        return jsonify(error_response("VALIDATION_ERROR", ve.message)), 401

@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    try:
        jti = get_jwt()["jti"]
        result, status = logout_token(jti)
        return jsonify(success_response(result)), status
    except ValidationError as ve:
        return jsonify(error_response("VALIDATION_ERROR", ve.message)), 400