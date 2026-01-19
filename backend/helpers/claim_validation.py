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
