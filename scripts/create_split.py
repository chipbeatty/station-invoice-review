"""Create the dev/test split and write manifest/split.json.

Dev set: 20 invoices — 7 pre-viewed invoices forced in, 13 drawn randomly.
Test set: 55 invoices.

Run once, before reading any invoice:
    uv run python scripts/create_split.py
"""

import json
import random
from pathlib import Path

SEED = 42
DEV_SIZE = 20
PDF_DIR = Path("data/raw/fcc/pdfs")
VIEWED_FILE = Path("docs/viewed_before_split.txt")
MANIFEST_FILE = Path("manifest/split.json")


def main() -> None:
    all_pdfs = sorted(p.name for p in PDF_DIR.glob("*.pdf"))
    assert len(all_pdfs) == 75, f"Expected 75 PDFs, found {len(all_pdfs)}"

    viewed = [line.strip() for line in VIEWED_FILE.read_text().splitlines() if line.strip()]
    assert all(v in all_pdfs for v in viewed), "viewed_before_split.txt references unknown PDF"
    assert len(viewed) <= DEV_SIZE, f"More pre-viewed files ({len(viewed)}) than dev slots ({DEV_SIZE})"

    remaining = [p for p in all_pdfs if p not in viewed]
    rng = random.Random(SEED)
    extra_dev = rng.sample(remaining, DEV_SIZE - len(viewed))

    dev = sorted(viewed + extra_dev)
    test = sorted(p for p in all_pdfs if p not in dev)

    assert len(dev) == DEV_SIZE
    assert len(test) == 55
    assert not set(dev) & set(test), "dev and test overlap"

    MANIFEST_FILE.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_FILE.write_text(json.dumps({"seed": SEED, "dev": dev, "test": test}, indent=2) + "\n")
    print(f"Split written to {MANIFEST_FILE}: {len(dev)} dev, {len(test)} test.")
    print(f"  Pre-viewed forced into dev: {len(viewed)}")
    print(f"  Randomly sampled into dev:  {len(extra_dev)}")


if __name__ == "__main__":
    main()
