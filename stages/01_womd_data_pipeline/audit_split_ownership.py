#!/usr/bin/env python3
"""Verify scenario-level ownership across canonical Stage-01 corpora."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def load_ownership(path: Path) -> dict[str, set[str]]:
    with np.load(path, allow_pickle=False) as data:
        scenarios = [str(x) for x in data["scenario_id"].tolist()]
        splits = [str(x) for x in data["split"].tolist()]
    ownership: dict[str, set[str]] = {}
    for scenario, split in zip(scenarios, splits, strict=True):
        ownership.setdefault(split, set()).add(scenario)
    return ownership


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("training_npz", type=Path)
    p.add_argument("official_validation_npz", type=Path)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    a = load_ownership(args.training_npz)
    b = load_ownership(args.official_validation_npz)
    train = a.get("training", set())
    dev = a.get("development", set())
    official = b.get("official_validation", set())
    overlaps = {
        "training_development": sorted(train & dev),
        "training_official_validation": sorted(train & official),
        "development_official_validation": sorted(dev & official),
    }
    errors = []
    if set(a) - {"training", "development"}:
        errors.append(f"training corpus has unexpected splits: {sorted(set(a))}")
    if set(b) != {"official_validation"}:
        errors.append(f"official corpus split labels are {sorted(set(b))}")
    if any(overlaps.values()):
        errors.append("scenario leakage detected across split ownership")
    report = {
        "scenario_counts": {
            "training": len(train),
            "development": len(dev),
            "official_validation": len(official),
        },
        "overlap_counts": {k: len(v) for k, v in overlaps.items()},
        "overlaps": overlaps,
        "passed": not errors,
        "errors": errors,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
