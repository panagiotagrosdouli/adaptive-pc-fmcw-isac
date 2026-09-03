#!/usr/bin/env python3
"""Audit a Stage-01 canonical WOMD NPZ corpus without modifying it."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

REQUIRED = {
    "history_xy": (3, (11, 2)),
    "history_vxy": (3, (11, 2)),
    "future_xy": (3, (80, 2)),
    "history_valid": (2, (11,)),
    "future_valid": (2, (80,)),
    "scenario_id": (1, ()),
    "track_id": (1, ()),
    "sdc_track_id": (1, ()),
    "split": (1, ()),
}
NUMERIC_KEYS = ("history_xy", "history_vxy", "future_xy")
VALID_KEYS = ("history_valid", "future_valid")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def strings(a: np.ndarray) -> set[str]:
    return {str(x) for x in a.tolist()}


def audit(path: Path, expected_split: str | None = None) -> dict:
    errors: list[str] = []
    with np.load(path, allow_pickle=False) as data:
        keys = set(data.files)
        missing = sorted(set(REQUIRED) - keys)
        if missing:
            errors.append(f"missing required arrays: {missing}")

        arrays = {k: data[k] for k in REQUIRED if k in data}
        n_values = {a.shape[0] for a in arrays.values() if a.ndim >= 1}
        n = next(iter(n_values)) if len(n_values) == 1 else None
        if len(n_values) != 1:
            errors.append(f"inconsistent sample dimension: {sorted(n_values)}")

        for key, (ndim, tail) in REQUIRED.items():
            if key not in arrays:
                continue
            a = arrays[key]
            if a.ndim != ndim:
                errors.append(f"{key}: expected ndim={ndim}, got {a.ndim}")
            elif tail and a.shape[1:] != tail:
                errors.append(f"{key}: expected tail shape {tail}, got {a.shape[1:]}")

        for key in NUMERIC_KEYS:
            if key in arrays and not np.isfinite(arrays[key]).all():
                errors.append(f"{key}: contains NaN or Inf")
        for key in VALID_KEYS:
            if key in arrays:
                unique = set(np.unique(arrays[key]).tolist())
                if not unique.issubset({0, 1, False, True}):
                    errors.append(f"{key}: validity mask is not boolean/0-1")

        scenario_ids = strings(arrays["scenario_id"]) if "scenario_id" in arrays else set()
        split_values = strings(arrays["split"]) if "split" in arrays else set()
        if not scenario_ids:
            errors.append("scenario_id is empty")
        if any(not sid.strip() for sid in scenario_ids):
            errors.append("scenario_id contains empty identity")
        if expected_split is not None and split_values != {expected_split}:
            errors.append(
                f"expected split={expected_split!r}, observed={sorted(split_values)}"
            )

        report = {
            "schema": "womd_predictive_connectivity_npz_v1",
            "path": str(path),
            "sha256": sha256(path),
            "sample_count": n,
            "scenario_count": len(scenario_ids),
            "splits": sorted(split_values),
            "arrays": {
                k: {"shape": list(v.shape), "dtype": str(v.dtype)}
                for k, v in arrays.items()
            },
            "finite_numeric_arrays": not any("NaN or Inf" in e for e in errors),
            "passed": not errors,
            "errors": errors,
        }
    return report


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("npz", type=Path)
    p.add_argument("--expected-split")
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    report = audit(args.npz, args.expected_split)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
