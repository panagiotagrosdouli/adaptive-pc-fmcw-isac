"""Publication-v2.1 policy semantics after the mandatory v2 smoke gate.

The v2 smoke run is preserved as immutable diagnostic evidence. It exposed that
B1 and B3 collapsed because the v1/v2 selector-side sensing heuristic clipped
the SNR penalty at unity, making the declared 1 m / 1 m/s sensing constraints
non-binding for every physics-feasible action. V2.1 fixes only that selector
model defect; QoS thresholds and receiver-level evaluation are unchanged.

All reported outcomes remain simulation evidence, never hardware measurements.
"""
from __future__ import annotations

from dataclasses import replace
import hashlib

import numpy as np

from .policy_evaluation import (
    _cheapest,
    _estimated_state,
    evaluate_action,
    normalized_resource_cost,
    profile_registry,
    repetition_ber,
)
from .publication_protocol import (
    FROZEN_PROTOCOL_V1,
    EvaluationState,
    PhyActionSpec,
    filter_physics_feasible_actions,
)
from .publication_validation import _comm_cfg
from .statistics import wilson_lower_bound


def _action_seed(state: EvaluationState, action: PhyActionSpec) -> int:
    key = (
        f"v2.1|{state.seed}|{action.profile_name}|{action.chips_per_chirp}|"
        f"{action.tx_power_backoff_db}|{action.repetition_factor}"
    )
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "little") % (2**32 - 1)


def _predict_metrics_v2_1(
    action: PhyActionSpec,
    state: EvaluationState,
) -> tuple[bool, bool, bool, float]:
    """Low-cost v2.1 selector model with SNR-sensitive sensing guards.

    Communication keeps the analytical DBPSK-plus-impairment approximation used
    in v2. The sensing guard scales the physical range/velocity resolution by
    1/sqrt(SNR) without the v1/v2 unit floor. This restores the expected
    low-SNR degradation and prevents sensing QoS from being tautologically true.
    Receiver-level metrics are still produced only by evaluate_action().
    """
    profiles = profile_registry()
    feasible = action in filter_physics_feasible_actions((action,), profiles, state)
    if not feasible:
        return False, False, False, normalized_resource_cost(action)

    cfg = _comm_cfg(action.profile_name, action.chips_per_chirp)
    gamma = 10.0 ** ((state.ebn0_db - action.tx_power_backoff_db) / 10.0)
    p = 0.5 * np.exp(-gamma)
    cfo_phase = 2.0 * np.pi * state.residual_cfo_hz * cfg.chip_duration_s
    impairment = 1.0 + 0.5 * cfo_phase**2 + state.phase_noise_std_rad_per_sample**2
    if state.inr_db is not None:
        impairment *= 1.0 + 10.0 ** (state.inr_db / 10.0) / max(gamma, 1e-12)
    p = min(0.5, float(p * impairment))
    p = repetition_ber(p, action.repetition_factor)
    rate = cfg.raw_bit_rate_bps / action.repetition_factor * (1.0 - p)

    radar = profiles[action.profile_name]
    snr_lin = 10.0 ** ((state.if_snr_db - action.tx_power_backoff_db) / 10.0)
    snr_scale = np.sqrt(max(snr_lin, 1e-12))
    r_bound = radar.range_resolution_m / snr_scale
    v_bound = radar.velocity_resolution_mps / snr_scale

    q = FROZEN_PROTOCOL_V1.qos
    comm_ok = p <= q.ber_max and rate >= q.effective_rate_min_bps
    sensing_ok = r_bound <= q.range_rmse_max_m and v_bound <= q.velocity_rmse_max_mps
    return True, bool(comm_ok), bool(sensing_ok), normalized_resource_cost(action)


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
            residual_cfo_hz=max(
                0.0,
                estimated.residual_cfo_hz + rng.normal(0.0, 250.0 * u),
            ),
        )
        feasible, c_ok, s_ok, _ = _predict_metrics_v2_1(action, draw)
        success += int(feasible and c_ok and s_ok)
    lower = wilson_lower_bound(success, robust_draws, confidence=confidence)
    return lower >= FROZEN_PROTOCOL_V1.qos.joint_reliability_target, lower, success


def select_action_v2_1(
    policy: str,
    true_state: EvaluationState,
    *,
    robust_draws: int = 512,
    reliability_confidence: float = 0.95,
    oracle_comm_bits: int = 20_000,
    oracle_sensing_trials: int = 3,
) -> PhyActionSpec | None:
    actions = FROZEN_PROTOCOL_V1.actions()
    estimated = _estimated_state(true_state, true_state.state_uncertainty_scale)
    physics_actions = filter_physics_feasible_actions(actions, profile_registry(), estimated)

    if policy == "ORACLE":
        true_actions = filter_physics_feasible_actions(actions, profile_registry(), true_state)
        ordered = sorted(
            true_actions,
            key=lambda a: (
                normalized_resource_cost(a),
                a.profile_name,
                a.chips_per_chirp,
                a.repetition_factor,
            ),
        )
        for action in ordered:
            metrics = evaluate_action(
                action,
                true_state,
                comm_bits=oracle_comm_bits,
                sensing_trials=oracle_sensing_trials,
            )
            if metrics.joint_qos:
                return action
        return None

    if not physics_actions:
        return None
    if policy == "B0_FIXED":
        fixed = PhyActionSpec(
            "ti_77ghz_high_mobility_capability_profile", 32, 0.0, 2
        )
        return fixed if fixed in physics_actions else None

    if policy in ("B1_COMM_ONLY", "B2_SENSING_ONLY", "B3_DETERMINISTIC_JOINT"):
        candidates = []
        for action in physics_actions:
            _, comm_ok, sensing_ok, _ = _predict_metrics_v2_1(action, estimated)
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


def evaluate_policy_v2_1(
    policy: str,
    state: EvaluationState,
    *,
    comm_bits: int = 20_000,
    sensing_trials: int = 3,
    robust_draws: int = 512,
    reliability_confidence: float = 0.95,
) -> dict:
    action = select_action_v2_1(
        policy,
        state,
        robust_draws=robust_draws,
        reliability_confidence=reliability_confidence,
        oracle_comm_bits=comm_bits,
        oracle_sensing_trials=sensing_trials,
    )
    if action is None:
        return {
            "policy": policy,
            "selected_action": None,
            "physics_feasible": False,
            "joint_qos": False,
            "outage": True,
            "protocol_semantics": "publication_v2_1",
        }
    metrics = evaluate_action(
        action,
        state,
        comm_bits=comm_bits,
        sensing_trials=sensing_trials,
    )
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
        "protocol_semantics": "publication_v2_1",
    }
