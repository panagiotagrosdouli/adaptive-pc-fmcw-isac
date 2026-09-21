#!/usr/bin/env python3
"""Confidence-qualify frozen v2.1 E9 feasible-region cells without rerunning them.

The frozen E9 artifact stores per-cell empirical unconditional joint-QoS
probabilities but not explicit success counts. The frozen generator used exactly
20 seeds per cell. This postprocessor requires the trial count as an explicit
argument, reconstructs only integer counts that are exactly supported by the
stored probabilities, and adds one-sided Wilson lower bounds. It never modifies
the frozen input artifact.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from pcfmcw_isac.statistics import wilson_lower_bound


EXPECTED_EVIDENCE_CLASS = "FROZEN_PUBLICATION_V2_1_E9_E11_SIMULATION_NOT_HARDWARE_MEASUREMENT"
EXPECTED_PROTOCOL = "pcfmcw_isac_paper_v2_1"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--trials-per-cell", type=int, required=True)
    p.add_argument("--target", type=float, default=0.95)
    p.add_argument("--confidence", type=float, default=0.95)
    return p.parse_args()


def _count_from_probability(probability: float, trials: int, *, tolerance: float = 1e-10) -> int:
    raw = float(probability) * trials
    rounded = int(round(raw))
    if abs(raw - rounded) > tolerance:
        raise ValueError(
            f"stored probability {probability!r} is incompatible with integer count over {trials} trials"
        )
    if rounded < 0 or rounded > trials:
        raise ValueError("reconstructed count lies outside [0, trials]")
    return rounded


def qualify_e9(payload: dict, *, trials_per_cell: int, target: float = 0.95, confidence: float = 0.95) -> dict:
    if trials_per_cell <= 0:
        raise ValueError("trials_per_cell must be positive")
    if not 0.0 < target < 1.0:
        raise ValueError("target must lie in (0,1)")
    if payload.get("evidence_class") != EXPECTED_EVIDENCE_CLASS:
        raise ValueError("unexpected frozen E9/E11 evidence class")
    if payload.get("protocol_id") != EXPECTED_PROTOCOL:
        raise ValueError("unexpected frozen protocol id")
    if "e9" not in payload or not isinstance(payload["e9"], dict):
        raise ValueError("missing E9 slices")

    max_possible_lower = wilson_lower_bound(trials_per_cell, trials_per_cell, confidence=confidence)
    slices = {}
    total_cells = 0
    raw_target_cells = 0
    confidence_qualified_cells = 0

    for slice_name, source in payload["e9"].items():
        cells = []
        for cell in source.get("cells", []):
            successes = _count_from_probability(cell["joint_qos_probability"], trials_per_cell)
            selections = _count_from_probability(cell["selection_rate"], trials_per_cell)
            lower = wilson_lower_bound(successes, trials_per_cell, confidence=confidence)
            raw_meets = bool(cell.get("empirically_meets_declared_target", False))
            qualified = bool(lower >= target)
            cells.append({
                **cell,
                "trials": trials_per_cell,
                "joint_qos_successes_reconstructed": successes,
                "selections_reconstructed": selections,
                "wilson_lower": lower,
                "confidence": confidence,
                "target": target,
                "confidence_qualified_meets_target": qualified,
            })
            total_cells += 1
            raw_target_cells += int(raw_meets)
            confidence_qualified_cells += int(qualified)
        slices[slice_name] = {
            "axis_x": source.get("axis_x"),
            "axis_y": source.get("axis_y"),
            "policy": source.get("policy"),
            "cells": cells,
            "n_cells": len(cells),
            "raw_empirical_target_cells": sum(bool(c.get("empirically_meets_declared_target", False)) for c in cells),
            "confidence_qualified_target_cells": sum(bool(c["confidence_qualified_meets_target"]) for c in cells),
        }

    return {
        "evidence_class": "POSTPROCESSED_FROZEN_PUBLICATION_V2_1_E9_CONFIDENCE_NOT_HARDWARE_MEASUREMENT",
        "source_evidence_class": payload["evidence_class"],
        "protocol_id": payload["protocol_id"],
        "trials_per_cell": trials_per_cell,
        "target": target,
        "confidence": confidence,
        "max_possible_wilson_lower_at_trials_per_cell": max_possible_lower,
        "target_statistically_attainable_at_trials_per_cell": bool(max_possible_lower >= target),
        "total_cells": total_cells,
        "raw_empirical_target_cells": raw_target_cells,
        "confidence_qualified_target_cells": confidence_qualified_cells,
        "slices": slices,
        "claim_boundary": (
            "Postprocessing of frozen empirical cell probabilities only. Reconstructed counts are valid only because the frozen generator "
            "used the declared common trial count per cell. This does not create new receiver simulations or hardware evidence."
        ),
    }


def main() -> None:
    args = parse_args()
    payload = json.loads(Path(args.input).read_text())
    result = qualify_e9(
        payload,
        trials_per_cell=args.trials_per_cell,
        target=args.target,
        confidence=args.confidence,
    )
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, allow_nan=False))
    print(out)


if __name__ == "__main__":
    main()
