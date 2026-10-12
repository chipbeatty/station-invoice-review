"""Download a small subset of clean FCC invoices from amazon/ConfBench.

Fetches only the original (non-degraded) PDFs plus the small ground-truth
parquet file, then writes one JSON label file per downloaded invoice.
PDFs already present in <out>/pdfs/ are skipped, so this also works to fetch
just the labels for invoices you downloaded another way.

Usage (from the repo root):
    uv run python scripts/download_fcc_subset.py            # 10 invoices
    uv run python scripts/download_fcc_subset.py -n 75      # all clean originals

Output (default --out data/raw/fcc):
    pdfs/<id>__original.pdf     invoice PDFs
    labels/<id>__original.json  ground truth for each PDF
    data/*.parquet              the dataset's full ground-truth table
"""

import argparse
import json
from pathlib import Path

import pandas as pd
from huggingface_hub import hf_hub_download, list_repo_files

REPO_ID = "amazon/ConfBench"
GROUND_TRUTH_FILE = "data/test-00000-of-00001.parquet"


def to_jsonable(obj):
    """Convert numpy arrays/scalars from parquet into plain Python for json.dump."""
    if hasattr(obj, "tolist"):
        return obj.tolist()
    return str(obj)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-n", type=int, default=10, help="number of invoices to download")
    parser.add_argument("--out", default="data/raw/fcc", help="output folder")
    args = parser.parse_args()
    out = Path(args.out)

    # 1. List files in the repo (no download) and keep only clean originals.
    all_files = list_repo_files(REPO_ID, repo_type="dataset")
    originals = sorted(
        f for f in all_files if f.startswith("pdfs/") and f.endswith("__original.pdf")
    )
    print(f"Found {len(originals)} clean originals; downloading {min(args.n, len(originals))}.")
    subset = originals[: args.n]  # IDs are hashes, so sorted order is effectively random

    # 2. Download just those PDFs, skipping any already on disk.
    for i, filename in enumerate(subset, 1):
        if (out / filename).exists():
            print(f"  [{i}/{len(subset)}] {Path(filename).name} (already present, skipped)")
            continue
        hf_hub_download(REPO_ID, filename, repo_type="dataset", local_dir=out)
        print(f"  [{i}/{len(subset)}] {Path(filename).name}")

    # 3. Download the ground-truth parquet (small: metadata only, no PDFs).
    gt_path = hf_hub_download(REPO_ID, GROUND_TRUTH_FILE, repo_type="dataset", local_dir=out)
    df = pd.read_parquet(gt_path)

    # 4. Write one label JSON per downloaded invoice.
    wanted = {Path(f).name for f in subset}
    labels_dir = out / "labels"
    labels_dir.mkdir(parents=True, exist_ok=True)
    rows = df[df["id"].isin(wanted)]
    for _, row in rows.iterrows():
        label_file = labels_dir / row["id"].replace(".pdf", ".json")
        with open(label_file, "w") as f:
            json.dump(row["json_response"], f, indent=2, default=to_jsonable)

    print(f"\nDone. PDFs in {out / 'pdfs'}, labels in {labels_dir} ({len(rows)} files).")


if __name__ == "__main__":
    main()
