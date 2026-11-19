import csv
import io
from pathlib import Path
from docx import Document as DocxDocument
from pypdf import PdfReader

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md", ".csv"}

def extract_document(filename: str, content: bytes) -> list[dict]:
    """Return ordered text segments with optional page numbers."""
    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type '{suffix}'. Supported: PDF, DOCX, TXT, MD, CSV.")
    if not content:
        raise ValueError("The uploaded file is empty.")

    if suffix == ".pdf":
        reader = PdfReader(io.BytesIO(content))
        segments = [
            {"text": (page.extract_text() or "").strip(), "page_number": index + 1}
            for index, page in enumerate(reader.pages)
        ]
    elif suffix == ".docx":
        doc = DocxDocument(io.BytesIO(content))
        lines = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        for table in doc.tables:
            for row in table.rows:
                lines.append(" | ".join(cell.text.strip() for cell in row.cells))
        segments = [{"text": "\n".join(lines), "page_number": None}]
    elif suffix == ".csv":
        decoded = content.decode("utf-8-sig")
        rows = list(csv.reader(io.StringIO(decoded)))
        segments = [{"text": "\n".join(" | ".join(cell for cell in row) for row in rows),
                     "page_number": None}]
    else:
        text = content.decode("utf-8-sig")
        segments = [{"text": text.strip(), "page_number": None}]

    segments = [segment for segment in segments if segment["text"]]
    if not segments:
        raise ValueError("No extractable text was found. Scanned PDFs may require OCR, which is not included yet.")
    return segments
