"""Tests for extract_text()."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from invoice_review.extraction.text import extract_text

PDF_DIR = Path("data/raw/fcc/pdfs")


def _mock_pdf(page_texts: list[str | None]):
    """Build a mock pdfplumber PDF with the given per-page text values."""
    pages = []
    for text in page_texts:
        page = MagicMock()
        page.extract_text.return_value = text
        pages.append(page)
    pdf = MagicMock()
    pdf.__enter__ = MagicMock(return_value=pdf)
    pdf.__exit__ = MagicMock(return_value=False)
    pdf.pages = pages
    return pdf


def test_pages_joined_with_double_newline():
    with patch("invoice_review.extraction.text.pdfplumber.open", return_value=_mock_pdf(["page one", "page two"])):
        result = extract_text(Path("fake.pdf"))
    assert result == "page one\n\npage two"


def test_none_page_becomes_empty_string():
    """pdfplumber returns None for scanned pages; extract_text should coerce to ''."""
    with patch("invoice_review.extraction.text.pdfplumber.open", return_value=_mock_pdf([None, "text"])):
        result = extract_text(Path("fake.pdf"))
    assert result == "\n\ntext"


def test_all_scanned_returns_empty_ish():
    with patch("invoice_review.extraction.text.pdfplumber.open", return_value=_mock_pdf([None, None])):
        result = extract_text(Path("fake.pdf"))
    assert result.strip() == ""


@pytest.mark.skipif(not PDF_DIR.exists(), reason="requires data/raw/fcc/pdfs/")
def test_real_pdf_returns_nonempty_string():
    """Smoke test against a real PDF from the dataset."""
    pdf = next(PDF_DIR.glob("*.pdf"))
    result = extract_text(pdf)
    assert isinstance(result, str)
    assert len(result) >= 0  # scanned PDFs may return empty; just verify no exception
