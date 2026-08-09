import pytest

from app.services.fuzzy_match_service import (DEFAULT_SIMILARITY_THRESHOLD, calculate_similarity, is_probable_match, fuzzy_match)

def test_calculate_similarity_exact_match():

    score = calculate_similarity("ABC Corporation", "ABC Corporation")

    assert score == 100.0

def test_calculate_similarity_is_case_insensitive():

    score = calculate_similarity("ABC Corporation", "abc corporation")

    assert score == 100.0

def test_calculate_similarity_ignores_surrounding_whitespace():

    score = calculate_similarity("  ABC Corporation  ", "ABC Corporation")

    assert score == 100.0

def test_calculate_similarity_returns_lower_score_for_different_values():

    score = calculate_similarity("ABC Corporation", "XYZ Industries")

    assert 0.0 <= score < 90.0

def test_calculate_similarity_returns_zero_for_missing_left_value():

    score = calculate_similarity(None, "ABC Corporation")

    assert score == 0.0

def test_calculate_similarity_returns_zero_for_missing_right_value():

    score = calculate_similarity("ABC Corporation", None)

    assert score == 0.0

def test_calculate_similarity_returns_zero_for_empty_left_value():

    score = calculate_similarity("", "ABC Corporation")

    assert score == 0.0

def test_calculate_similarity_returns_zero_for_empty_right_value():

    score = calculate_similarity("ABC Corporation", "")

    assert score == 0.0

def test_default_similarity_threshold_is_90():

    assert DEFAULT_SIMILARITY_THRESHOLD == 90.0

def test_is_probable_match_accepts_exact_match():

    result = is_probable_match("ABC Corporation", "ABC Corporation")

    assert result is True

def test_is_probable_match_rejects_low_similarity():

    result = is_probable_match("ABC Corporation", "XYZ Industries")

    assert result is False

def test_is_probable_match_uses_explicit_threshold():

    value_1 = "ABC Corporation"
    value_2 = "ABC Corp"

    score = calculate_similarity(value_1,  value_2)

    assert score < 100.0

    assert is_probable_match(value_1, value_2, threshold=score) is True

    assert is_probable_match(value_1, value_2, threshold=score + 0.1) is False

def test_is_probable_match_accepts_custom_lower_threshold():

    result = is_probable_match("ABC Corporation", "ABC Corp", threshold=70)

    assert result is True

def test_is_probable_match_rejects_custom_higher_threshold():

    result = is_probable_match("ABC Corporation", "ABC Corp", threshold=100)

    assert result is False

@pytest.mark.parametrize("threshold", [-1, 100.1, 101])

def test_is_probable_match_rejects_invalid_threshold(threshold):

    with pytest.raises(ValueError, match="Similarity threshold must be between 0 and 100"):

        is_probable_match("ABC Corporation", "ABC Corporation", threshold=threshold)

def test_fuzzy_match_returns_score_threshold_and_decision():

    result = fuzzy_match("ABC Corporation", "ABC Corporation")

    assert result["score"] == 100.0
    assert result["threshold"] == 90.0
    assert result["matched"] is True

def test_fuzzy_match_respects_custom_threshold():

    result = fuzzy_match("ABC Corporation", "ABC Corp", threshold=70)

    assert result["score"] >= 70.0
    assert result["threshold"] == 70.0
    assert result["matched"] is True

def test_fuzzy_match_exposes_failed_threshold_decision():

    result = fuzzy_match("ABC Corporation", "XYZ Industries", threshold=90)

    assert result["score"] < 90.0
    assert result["threshold"] == 90.0
    assert result["matched"] is False

def test_fuzzy_match_rejects_invalid_threshold():

    with pytest.raises(ValueError, match="Similarity threshold must be between 0 and 100"):
        
        fuzzy_match("ABC Corporation", "ABC Corporation", threshold=101)


def test_fuzzy_matching_is_secondary_to_transaction_id_reconciliation():

    result = fuzzy_match("Product description A", "Product description A")

    assert result["matched"] is True
    assert result["score"] == 100.0