#!/usr/bin/env python3
"""Run the frozen publication-v2 smoke benchmark and write machine-readable JSON."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from pcfmcw_isac.publication_benchmark_v2 import run_v2_smoke


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default="artifacts/publication_v2/v2_smoke.json",
        help="Output JSON path",
    )
    args = parser.parse_args()
    payload = run_v2_smoke()
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
