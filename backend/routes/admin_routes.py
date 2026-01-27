from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from functools import wraps
from backend.services.admin_service import get_pending_claims_service, process_claim_verification
from backend.helpers.response import success_response, error_response
from backend.models import ValidationError

admin_bp = Blueprint("admin", __name__)

# Thin admin check decorator
def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if get_jwt().get("role") != "admin":
            return jsonify(error_response("FORBIDDEN", "Admin access required")), 403
        return fn(*args, **kwargs)
    return wrapper


@admin_bp.route("/claims", methods=["GET"])
@jwt_required()
@admin_required
def view_claims():
    try:
        claims, status = get_pending_claims_service()
        return jsonify(success_response(claims)), status
    except ValidationError as ve:
        return jsonify(error_response("VALIDATION_ERROR", ve.message)), ve.status_code


@admin_bp.route("/claims/<int:claim_id>/verify", methods=["POST"])
@jwt_required()
@admin_required
def verify_claim_route(claim_id):
    data = request.json or {}
    try:
        result, status = process_claim_verification(
            claim_id, data, get_jwt_identity()
        )
        return jsonify(success_response(result)), status
    except ValidationError as ve:
        return jsonify(error_response("VALIDATION_ERROR", ve.message)), ve.status_code
