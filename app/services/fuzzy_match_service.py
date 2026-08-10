from __future__ import annotations

from typing import Any

from rapidfuzz import fuzz

DEFAULT_SIMILARITY_THRESHOLD = 90.0

def _normalize_text(value: Any) -> str:

    if value is None:

        return ""

    return str(value).strip().lower()

def _validate_threshold(threshold: float) -> None:

    if not 0 <= threshold <= 100:

        raise ValueError("Similarity threshold must be between 0 and 100")

def calculate_similarity(value_1: Any, value_2: Any) -> float:

    normalized_value_1 = _normalize_text(value_1)

    normalized_value_2 = _normalize_text(value_2)

    if not normalized_value_1 or not normalized_value_2:

        return 0.0

    return float(fuzz.ratio(normalized_value_1, normalized_value_2))

def is_probable_match(value_1: Any, value_2: Any, threshold: float = DEFAULT_SIMILARITY_THRESHOLD) -> bool:
   
    _validate_threshold(threshold)

    score = calculate_similarity(value_1, value_2)

    return score >= threshold

def fuzzy_match(value_1: Any, value_2: Any, threshold: float = DEFAULT_SIMILARITY_THRESHOLD) -> dict[str, Any]:
   
    _validate_threshold(threshold)

    score = calculate_similarity(value_1, value_2)

    return {"score": score, "threshold": threshold, "matched": score >= threshold}

def fuzzy_match_field(left_value: Any,
                      right_value: Any,
                      field_name: str,
                      threshold: float = DEFAULT_SIMILARITY_THRESHOLD) -> dict[str, Any]:

    if not field_name or not field_name.strip():

        raise ValueError("field_name must identify a supported secondary textual field")

    result = fuzzy_match(left_value, right_value, threshold=threshold)

    return {"field": field_name,
            "left_value": left_value,
            "right_value": right_value,
            "score": result["score"],
            "threshold": result["threshold"],
            "matched": result["matched"]}