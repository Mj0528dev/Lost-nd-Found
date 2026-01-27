from backend.models import (
    get_pending_claims,
    verify_claim,
    require_fields,
    validate_claim_decision,
    ValidationError
)

def get_pending_claims_service():
    """Return pending claims"""
    claims = get_pending_claims()
    return claims, 200


def process_claim_verification(claim_id: int, data: dict, admin_username: str):
    """Validate and verify claim"""
    require_fields(data, ["decision"])
    validate_claim_decision(data["decision"])

    result, status = verify_claim(
        claim_id=claim_id,
        decision=data["decision"],
        admin_username=admin_username
    )
    return result, status
