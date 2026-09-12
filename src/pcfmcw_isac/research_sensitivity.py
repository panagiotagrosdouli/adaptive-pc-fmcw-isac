"""Counterfactual QoS-threshold sensitivity for frozen policy decisions.

The controller decisions are generated once using the declared v2.1 policy.
Continuous receiver metrics are then rescored under alternative QoS thresholds.
This deliberately separates conclusion sensitivity from policy redesign and must
not be described as re-optimizing the controller for each threshold.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Iterable

from .policy_evaluation import _estimated_state
from .policy_v2_1 import select_action_v2_1
from .publication_benchmark import benchmark_states
from .supplemental_evidence_v2_1 import _deterministic_select_from_controller_state, _evaluate_selected
from .statistics import wilson_lower_bound


@dataclass(frozen=True)
class CounterfactualQoS:
    name: str
    ber_max: float
    rate_min_bps: float
    range_rmse_max_m: float
    velocity_rmse_max_mps: float

    def validate(self) -> None:
        if not 0.0 < self.ber_max < 1.0: raise ValueError("ber_max must be in (0,1)")
        if self.rate_min_bps <= 0.0: raise ValueError("rate_min_bps must be positive")
        if self.range_rmse_max_m <= 0.0 or self.velocity_rmse_max_mps <= 0.0: raise ValueError("RMSE limits must be positive")


def default_qos_variants() -> tuple[CounterfactualQoS, ...]:
    return (
        CounterfactualQoS("BASELINE", 1e-3, 1e5, 1.0, 1.0),
        CounterfactualQoS("STRICT_COMM", 1e-4, 2e5, 1.0, 1.0),
        CounterfactualQoS("RELAXED_COMM", 1e-2, 5e4, 1.0, 1.0),
        CounterfactualQoS("STRICT_SENSING", 1e-3, 1e5, 0.5, 0.5),
        CounterfactualQoS("RELAXED_SENSING", 1e-3, 1e5, 2.0, 2.0),
        CounterfactualQoS("STRICT_JOINT", 1e-4, 2e5, 0.5, 0.5),
        CounterfactualQoS("RELAXED_JOINT", 1e-2, 5e4, 2.0, 2.0),
    )


def _score(row: dict, q: CounterfactualQoS) -> bool:
    if row.get("selected_action") is None or not row.get("physics_feasible", False):
        return False
    values = (row.get("ber"), row.get("effective_rate_bps"), row.get("range_rmse_m"), row.get("velocity_rmse_mps"))
    if any(v is None for v in values):
        return False
    ber, rate, rr, vr = values
    return bool(ber <= q.ber_max and rate >= q.rate_min_bps and rr <= q.range_rmse_max_m and vr <= q.velocity_rmse_max_mps)


def _aggregate(rows: list[dict]) -> dict:
    n = len(rows); selected = [r for r in rows if r.get("selected_action") is not None]; ns = len(selected)
    success = sum(bool(r["counterfactual_joint_qos"]) for r in rows)
    selected_success = sum(bool(r["counterfactual_joint_qos"]) for r in selected)
    return {
        "n": n,
        "selected": ns,
        "selection_rate": ns / n if n else None,
        "counterfactual_joint_qos_unconditional": success / n if n else None,
        "counterfactual_joint_qos_conditional": selected_success / ns if ns else None,
        "wilson_lower_95_conditional": wilson_lower_bound(selected_success, ns, confidence=0.95) if ns else None,
    }


def run_qos_threshold_sensitivity(
    *,
    seeds: Iterable[int],
    comm_bits: int = 5_000,
    sensing_trials: int = 1,
    robust_draws: int = 256,
    variants: Iterable[CounterfactualQoS] | None = None,
) -> dict:
    """Rescore identical B3/B4 decisions under alternative receiver QoS thresholds."""
    variants = tuple(variants or default_qos_variants())
    if not variants: raise ValueError("at least one QoS variant is required")
    for q in variants: q.validate()
    base_records: list[dict] = []
    for seed in seeds:
        for scenario_id, state in enumerate(benchmark_states(int(seed))):
            estimated = _estimated_state(state, state.state_uncertainty_scale)
            actions = {
                "B3_DETERMINISTIC_JOINT": _deterministic_select_from_controller_state(estimated),
                "B4_ROBUST_JOINT": select_action_v2_1("B4_ROBUST_JOINT", state, robust_draws=robust_draws),
            }
            for policy, action in actions.items():
                out = _evaluate_selected(policy, action, state, comm_bits=comm_bits, sensing_trials=sensing_trials)
                base_records.append({"seed": int(seed), "scenario_id": scenario_id, "state": asdict(state), **out})

    records: list[dict] = []
    for q in variants:
        for row in base_records:
            records.append({
                **row,
                "qos_variant": q.name,
                "qos_thresholds": asdict(q),
                "counterfactual_joint_qos": _score(row, q),
            })
    summary = {
        q.name: {
            policy: _aggregate([r for r in records if r["qos_variant"] == q.name and r["policy"] == policy])
            for policy in ("B3_DETERMINISTIC_JOINT", "B4_ROBUST_JOINT")
        }
        for q in variants
    }
    return {
        "records": records,
        "summary": summary,
        "method_boundary": "Post-selection counterfactual rescoring of identical controller decisions; not policy re-optimization under each threshold.",
    }
