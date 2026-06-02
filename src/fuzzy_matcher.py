from rapidfuzz import fuzz

def calculate_similarity(name_1, name_2):

    score = fuzz.ratio(name_1, name_2)

    return score

def is_probable_match(name_1, name_2):

    score = calculate_similarity(name_1, name_2)

    return score >= 90