"""Reads the text out of an uploaded PDF resume, in memory. Nothing is stored."""
import re
from io import BytesIO

from pypdf import PdfReader

MAX_BYTES = 2 * 1024 * 1024
MAX_PAGES = 10
MAX_CHARS = 20000


class PdfExtractionError(Exception):
    """Raised when a PDF cannot be turned into text. Carries the HTTP status to answer with."""

    def __init__(self, message: str, status_code: int = 422):
        super().__init__(message)
        self.status_code = status_code


def _tidy(text: str) -> str:
    lines = [line.strip() for line in text.replace("\r", "\n").split("\n")]
    cleaned = "\n".join(lines)
    return re.sub(r"\n{3,}", "\n\n", cleaned).strip()


def extract_text_from_pdf(data: bytes) -> dict:
    if not data:
        raise PdfExtractionError("The file is empty.")
    if len(data) > MAX_BYTES:
        raise PdfExtractionError("That PDF is larger than 2 MB. Export a smaller one or paste the text.", 413)
    if not data.startswith(b"%PDF-"):
        raise PdfExtractionError("That file is not a PDF.")

    try:
        reader = PdfReader(BytesIO(data))
        if reader.is_encrypted:
            raise PdfExtractionError("This PDF is password-protected. Remove the password or paste the text.")
        total_pages = len(reader.pages)
        parts = [(page.extract_text() or "") for page in reader.pages[:MAX_PAGES]]
    except PdfExtractionError:
        raise
    except Exception:
        raise PdfExtractionError("Could not read this PDF. It may be damaged. Paste the text instead.")

    text = _tidy("\n".join(parts))
    if not text:
        raise PdfExtractionError(
            "No text was found. This looks like a scanned or image-only PDF. Paste the text instead."
        )

    truncated = total_pages > MAX_PAGES or len(text) > MAX_CHARS
    text = text[:MAX_CHARS]
    return {"text": text, "pages": total_pages, "chars": len(text), "truncated": truncated}