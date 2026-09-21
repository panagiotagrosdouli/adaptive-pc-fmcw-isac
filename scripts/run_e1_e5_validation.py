#!/usr/bin/env python3
"""Run executable E1-E5 publication validation and write JSON evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from pcfmcw_isac.publication_validation import run_e1_e5


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default="artifacts/publication/e1_e5_validation.json",
        help="JSON output path",
    )
    args = parser.parse_args()

    result = run_e1_e5()
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(path)


if __name__ == "__main__":
    main()
