UNKNOWN_RESPONSE = "This information is not found in the documents."


def is_unknown_answer(answer: str) -> bool:
    if not answer:
        return True

    normalized = answer.strip().lower()

    bad_answers = {
        "",
        "this information is not found in the documents.",
        "i don't know",
        "not sure",
        "cannot determine from the provided context",
    }

    return normalized in bad_answers


def has_relevant_results(results: list, min_final_score: float = 0.12) -> bool:
    if not results:
        return False

    best_doc = results[0]
    best_score = float(best_doc.metadata.get("final_score", 0.0))
    return best_score >= min_final_score
