#!/usr/bin/env python3
"""Fail-closed audit for the canonical Stage-01 WOMD NPZ contract."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np

REQUIRED = {
    "history_xy": (3, (11, 2)), "history_vxy": (3, (11, 2)),
    "future_xy": (3, (80, 2)), "future_relative_xy": (3, (80, 2)),
    "sdc_future_xy": (3, (80, 2)), "history_valid": (2, (11,)),
    "future_valid": (2, (80,)), "scenario_id": (1, ()),
    "track_id": (1, ()), "sdc_track_id": (1, ()), "split": (1, ())}
NUMERIC = ("history_xy", "history_vxy", "future_xy", "future_relative_xy", "sdc_future_xy")

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""): h.update(chunk)
    return h.hexdigest()

def audit(path: Path, expected_split: str | None = None) -> dict:
    errors = []
    with np.load(path, allow_pickle=False) as data:
        missing = sorted(set(REQUIRED) - set(data.files))
        if missing: errors.append(f"missing required arrays: {missing}")
        a = {k: data[k] for k in REQUIRED if k in data}
        ns = {v.shape[0] for v in a.values() if v.ndim >= 1}
        if len(ns) != 1: errors.append(f"inconsistent sample dimension: {sorted(ns)}")
        n = next(iter(ns)) if len(ns) == 1 else None
        for k, (ndim, tail) in REQUIRED.items():
            if k not in a: continue
            if a[k].ndim != ndim: errors.append(f"{k}: expected ndim={ndim}, got {a[k].ndim}")
            elif tail and a[k].shape[1:] != tail: errors.append(f"{k}: expected tail {tail}, got {a[k].shape[1:]}")
        for k in NUMERIC:
            if k in a and not np.isfinite(a[k]).all(): errors.append(f"{k}: contains NaN or Inf")
        for k in ("history_valid", "future_valid"):
            if k in a and not set(np.unique(a[k]).tolist()).issubset({0, 1, False, True}): errors.append(f"{k}: invalid mask")
        if all(k in a for k in ("future_xy", "sdc_future_xy", "future_relative_xy")):
            if not np.allclose(a["future_xy"] - a["sdc_future_xy"], a["future_relative_xy"], rtol=1e-5, atol=1e-4):
                errors.append("future_relative_xy violates actor-minus-SDC geometry identity")
        sids = {str(x) for x in a.get("scenario_id", np.array([])).tolist()}
        splits = {str(x) for x in a.get("split", np.array([])).tolist()}
        if not sids or any(not x.strip() for x in sids): errors.append("scenario_id is empty or invalid")
        if expected_split is not None and splits != {expected_split}: errors.append(f"expected split={expected_split!r}, observed={sorted(splits)}")
    return {"schema": "womd_predictive_connectivity_npz_v2", "path": str(path), "sha256": sha256(path), "sample_count": n, "scenario_count": len(sids), "splits": sorted(splits), "passed": not errors, "errors": errors}

def main() -> int:
    p = argparse.ArgumentParser(); p.add_argument("npz", type=Path); p.add_argument("--expected-split"); p.add_argument("--output", type=Path, required=True); args = p.parse_args()
    report = audit(args.npz, args.expected_split); args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n"); print(json.dumps(report, indent=2, sort_keys=True)); return 0 if report["passed"] else 2
if __name__ == "__main__": raise SystemExit(main())
