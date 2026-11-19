import re


def _split_sentences(text: str) -> list[str]:
    """Normalize whitespace and split text into sentence-like units."""
    text = re.sub(r"\s+", " ", text).strip()

    if not text:
        return []

    return [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", text)
        if sentence.strip()
    ]


def chunk_segments(
    segments: list[dict],
    chunk_size: int = 180,
    overlap: int = 35,
) -> list[dict]:
    """
    Build sentence-aware chunks with source metadata.

    Normal chunks do not overlap, avoiding mid-sentence passage starts.
    Long sentences are split into bounded overlapping windows.
    Word offsets refer to positions in the normalized segment.
    """
    if chunk_size < 20:
        raise ValueError("chunk_size must be at least 20 words.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "overlap must be non-negative and smaller than chunk_size."
        )

    output = []

    for segment in segments:
        original_text = segment.get("text", "")
        if not original_text or not original_text.strip():
            continue

        sentences = _split_sentences(original_text)
        current = []
        word_cursor = 0

        def emit(items):
            if not items:
                return

            output.append({
                "text": " ".join(word for word, _ in items),
                "page_number": segment.get("page_number"),
                "start_word": items[0][1],
                "end_word": items[-1][1] + 1,
            })

        for sentence in sentences:
            sentence_words = re.findall(r"\S+", sentence)

            indexed_words = [
                (word, word_cursor + index)
                for index, word in enumerate(sentence_words)
            ]
            word_cursor += len(sentence_words)

            if not indexed_words:
                continue

            # Split exceptionally long sentences into overlapping windows.
            if len(indexed_words) > chunk_size:
                emit(current)
                current = []

                step = chunk_size - overlap
                for start in range(0, len(indexed_words), step):
                    window = indexed_words[start:start + chunk_size]
                    emit(window)

                    if start + chunk_size >= len(indexed_words):
                        break

                continue

            # Keep complete sentences together whenever possible.
            if len(current) + len(indexed_words) <= chunk_size:
                current.extend(indexed_words)
            else:
                emit(current)
                current = list(indexed_words)

        emit(current)

    return output
