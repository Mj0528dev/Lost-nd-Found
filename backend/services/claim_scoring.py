from config.claim_scoring import SCORING_RULES


def normalize(value):
    return value.strip().lower() if value else None

def matches(a, b):
    return normalize(a) == normalize(b)

def compute_claim_score(claim_data, found_item):
    score = 0

    comparisons = [
        ("claimed_category", found_item["category"], SCORING_RULES["category"]),
        ("claimed_item_type", found_item["item_type"], SCORING_RULES["item_type"]),
        ("claimed_brand", found_item["brand"], SCORING_RULES["brand"]),
        ("claimed_color", found_item["color"], SCORING_RULES["color"]),
        ("claimed_location", found_item["found_location"], SCORING_RULES["location"]),
        ("claimed_private_details", found_item["public_description"], SCORING_RULES["private_details"]),
    ]

    for claim_key, found_value, weight in comparisons:
        if matches(claim_data.get(claim_key), found_value):
            score += weight

    return score
