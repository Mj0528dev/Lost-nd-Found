from flask import Blueprint, request, jsonify
from backend.helpers.response import success_response, error_response
from backend.models import ValidationError
from backend.services.auth_service import login_user, register_user

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
