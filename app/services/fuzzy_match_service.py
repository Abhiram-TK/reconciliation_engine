from rapidfuzz import fuzz

DEFAULT_SIMILARITY_THRESHOLD = 90.0

def _normalize_text(value: object) -> str:
 
    if value is None:

        return ""

    return str(value).strip().casefold()

def calculate_similarity(value_1: object, value_2: object) -> float:
    
    normalized_value_1 = _normalize_text(value_1)
    normalized_value_2 = _normalize_text(value_2)

    if not normalized_value_1 or not normalized_value_2:

        return 0.0

    return float(fuzz.ratio(normalized_value_1, normalized_value_2))

def is_probable_match(value_1: object, value_2: object, threshold: float = DEFAULT_SIMILARITY_THRESHOLD) -> bool:
 
    if not 0 <= threshold <= 100:

        raise ValueError("Similarity threshold must be between 0 and 100.")

    score = calculate_similarity(value_1, value_2)

    return score >= threshold

def fuzzy_match(value_1: object,value_2: object, threshold: float = DEFAULT_SIMILARITY_THRESHOLD) -> dict:

    if not 0 <= threshold <= 100:

        raise ValueError("Similarity threshold must be between 0 and 100.")

    score = calculate_similarity(value_1, value_2)

    return {"score": score, "threshold": float(threshold), "matched": score >= threshold}