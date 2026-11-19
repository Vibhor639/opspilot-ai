import pytest

from app.services.chunking import chunk_segments


def test_chunks_preserve_page_metadata_and_word_offsets():
    segments = [{
        "text": "First sentence has five words. Second sentence has four.",
        "page_number": 3,
    }]

    chunks = chunk_segments(segments, chunk_size=20, overlap=3)

    assert len(chunks) == 1
    assert chunks[0]["page_number"] == 3
    assert chunks[0]["start_word"] == 0
    assert chunks[0]["end_word"] == 9
    assert chunks[0]["text"].startswith("First sentence")


def test_chunks_never_exceed_configured_size():
    text = " ".join(f"word{i}" for i in range(250)) + "."

    chunks = chunk_segments(
        [{"text": text, "page_number": 1}],
        chunk_size=40,
        overlap=8,
    )

    assert len(chunks) > 1
    assert all(len(chunk["text"].split()) <= 40 for chunk in chunks)


def test_long_sentence_uses_overlapping_windows():
    text = " ".join(f"token{i}" for i in range(95)) + "."

    chunks = chunk_segments(
        [{"text": text}],
        chunk_size=30,
        overlap=5,
    )

    assert len(chunks) > 1
    assert all(len(chunk["text"].split()) <= 30 for chunk in chunks)
    assert chunks[0]["end_word"] - chunks[1]["start_word"] == 5


def test_sentence_boundaries_are_preferred():
    text = (
        "First sentence has six words here. "
        "Second sentence has six words here. "
        "Third sentence has six words here."
    )

    chunks = chunk_segments(
        [{"text": text}],
        chunk_size=20,
        overlap=2,
    )

    assert len(chunks) == 1
    assert chunks[0]["text"].endswith("here.")
    assert chunks[0]["start_word"] == 0
    assert chunks[0]["end_word"] == 18


def test_empty_segments_are_ignored():
    assert chunk_segments([
        {"text": ""},
        {"text": "   "},
    ]) == []


def test_invalid_chunk_configuration_is_rejected():
    with pytest.raises(ValueError):
        chunk_segments([{"text": "Some text."}], chunk_size=10)

    with pytest.raises(ValueError):
        chunk_segments([{"text": "Some text."}], chunk_size=20, overlap=20)
