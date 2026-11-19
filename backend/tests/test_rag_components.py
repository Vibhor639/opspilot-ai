import pytest
from app.services.chunking import chunk_segments
from app.services.document_parser import extract_document
from app.services.retrieval import lexical_score, hybrid_rerank

def test_chunking_preserves_page_and_overlap():
    segments = [{"text":" ".join(f"word{i}" for i in range(50)), "page_number":2}]
    chunks = chunk_segments(segments, chunk_size=25, overlap=5)
    assert len(chunks) == 3
    assert chunks[0]["page_number"] == 2
    assert chunks[0]["end_word"] - chunks[1]["start_word"] == 5

def test_text_extraction():
    segments = extract_document("notes.txt", b"CPU troubleshooting steps")
    assert segments[0]["text"] == "CPU troubleshooting steps"

def test_unsupported_file():
    with pytest.raises(ValueError):
        extract_document("malware.exe", b"content")

def test_lexical_score():
    assert lexical_score("high CPU alert", "high CPU utilization alert") == 1.0

def test_hybrid_rerank_prefers_relevant_text():
    candidates = [
        {"text":"database backup and recovery", "dense_score":0.9},
        {"text":"high CPU utilization on EC2 instance", "dense_score":0.7},
    ]
    ranked = hybrid_rerank("high CPU EC2", candidates)
    assert ranked[0]["text"].startswith("high CPU")
