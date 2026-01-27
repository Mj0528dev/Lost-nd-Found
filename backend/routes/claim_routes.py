from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.claim_service import submit_claim
from backend.helpers.response import success_response, error_response
from backend.models import ValidationError

claim_bp = Blueprint("claims", __name__)

@claim_bp.route("/claim", methods=["POST"])
@jwt_required()
def submit_claim_route():
    data = request.json or {}
    try:
        identity = get_jwt_identity()
        minimal_identity = {"user_id": identity["user_id"], "role": identity["role"]}
        result, status = submit_claim(data, minimal_identity)
        return jsonify(success_response(result)), status
    except ValidationError as ve:
        return jsonify(error_response("VALIDATION_ERROR", ve.message)), ve.status_code
