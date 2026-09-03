#!/usr/bin/env python3
"""Run pre-official-evaluation sensitivity checks for the Stage-02 link model."""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("link_model", HERE / "link_model.py")
lm = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(lm)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--config", type=Path, default=HERE / "link_model_config.json")
    p.add_argument("--ber-lut", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--manifest", type=Path, required=True)
    args = p.parse_args()
    cfg = json.loads(args.config.read_text())
    lut = lm.BerLut.from_csv(args.ber_lut)
    model = lm.LinkModel.from_dict(cfg, lut)

    ranges = [10, 25, 50, 75, 100, 150, 200]
    bearings_deg = [0, 1, 2, 5, 10, 15, 20]
    rows = []
    for r in ranges:
        for b in bearings_deg:
            state = model.evaluate(range_m=float(r), pointing_error_rad=np.deg2rad(b))
            rows.append({
                "range_m": r, "pointing_error_deg": b,
                "snr_db": state.snr_db, "ber": state.ber, "per": state.per,
                "goodput_bps": state.goodput_bps, "outage": int(state.outage),
            })
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)

    # Frozen monotonicity checks along boresight and at fixed range.
    boresight = [x for x in rows if x["pointing_error_deg"] == 0]
    fixed_range = [x for x in rows if x["range_m"] == 50]
    checks = {
        "snr_nonincreasing_with_range": all(a["snr_db"] >= b["snr_db"] for a,b in zip(boresight, boresight[1:])),
        "snr_nonincreasing_with_pointing_error": all(a["snr_db"] >= b["snr_db"] for a,b in zip(fixed_range, fixed_range[1:])),
        "ber_in_unit_interval": all(0 <= x["ber"] <= 1 for x in rows),
        "per_in_unit_interval": all(0 <= x["per"] <= 1 for x in rows),
        "goodput_nonnegative": all(x["goodput_bps"] >= 0 for x in rows),
    }
    manifest = {
        "artifact": str(args.output), "artifact_sha256": sha256(args.output),
        "link_config": str(args.config), "link_config_sha256": sha256(args.config),
        "ber_lut": str(args.ber_lut), "ber_lut_sha256": sha256(args.ber_lut),
        "grid": {"range_m": ranges, "pointing_error_deg": bearings_deg},
        "checks": checks, "passed": all(checks.values()),
        "claim_boundary": "Sensitivity analysis of a model-based communication layer driven by real WOMD geometry; not measured WOMD communication data.",
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0 if manifest["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
