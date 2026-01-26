def no_receipt(data):
    return not data.get("receipt")

def high_amount(data):
    return data.get("amount", 0) > 5000

def missing_description(data):
    return not data.get("description")


VALIDATION_RULES = [
    (no_receipt, "No receipt uploaded"),
    (high_amount, "Unusually high claim amount"),
    (missing_description, "Missing description"),
]


def validate_claim_data(data):
    """
    Runs all claim validation rules.
    Returns a list of error messages.
    """
    errors = []

    for rule, message in VALIDATION_RULES:
        try:
            if rule(data):
                errors.append(message)
        except Exception as e:
            errors.append(f"Validation error: {rule.__name__} failed")

    return errors
