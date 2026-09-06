"""Command-line interface."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from .pipeline import map_inventory


def main() -> None:
    parser = argparse.ArgumentParser(description="Map BAS points to scheduled HVAC equipment")
    parser.add_argument("--points", type=Path, required=True)
    parser.add_argument("--schedule", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    points = pd.read_csv(args.points)
    schedule = pd.read_csv(args.schedule)
    mapped, metrics = map_inventory(points, schedule)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    mapped.to_csv(args.output_dir / "mapping_results.csv", index=False)
    (args.output_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
