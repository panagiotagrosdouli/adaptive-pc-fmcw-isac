"""Paper-1-specific deterministic physics-gate ablation.

This module is deliberately independent of the Paper 2 robust/Wilson policy story.
It compares two nominal selectors that differ only by whether the canonical FMCW
physical-feasibility filter is applied before action ranking. Outputs are
analytical/simulation-model evidence, never hardware measurements.
"""
from __future__ import annotations

from dataclasses import asdict
from itertools import product

import numpy as np

from .policy_evaluation import normalized_resource_cost, profile_registry, repetition_ber
from .publication_protocol import (
    EvaluationState,
    FROZEN_PROTOCOL_V1,
    PhyActionSpec,
    filter_physics_feasible_actions,
    is_physics_feasible,
)
from .publication_validation import _comm_cfg

EXPERIMENT_ID = "paper1_physics_gate_ablation_v1"
EVIDENCE_CLASS = "PAPER1_POST_FREEZE_ANALYTICAL_SIMULATION_MODEL_NOT_HARDWARE_MEASUREMENT"

# Boundary-aware grid: includes points immediately around both profiles' range and
# velocity limits as well as clearly feasible and clearly unsupported states.
RANGE_GRID_M = (0.0, 5.0, 10.0, 20.0, 22.0, 22.36, 23.0, 30.0, 40.0, 50.0, 56.0, 56.21, 57.0, 60.0)
VELOCITY_GRID_MPS = (-60.0, -50.0, -48.67, -48.0, -30.0, -10.0, -8.41, -8.0, 0.0, 8.0, 8.41, 10.0, 30.0, 48.0, 48.67, 50.0, 60.0)


def nominal_state(range_m: float, velocity_mps: float) -> EvaluationState:
    """Fixed non-stochastic selector state used to isolate the physics gate."""
    return EvaluationState(
        ebn0_db=12.0,
        if_snr_db=10.0,
        range_m=float(range_m),
        radial_velocity_mps=float(velocity_mps),
        residual_cfo_hz=0.0,
        inr_db=None,
        phase_noise_std_rad_per_sample=0.0,
        state_uncertainty_scale=0.0,
        seed=0,
    )


def _nominal_qos_ok(action: PhyActionSpec, state: EvaluationState) -> bool:
    """Nominal low-cost QoS screen with no physical-support test.

    This intentionally mirrors the selector-side communication/sensing bounds used
    elsewhere in the repository while omitting only the hard physics gate.
    """
    cfg = _comm_cfg(action.profile_name, action.chips_per_chirp)
    gamma = 10.0 ** ((state.ebn0_db - action.tx_power_backoff_db) / 10.0)
    p = repetition_ber(min(0.5, float(0.5 * np.exp(-gamma))), action.repetition_factor)
    rate = cfg.raw_bit_rate_bps / action.repetition_factor * (1.0 - p)
    radar = profile_registry()[action.profile_name]
    snr_lin = 10.0 ** ((state.if_snr_db - action.tx_power_backoff_db) / 10.0)
    scale = max(np.sqrt(max(snr_lin, 1e-9)), 1.0)
    q = FROZEN_PROTOCOL_V1.qos
    return bool(
        p <= q.ber_max
        and rate >= q.effective_rate_min_bps
        and radar.range_resolution_m / scale <= q.range_rmse_max_m
        and radar.velocity_resolution_mps / scale <= q.velocity_rmse_max_mps
    )


def _rank(action: PhyActionSpec) -> tuple:
    return (
        normalized_resource_cost(action),
        action.profile_name,
        action.chips_per_chirp,
        action.repetition_factor,
        action.tx_power_backoff_db,
    )


def select_nominal(state: EvaluationState, *, use_physics_gate: bool) -> PhyActionSpec | None:
    """Select the cheapest nominal-QoS action; optionally apply the hard gate first."""
    actions = FROZEN_PROTOCOL_V1.actions()
    if use_physics_gate:
        actions = filter_physics_feasible_actions(actions, profile_registry(), state)
    candidates = [a for a in actions if _nominal_qos_ok(a, state)]
    return min(candidates, key=_rank) if candidates else None


def action_is_physically_valid(action: PhyActionSpec | None, state: EvaluationState) -> bool:
    if action is None:
        return False
    return is_physics_feasible(profile_registry()[action.profile_name], state)


def classify_state(state: EvaluationState, selected: PhyActionSpec | None) -> str:
    any_feasible = bool(filter_physics_feasible_actions(FROZEN_PROTOCOL_V1.actions(), profile_registry(), state))
    if not any_feasible:
        return "PHYSICALLY_INFEASIBLE_STATE"
    if selected is None:
        return "POLICY_ABSTENTION"
    if action_is_physically_valid(selected, state):
        return "VALID_SELECTED_ACTION"
    return "INVALID_SELECTED_ACTION"


def _action_dict(action: PhyActionSpec | None) -> dict | None:
    return asdict(action) if action is not None else None


def run_paper1_physics_gate_ablation(
    ranges_m=RANGE_GRID_M,
    velocities_mps=VELOCITY_GRID_MPS,
) -> dict:
    """Run the deterministic boundary-aware gated-vs-ungated Paper 1 ablation."""
    profiles = profile_registry()
    records = []
    for range_m, velocity_mps in product(tuple(ranges_m), tuple(velocities_mps)):
        state = nominal_state(range_m, velocity_mps)
        gated = select_nominal(state, use_physics_gate=True)
        ungated = select_nominal(state, use_physics_gate=False)
        support = {name: is_physics_feasible(profile, state) for name, profile in profiles.items()}
        records.append({
            "range_m": float(range_m),
            "radial_velocity_mps": float(velocity_mps),
            "any_profile_feasible": any(support.values()),
            "profile_support": support,
            "gated_action": _action_dict(gated),
            "ungated_action": _action_dict(ungated),
            "gated_class": classify_state(state, gated),
            "ungated_class": classify_state(state, ungated),
            "gated_physics_valid": action_is_physically_valid(gated, state),
            "ungated_physics_valid": action_is_physically_valid(ungated, state),
            "selection_changed": gated != ungated,
        })

    n = len(records)
    gated_selected = [r for r in records if r["gated_action"] is not None]
    ungated_selected = [r for r in records if r["ungated_action"] is not None]
    ungated_invalid = [r for r in ungated_selected if not r["ungated_physics_valid"]]
    valid_alternative = [
        r for r in records
        if r["ungated_action"] is not None and not r["ungated_physics_valid"]
        and r["gated_action"] is not None and r["gated_physics_valid"]
    ]
    feasible_states = sum(bool(r["any_profile_feasible"]) for r in records)
    summary = {
        "total_states": n,
        "physically_feasible_states": feasible_states,
        "physically_feasible_state_fraction": feasible_states / n if n else None,
        "physically_infeasible_states": n - feasible_states,
        "gated_selected": len(gated_selected),
        "gated_selection_rate": len(gated_selected) / n if n else None,
        "gated_invalid_selections": sum(not r["gated_physics_valid"] for r in gated_selected),
        "ungated_selected": len(ungated_selected),
        "ungated_selection_rate": len(ungated_selected) / n if n else None,
        "ungated_invalid_selections": len(ungated_invalid),
        "ungated_invalid_selection_rate_all_states": len(ungated_invalid) / n if n else None,
        "ungated_invalid_selection_rate_conditional": len(ungated_invalid) / len(ungated_selected) if ungated_selected else None,
        "selection_changed_cases": sum(bool(r["selection_changed"]) for r in records),
        "ungated_invalid_gated_valid_alternative_cases": len(valid_alternative),
    }
    return {
        "experiment_id": EXPERIMENT_ID,
        "evidence_class": EVIDENCE_CLASS,
        "paper_scope": "Paper 1 deterministic physical representability only; no B4, Monte Carlo, Wilson, or reliability-availability claims.",
        "selector_fairness": "GATED and UNGATED use the same nominal QoS screen and deterministic resource ranking; the only difference is canonical physical-feasibility filtering before ranking.",
        "grid_rationale": "Boundary-aware range/velocity grid spans clearly feasible states, both profile boundaries, parking-invalid/high-mobility-valid states, and states unsupported by either profile.",
        "axes": {"range_m": list(map(float, ranges_m)), "radial_velocity_mps": list(map(float, velocities_mps))},
        "action_space_size": len(FROZEN_PROTOCOL_V1.actions()),
        "derived_profile_limits": {
            name: {
                "positive_if_max_range_m": p.positive_if_max_range_m,
                "max_unambiguous_velocity_mps": p.max_unambiguous_velocity_mps,
            }
            for name, p in profiles.items()
        },
        "summary": summary,
        "records": records,
    }
