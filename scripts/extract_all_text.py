"""Extract text from all 75 PDFs and save to data/interim/text/.

Also prints a summary of how many PDFs have a usable text layer vs. appear
to be scanned (no extractable text).

Usage:
    uv run python scripts/extract_all_text.py
"""

from pathlib import Path

from invoice_review.extraction.text import extract_text

PDF_DIR = Path("data/raw/fcc/pdfs")
OUT_DIR = Path("data/interim/text")
MIN_TEXT_CHARS = 50  # fewer than this → treat as scanned


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pdfs = sorted(PDF_DIR.glob("*.pdf"))
    assert pdfs, f"No PDFs found in {PDF_DIR}"

    has_text, scanned = [], []
    for pdf in pdfs:
        text = extract_text(pdf)
        out_path = OUT_DIR / (pdf.stem + ".txt")
        out_path.write_text(text, encoding="utf-8")

        if len(text.strip()) >= MIN_TEXT_CHARS:
            has_text.append(pdf.name)
        else:
            scanned.append(pdf.name)

    print(f"Extracted text for {len(pdfs)} PDFs → {OUT_DIR}")
    print(f"  Text layer (≥{MIN_TEXT_CHARS} chars): {len(has_text)}")
    print(f"  Likely scanned (<{MIN_TEXT_CHARS} chars): {len(scanned)}")
    if scanned:
        print("\nScanned / empty:")
        for name in scanned:
            print(f"  {name}")


if __name__ == "__main__":
    main()
