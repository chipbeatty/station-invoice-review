"""PDF text extraction using pdfplumber."""

from pathlib import Path

import pdfplumber


def extract_text(pdf_path: Path) -> str:
    """Extract all text from a PDF, joining pages with double newlines.

    Returns an empty string for pages with no text layer (scanned pages).
    The caller can detect a fully scanned document by checking whether the
    returned string is empty or very short.
    """
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            pages.append(page.extract_text() or "")
    return "\n\n".join(pages)
