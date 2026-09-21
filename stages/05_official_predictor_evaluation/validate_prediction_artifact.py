#!/usr/bin/env python3
"""Validate a Stage-05 prediction artifact without modifying it.

This validator checks the structural/provenance contract only. It deliberately
cannot turn missing official WOMD or checkpoint artifacts into publication
 evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

REQUIRED = {
    "scenario_id": (1, ()),
    "track_id": (1, ()),
    "sdc_track_id": (1, ()),
    "predicted_xy": (3, (80, 2)),
    "prediction_valid": (2, (80,)),
}
PROVENANCE = ("checkpoint_sha256", "preprocessing_sha256", "input_corpus_sha256")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def validate(path: Path) -> dict:
    errors: list[str] = []
    with np.load(path, allow_pickle=False) as data:
        missing = sorted(set(REQUIRED) - set(data.files))
        if missing:
            errors.append(f"missing required arrays: {missing}")
        arrays = {k: data[k] for k in REQUIRED if k in data.files}
        sizes = {a.shape[0] for a in arrays.values() if a.ndim >= 1}
        n = next(iter(sizes)) if len(sizes) == 1 else None
        if len(sizes) != 1:
            errors.append(f"inconsistent sample dimension: {sorted(sizes)}")
        for key, (ndim, tail) in REQUIRED.items():
            if key not in arrays:
                continue
            a = arrays[key]
            if a.ndim != ndim:
                errors.append(f"{key}: expected ndim={ndim}, got {a.ndim}")
            elif tail and a.shape[1:] != tail:
                errors.append(f"{key}: expected tail shape {tail}, got {a.shape[1:]}")
        if "predicted_xy" in arrays and not np.isfinite(arrays["predicted_xy"]).all():
            errors.append("predicted_xy contains NaN or Inf")
        if "prediction_valid" in arrays:
            values = set(np.unique(arrays["prediction_valid"]).tolist())
            if not values.issubset({0, 1, False, True}):
                errors.append("prediction_valid must contain only boolean/0-1 values")
        for key in PROVENANCE:
            if key not in data.files:
                errors.append(f"missing provenance field: {key}")
            elif not str(data[key]).strip():
                errors.append(f"empty provenance field: {key}")
        scenarios = {str(x) for x in arrays["scenario_id"].tolist()} if "scenario_id" in arrays else set()
        tracks = {str(x) for x in arrays["track_id"].tolist()} if "track_id" in arrays else set()
        if not scenarios:
            errors.append("scenario_id is empty")
        if not tracks:
            errors.append("track_id is empty")
        return {
            "schema": "stage05_prediction_artifact_v1",
            "path": str(path),
            "sha256": sha256(path),
            "sample_count": n,
            "scenario_count": len(scenarios),
            "track_count": len(tracks),
            "arrays": {k: {"shape": list(v.shape), "dtype": str(v.dtype)} for k, v in arrays.items()},
            "passed": not errors,
            "errors": errors,
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = validate(args.artifact)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
