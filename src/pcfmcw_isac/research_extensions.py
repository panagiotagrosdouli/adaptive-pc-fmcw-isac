"""Post-freeze research experiments for reliability calibration and action-space sensitivity.

These experiments are intentionally separate from the frozen publication-v2.1
benchmark. They consume the same controller and receiver models but answer two
reviewer-facing questions that the frozen benchmark does not resolve:

1) How often does a finite-draw Wilson reliability certificate disagree with a
   higher-draw reference decision, and how stable is that decision?
2) How sensitive are selection, conditional joint QoS, and resource cost to
   restrictions of the PC-FMCW action space?

All outputs are simulation/analytical evidence, never hardware measurements.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import asdict
from typing import Iterable

import numpy as np

from .part_b_completion import _full_metrics, _robust_success_table, _select_from_table
from .policy_evaluation import _estimated_state, normalized_resource_cost
from .publication_benchmark import benchmark_states
from .publication_protocol import FROZEN_PROTOCOL_V1, PhyActionSpec
from .supplemental_evidence_v2_1 import _evaluate_selected


def _restricted_select(
    state,
    *,
    robust_draws: int,
    allowed_profiles: set[str] | None = None,
    allowed_chips: set[int] | None = None,
    allowed_repetitions: set[int] | None = None,
    allowed_backoff_db: set[float] | None = None,
) -> PhyActionSpec | None:
    estimated = _estimated_state(state, state.state_uncertainty_scale)
    table = _robust_success_table(state, estimated, robust_draws=robust_draws)
    target = FROZEN_PROTOCOL_V1.qos.joint_reliability_target
    accepted = []
    for action, (lower, _) in table.items():
        if lower < target:
            continue
        if allowed_profiles is not None and action.profile_name not in allowed_profiles:
            continue
        if allowed_chips is not None and action.chips_per_chirp not in allowed_chips:
            continue
        if allowed_repetitions is not None and action.repetition_factor not in allowed_repetitions:
            continue
        if allowed_backoff_db is not None and action.tx_power_backoff_db not in allowed_backoff_db:
            continue
        accepted.append(action)
    if not accepted:
        return None
    return min(
        accepted,
        key=lambda a: (
            normalized_resource_cost(a),
            a.profile_name,
            a.chips_per_chirp,
            a.repetition_factor,
            a.tx_power_backoff_db,
        ),
    )


def run_reliability_calibration(
    *,
    seeds: Iterable[int],
    robust_draws_values: Iterable[int] = (32, 64, 128, 256, 512),
    reference_draws: int = 4096,
    target: float = 0.95,
) -> dict:
    """Compare finite-draw robust decisions against a higher-draw reference.

    The statistical unit is one benchmark state. The reference is not treated as
    ground truth; it is a much lower-Monte-Carlo-noise decision used to quantify
    finite-draw disagreement and instability.
    """
    draws_values = tuple(int(x) for x in robust_draws_values)
    if any(x <= 0 for x in draws_values) or reference_draws <= 0:
        raise ValueError("draw counts must be positive")
    if not 0.0 < target < 1.0:
        raise ValueError("target must be in (0,1)")

    records: list[dict] = []
    for seed in seeds:
        for scenario_id, state in enumerate(benchmark_states(int(seed))):
            estimated = _estimated_state(state, state.state_uncertainty_scale)
            reference_table = _robust_success_table(state, estimated, robust_draws=reference_draws)
            reference_action = _select_from_table(reference_table, target)
            reference_feasible = reference_action is not None

            for draws in draws_values:
                table = _robust_success_table(state, estimated, robust_draws=draws)
                action = _select_from_table(table, target)
                feasible = action is not None
                records.append(
                    {
                        "seed": int(seed),
                        "scenario_id": scenario_id,
                        "robust_draws": draws,
                        "target": target,
                        "reference_draws": reference_draws,
                        "reference_feasible": reference_feasible,
                        "finite_feasible": feasible,
                        "false_feasible": bool(feasible and not reference_feasible),
                        "false_infeasible": bool((not feasible) and reference_feasible),
                        "same_selected_action": bool(action == reference_action),
                        "selected_action": asdict(action) if action is not None else None,
                        "reference_action": asdict(reference_action) if reference_action is not None else None,
                    }
                )

    summary = {}
    for draws in draws_values:
        rows = [r for r in records if r["robust_draws"] == draws]
        n = len(rows)
        summary[str(draws)] = {
            "n": n,
            "false_feasible_rate": sum(r["false_feasible"] for r in rows) / n if n else None,
            "false_infeasible_rate": sum(r["false_infeasible"] for r in rows) / n if n else None,
            "decision_disagreement_rate": sum(r["finite_feasible"] != r["reference_feasible"] for r in rows) / n if n else None,
            "selected_action_disagreement_rate": sum(not r["same_selected_action"] for r in rows) / n if n else None,
            "finite_selection_rate": sum(r["finite_feasible"] for r in rows) / n if n else None,
            "reference_selection_rate": sum(r["reference_feasible"] for r in rows) / n if n else None,
        }
    return {
        "records": records,
        "summary": summary,
        "reference_note": "The high-draw reference reduces Monte Carlo decision noise but is not physical ground truth.",
    }


def run_action_space_sensitivity(
    *,
    seeds: Iterable[int],
    comm_bits: int = 5_000,
    sensing_trials: int = 1,
    robust_draws: int = 256,
) -> dict:
    """Evaluate how PC-FMCW action-space restrictions alter robust operation."""
    variants = {
        "FULL": {},
        "HIGH_MOBILITY_PROFILE_ONLY": {"allowed_profiles": {"ti_77ghz_high_mobility_capability_profile"}},
        "PARKING_PROFILE_ONLY": {"allowed_profiles": {"ti_77ghz_parking_profile"}},
        "NO_REPETITION": {"allowed_repetitions": {1}},
        "FIXED_32_CHIPS": {"allowed_chips": {32}},
        "NO_POWER_BACKOFF": {"allowed_backoff_db": {0.0}},
    }
    records: list[dict] = []
    for seed in seeds:
        for scenario_id, state in enumerate(benchmark_states(int(seed))):
            for label, restrictions in variants.items():
                action = _restricted_select(state, robust_draws=robust_draws, **restrictions)
                out = _evaluate_selected(label, action, state, comm_bits=comm_bits, sensing_trials=sensing_trials)
                records.append(
                    {
                        "variant": label,
                        "seed": int(seed),
                        "scenario_id": scenario_id,
                        "state": asdict(state),
                        **out,
                    }
                )

    summary = {label: _full_metrics([r for r in records if r["variant"] == label]) for label in variants}
    action_frequency = {}
    for label in variants:
        rows = [r for r in records if r["variant"] == label and r.get("selected_action") is not None]
        counts = Counter(
            (
                r["selected_action"]["profile_name"],
                r["selected_action"]["chips_per_chirp"],
                r["selected_action"]["tx_power_backoff_db"],
                r["selected_action"]["repetition_factor"],
            )
            for r in rows
        )
        action_frequency[label] = {str(k): int(v) for k, v in counts.most_common()}
    return {"records": records, "summary": summary, "action_frequency": action_frequency}
