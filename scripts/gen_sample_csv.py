#!/usr/bin/env python3
"""
Generate a sample CSV with 7-digit IDs and heights in [0, 5] cm.

Usage:
  python scripts/gen_sample_csv.py --out sample_data/jobs_20.csv --rows 20

Options:
  --out PATH     Output CSV path (default: sample_data/jobs_20.csv)
  --rows N       Number of rows (default: 20)
  --start-id N   Starting 7-digit ID (default: 1000001)
  --random       Randomize heights (default: evenly spaced)
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
import random


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="sample_data/jobs_20.csv")
    ap.add_argument("--rows", type=int, default=20)
    ap.add_argument("--start-id", type=int, default=1_000_001)
    ap.add_argument("--random", action="store_true")
    args = ap.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    if args.random:
        for i in range(args.rows):
            rid = args.start_id + i
            h = round(random.uniform(0, 5), 2)
            rows.append((rid, h, "not carved"))
    else:
        # evenly spaced 0..5
        if args.rows == 1:
            heights = [0.0]
        else:
            heights = [round(5.0 * i / (args.rows - 1), 2) for i in range(args.rows)]
        for i, h in enumerate(heights, start=0):
            rid = args.start_id + i
            rows.append((rid, h, "not carved"))

    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ID number", "height", "status"])
        for rid, h, s in rows:
            w.writerow([str(rid), f"{h:.2f}", s])

    print(f"Wrote {len(rows)} rows to {out_path}")


if __name__ == "__main__":
    main()

