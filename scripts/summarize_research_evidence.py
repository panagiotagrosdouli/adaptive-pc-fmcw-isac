#!/usr/bin/env python3
"""Derive a conservative machine-readable scientific verdict from research artifacts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from pcfmcw_isac.research_analysis import paired_bootstrap_binary_difference


B3 = "B3_DETERMINISTIC_JOINT"
B4 = "B4_ROBUST_JOINT"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--input-dir", default="artifacts/research")
    p.add_argument("--output", default="artifacts/research/scientific-verdict.json")
    p.add_argument("--bootstrap-resamples", type=int, default=10_000)
    return p.parse_args()


def _load(root: Path, name: str) -> dict:
    payload = json.loads((root / f"{name}.json").read_text())
    if "results" not in payload:
        raise ValueError(f"{name}: missing results envelope")
    return payload["results"]


def derive_verdict(root: Path, *, bootstrap_resamples: int = 10_000) -> dict:
    full = _load(root, "full-metrics")
    summary = full["summary"]
    b3 = summary[B3]
    b4 = summary[B4]
    paired = paired_bootstrap_binary_difference(
        full["records"],
        policy_a=B4,
        policy_b=B3,
        key_fields=("seed", "scenario_id"),
        metric="joint_qos",
        n_resamples=bootstrap_resamples,
        confidence=0.95,
        seed=20260912,
    )

    calibration = _load(root, "reliability-calibration")
    distribution = _load(root, "distribution-shift")
    pareto = _load(root, "pareto")
    runtime = _load(root, "runtime")
    uncertainty = _load(root, "uncertainty")

    b4_wilson = b4.get("wilson_lower_95_conditional")
    reliable_when_selected = bool(b4_wilson is not None and b4_wilson >= 0.95)
    availability_cost = bool(b4.get("selection_rate", 0.0) < b3.get("selection_rate", 0.0))
    unconditional_superiority_supported = bool(paired["ci_low"] > 0.0)
    unconditional_inferiority_supported = bool(paired["ci_high"] < 0.0)

    distribution_rows = {}
    for family, stats in distribution.get("paired_statistics", {}).items():
        distribution_rows[family] = {
            "b4_minus_b3_joint_qos": stats.get("mean_difference_a_minus_b"),
            "ci_low": stats.get("ci_low"),
            "ci_high": stats.get("ci_high"),
            "supports_b4_superiority": bool(stats.get("ci_low") is not None and stats["ci_low"] > 0.0),
            "supports_b4_inferiority": bool(stats.get("ci_high") is not None and stats["ci_high"] < 0.0),
        }

    calibration_rows = {}
    for draws, row in calibration.get("summary", {}).items():
        calibration_rows[draws] = {
            "target_attainable": row.get("target_attainable_at_draw_count"),
            "decision_disagreement_rate": row.get("decision_disagreement_rate"),
            "false_feasible_rate": row.get("false_feasible_rate"),
            "false_infeasible_rate": row.get("false_infeasible_rate"),
            "minimum_successes_to_accept": row.get("minimum_successes_to_accept"),
        }

    runtime_summary = runtime.get("summary", {})
    runtime_rows = {
        draws: policies.get(B4, {})
        for draws, policies in runtime_summary.items()
        if B4 in policies
    }

    uncertainty_summary = uncertainty.get("summary", {})
    uncertainty_boundary = {
        scale: {
            "b3_selection_rate": policies.get(B3, {}).get("selection_rate"),
            "b4_selection_rate": policies.get(B4, {}).get("selection_rate"),
            "b3_conditional_joint_qos": policies.get(B3, {}).get("joint_qos_conditional_on_selection"),
            "b4_conditional_joint_qos": policies.get(B4, {}).get("joint_qos_conditional_on_selection"),
        }
        for scale, policies in uncertainty_summary.items()
    }

    claim_status = {
        "b4_high_conditional_reliability_when_selected": reliable_when_selected,
        "b4_pays_availability_cost_vs_b3": availability_cost,
        "b4_unconditional_superiority_vs_b3": unconditional_superiority_supported,
        "b4_unconditional_inferiority_vs_b3": unconditional_inferiority_supported,
        "reliability_availability_tradeoff_supported": bool(reliable_when_selected and availability_cost),
        "universal_b4_superiority_allowed": False,
        "hardware_validation_allowed": False,
    }

    if claim_status["reliability_availability_tradeoff_supported"]:
        primary_interpretation = (
            "B4 identifies a conservative selectable operating subset with confidence-qualified high conditional joint reliability, "
            "while sacrificing availability relative to B3."
        )
    else:
        primary_interpretation = (
            "The current supplemental evidence does not yet satisfy the predeclared reliability-availability tradeoff claim gate."
        )

    return {
        "evidence_class": "DERIVED_SUPPLEMENTAL_PUBLICATION_V2_1_SIMULATION_VERDICT_NOT_HARDWARE_MEASUREMENT",
        "claim_status": claim_status,
        "primary_interpretation": primary_interpretation,
        "paired_b4_minus_b3_unconditional_joint_qos": paired,
        "full_metric_snapshot": {B3: b3, B4: b4},
        "distribution_shift_paired_effects": distribution_rows,
        "finite_draw_calibration": calibration_rows,
        "uncertainty_boundary": uncertainty_boundary,
        "pareto_partition": {
            "n_points": pareto.get("pareto", {}).get("n_points"),
            "n_non_dominated": pareto.get("pareto", {}).get("n_non_dominated"),
            "n_dominated": pareto.get("pareto", {}).get("n_dominated"),
            "claim_boundary": pareto.get("claim_boundary"),
        },
        "b4_runtime": runtime_rows,
        "forbidden_claims": [
            "Universal B4 superiority",
            "Hardware or RF measurement validation",
            "Global Pareto optimality outside realized selected operating points",
            "Confidence-qualified E9 claims from raw empirical flags alone",
        ],
    }


def main() -> None:
    args = parse_args()
    result = derive_verdict(Path(args.input_dir), bootstrap_resamples=args.bootstrap_resamples)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, allow_nan=False))
    print(out)


if __name__ == "__main__":
    main()
