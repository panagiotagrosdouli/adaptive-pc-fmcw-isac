#!/usr/bin/env python3
"""Run the publication-v2.1 mandatory smoke gate and write JSON evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from pcfmcw_isac.publication_benchmark_v2_1 import run_v2_1_smoke


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default="artifacts/publication/v2_1_smoke.json",
        help="Output JSON path",
    )
    args = parser.parse_args()
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    bundle = run_v2_1_smoke()
    out.write_text(json.dumps(bundle, indent=2, sort_keys=True))
    print(json.dumps({"output": str(out), "sanity_gate": bundle["sanity_gate"]}, indent=2))


if __name__ == "__main__":
    main()
