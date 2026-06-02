from fuzzy_matcher import (calculate_similarity, is_probable_match)

name_1 = "abhiram tk"
name_2 = "vivek nair"

score = calculate_similarity(name_1, name_2)

print(f"Similarity Score: {score}")

if is_probable_match(name_1, name_2):

    print("Probable Match")

else:

    print("Mismatch")