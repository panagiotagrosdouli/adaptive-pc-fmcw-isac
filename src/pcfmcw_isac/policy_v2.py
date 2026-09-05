"""Publication-v2 policy semantics.

V1 is intentionally preserved as immutable diagnostic evidence.  V2 fixes two
pre-declared issues exposed by the frozen v1 run:
(1) B4 now gates reliability by a one-sided Wilson lower confidence bound and
    uses action-local independent uncertainty streams;
(2) ORACLE is a hindsight reference evaluated with the same receiver-level
    evaluator as reported outcomes, rather than the approximate selector model.
These changes are methodological corrections, not post-hoc threshold tuning.
"""
from __future__ import annotations

from dataclasses import replace
import hashlib

import numpy as np

from .policy_evaluation import (
    _cheapest,
    _estimated_state,
    _predict_metrics,
    evaluate_action,
    normalized_resource_cost,
    profile_registry,
)
from .publication_protocol import FROZEN_PROTOCOL_V1, EvaluationState, PhyActionSpec, filter_physics_feasible_actions
from .statistics import wilson_lower_bound


def _action_seed(state: EvaluationState, action: PhyActionSpec) -> int:
    """Stable action-local seed; independent of candidate enumeration order."""
    key = f"{state.seed}|{action.profile_name}|{action.chips_per_chirp}|{action.tx_power_backoff_db}|{action.repetition_factor}"
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "little") % (2**32 - 1)


def _robust_candidate(
    action: PhyActionSpec,
    estimated: EvaluationState,
    true_state: EvaluationState,
    *,
    robust_draws: int,
    confidence: float,
) -> tuple[bool, float, int]:
    rng = np.random.default_rng(_action_seed(true_state, action))
    success = 0
    u = true_state.state_uncertainty_scale
    for _ in range(robust_draws):
        draw = replace(
            estimated,
            ebn0_db=estimated.ebn0_db + rng.normal(0.0, 1.5 * u),
            if_snr_db=estimated.if_snr_db + rng.normal(0.0, 1.5 * u),
            radial_velocity_mps=estimated.radial_velocity_mps + rng.normal(0.0, 1.0 * u),
            residual_cfo_hz=max(0.0, estimated.residual_cfo_hz + rng.normal(0.0, 250.0 * u)),
        )
        feasible, c_ok, s_ok, _ = _predict_metrics(action, draw)
        success += int(feasible and c_ok and s_ok)
    lower = wilson_lower_bound(success, robust_draws, confidence=confidence)
    return lower >= FROZEN_PROTOCOL_V1.qos.joint_reliability_target, lower, success


def select_action_v2(
    policy: str,
    true_state: EvaluationState,
    *,
    robust_draws: int = 512,
    reliability_confidence: float = 0.95,
    oracle_comm_bits: int = 20_000,
    oracle_sensing_trials: int = 3,
) -> PhyActionSpec | None:
    """Select an action under corrected v2 semantics.

    ORACLE is explicitly a hindsight upper-reference: candidates are sorted by
    the declared resource cost and receiver-evaluated on the true state until
    the cheapest action satisfying joint QoS is found.  It is not a deployable
    policy and is never used to tune B0-B4.
    """
    actions = FROZEN_PROTOCOL_V1.actions()
    estimated = _estimated_state(true_state, true_state.state_uncertainty_scale)
    physics_actions = filter_physics_feasible_actions(actions, profile_registry(), estimated)
    if policy == "ORACLE":
        true_actions = filter_physics_feasible_actions(actions, profile_registry(), true_state)
        for action in sorted(true_actions, key=lambda a: (normalized_resource_cost(a), a.profile_name, a.chips_per_chirp, a.repetition_factor)):
            metrics = evaluate_action(action, true_state, comm_bits=oracle_comm_bits, sensing_trials=oracle_sensing_trials)
            if metrics.joint_qos:
                return action
        return None
    if not physics_actions:
        return None
    if policy == "B0_FIXED":
        fixed = PhyActionSpec("ti_77ghz_high_mobility_capability_profile", 32, 0.0, 2)
        return fixed if fixed in physics_actions else None
    if policy in ("B1_COMM_ONLY", "B2_SENSING_ONLY", "B3_DETERMINISTIC_JOINT"):
        candidates = []
        for action in physics_actions:
            _, comm_ok, sensing_ok, _ = _predict_metrics(action, estimated)
            if policy == "B1_COMM_ONLY" and comm_ok:
                candidates.append(action)
            elif policy == "B2_SENSING_ONLY" and sensing_ok:
                candidates.append(action)
            elif policy == "B3_DETERMINISTIC_JOINT" and comm_ok and sensing_ok:
                candidates.append(action)
        return _cheapest(candidates) if candidates else None
    if policy != "B4_ROBUST_JOINT":
        raise ValueError(f"unknown policy {policy!r}")
    candidates = []
    for action in physics_actions:
        accepted, _, _ = _robust_candidate(
            action,
            estimated,
            true_state,
            robust_draws=robust_draws,
            confidence=reliability_confidence,
        )
        if accepted:
            candidates.append(action)
    return _cheapest(candidates) if candidates else None


def evaluate_policy_v2(
    policy: str,
    state: EvaluationState,
    *,
    comm_bits: int = 20_000,
    sensing_trials: int = 3,
    robust_draws: int = 512,
    reliability_confidence: float = 0.95,
) -> dict:
    action = select_action_v2(
        policy,
        state,
        robust_draws=robust_draws,
        reliability_confidence=reliability_confidence,
        oracle_comm_bits=comm_bits,
        oracle_sensing_trials=sensing_trials,
    )
    if action is None:
        return {"policy": policy, "selected_action": None, "physics_feasible": False, "joint_qos": False, "outage": True}
    metrics = evaluate_action(action, state, comm_bits=comm_bits, sensing_trials=sensing_trials)
    return {
        "policy": policy,
        "selected_action": {
            "profile_name": action.profile_name,
            "chips_per_chirp": action.chips_per_chirp,
            "tx_power_backoff_db": action.tx_power_backoff_db,
            "repetition_factor": action.repetition_factor,
        },
        "physics_feasible": metrics.physics_feasible,
        "ber": metrics.ber,
        "effective_rate_bps": metrics.effective_rate_bps,
        "range_rmse_m": metrics.range_error_m,
        "velocity_rmse_mps": metrics.velocity_error_mps,
        "joint_qos": metrics.joint_qos,
        "outage": not metrics.joint_qos,
        "normalized_resource_cost": metrics.normalized_resource_cost,
        "protocol_semantics": "publication_v2",
    }
