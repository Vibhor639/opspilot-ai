import re

def tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9_]+", text.lower()))

def lexical_score(query: str, text: str) -> float:
    query_terms = tokenize(query)
    if not query_terms:
        return 0.0
    text_terms = tokenize(text)
    return len(query_terms & text_terms) / len(query_terms)

def hybrid_rerank(query: str, candidates: list[dict]) -> list[dict]:
    """Combine vector similarity and lexical coverage, then sort transparently."""
    ranked = []
    for item in candidates:
        dense = max(0.0, min(1.0, float(item.get("dense_score", 0.0))))
        lexical = lexical_score(query, item.get("text", ""))
        phrase_bonus = 0.05 if query.lower().strip() in item.get("text", "").lower() else 0.0
        combined = 0.70 * dense + 0.30 * lexical + phrase_bonus
        ranked.append({**item, "lexical_score": round(lexical, 4),
                       "score": round(min(combined, 1.0), 4)})
    return sorted(ranked, key=lambda item: item["score"], reverse=True)
