"""Physics-gated B0-B4 evaluation on the frozen publication action set.

This module deliberately avoids the legacy surrogate model in physics.py.  It
uses the validated DBPSK reference modem, explicit repetition coding, the
FMCW IF receiver, and the hard profile feasibility gate.  Returned values are
simulation/analytical evidence, never hardware measurements.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from math import comb, log10
from typing import Iterable

import numpy as np

from .if_model import Target, estimate_single_target, synthesize_if
from .profiles import high_mobility_profile, short_range_profile
from .publication_protocol import (
    EvaluationState,
    FROZEN_PROTOCOL_V1,
    PhyActionSpec,
    filter_physics_feasible_actions,
)
from .publication_validation import _comm_cfg, simulate_dbpsk_impaired


@dataclass(frozen=True)
class ActionMetrics:
    physics_feasible: bool
    ber: float
    effective_rate_bps: float
    range_error_m: float
    velocity_error_mps: float
    joint_qos: bool
    normalized_resource_cost: float


def profile_registry():
    return {
        "ti_77ghz_parking_profile": short_range_profile(),
        "ti_77ghz_high_mobility_capability_profile": high_mobility_profile(),
    }


def normalized_resource_cost(action: PhyActionSpec) -> float:
    """Declared dimensionless experiment cost, not joules or monetary cost."""
    action.validate()
    profile_factor = 1.0 if action.profile_name == "ti_77ghz_parking_profile" else 1.6
    power_fraction = 10.0 ** (-action.tx_power_backoff_db / 10.0)
    chip_factor = action.chips_per_chirp / 16.0
    return float(profile_factor * (0.55 * power_fraction + 0.25 * chip_factor + 0.20 * action.repetition_factor))


def repetition_ber(bit_ber: float, repetitions: int) -> float:
    """BER after independent hard-decision repetition with random tie breaking."""
    if not 0.0 <= bit_ber <= 1.0:
        raise ValueError("bit_ber must be in [0,1]")
    if repetitions not in (1, 2, 4):
        raise ValueError("repetitions outside frozen action set")
    p = 0.0
    half = repetitions / 2.0
    for k in range(repetitions + 1):
        pk = comb(repetitions, k) * bit_ber**k * (1.0 - bit_ber) ** (repetitions - k)
        if k > half:
            p += pk
        elif k == half:
            p += 0.5 * pk
    return float(p)


def _single_sensing_trial(action: PhyActionSpec, state: EvaluationState, *, seed: int) -> tuple[float, float]:
    p = profile_registry()[action.profile_name]
    # Power backoff reduces radar echo SNR by the same transmitted-power dB.
    sensing_snr_db = state.if_snr_db - action.tx_power_backoff_db
    rng = np.random.default_rng(seed)
    y = synthesize_if(
        p,
        [Target(state.range_m, state.radial_velocity_mps)],
        snr_db=sensing_snr_db,
        rng=rng,
    )
    r_hat, v_hat = estimate_single_target(p, y)
    return float(abs(r_hat - state.range_m)), float(abs(v_hat - state.radial_velocity_mps))


def evaluate_action(
    action: PhyActionSpec,
    state: EvaluationState,
    *,
    comm_bits: int = 20_000,
    sensing_trials: int = 3,
) -> ActionMetrics:
    """Evaluate one action on one true state using receiver-level simulation."""
    action.validate()
    profiles = profile_registry()
    feasible = action in filter_physics_feasible_actions((action,), profiles, state)
    if not feasible:
        return ActionMetrics(False, 0.5, 0.0, float("inf"), float("inf"), False, normalized_resource_cost(action))

    cfg = _comm_cfg(action.profile_name, action.chips_per_chirp)
    effective_ebn0 = state.ebn0_db - action.tx_power_backoff_db
    base_ber = simulate_dbpsk_impaired(
        effective_ebn0,
        comm_bits,
        cfg=cfg,
        residual_frequency_hz=state.residual_cfo_hz,
        phase_noise_std_rad_per_chip=state.phase_noise_std_rad_per_sample,
        inr_db=state.inr_db,
        seed=state.seed + action.chips_per_chirp * 13 + int(action.tx_power_backoff_db * 101),
    )
    ber = repetition_ber(base_ber, action.repetition_factor)
    rate = cfg.raw_bit_rate_bps / action.repetition_factor * (1.0 - ber)

    r_errors = []
    v_errors = []
    for k in range(sensing_trials):
        re, ve = _single_sensing_trial(action, state, seed=state.seed + 1000 + 17 * k)
        r_errors.append(re)
        v_errors.append(ve)
    range_rmse = float(np.sqrt(np.mean(np.square(r_errors))))
    velocity_rmse = float(np.sqrt(np.mean(np.square(v_errors))))

    q = FROZEN_PROTOCOL_V1.qos
    joint = (
        ber <= q.ber_max
        and rate >= q.effective_rate_min_bps
        and range_rmse <= q.range_rmse_max_m
        and velocity_rmse <= q.velocity_rmse_max_mps
    )
    return ActionMetrics(
        True,
        ber,
        rate,
        range_rmse,
        velocity_rmse,
        bool(joint),
        normalized_resource_cost(action),
    )


def _estimated_state(true_state: EvaluationState, uncertainty_scale: float) -> EvaluationState:
    if uncertainty_scale <= 0:
        return true_state
    rng = np.random.default_rng(true_state.seed + 77_777)
    return replace(
        true_state,
        ebn0_db=true_state.ebn0_db + rng.normal(0.0, 1.5 * uncertainty_scale),
        if_snr_db=true_state.if_snr_db + rng.normal(0.0, 1.5 * uncertainty_scale),
        radial_velocity_mps=true_state.radial_velocity_mps + rng.normal(0.0, 1.0 * uncertainty_scale),
        residual_cfo_hz=max(0.0, true_state.residual_cfo_hz + rng.normal(0.0, 250.0 * uncertainty_scale)),
    )


def _predict_metrics(action: PhyActionSpec, state: EvaluationState) -> tuple[bool, bool, bool, float]:
    """Low-cost deterministic selector model calibrated to physical quantities.

    Final reported metrics still come from evaluate_action(); this predictor is
    used only to choose an action without consuming the held-out evaluation RNG.
    """
    profiles = profile_registry()
    feasible = action in filter_physics_feasible_actions((action,), profiles, state)
    if not feasible:
        return False, False, False, normalized_resource_cost(action)
    cfg = _comm_cfg(action.profile_name, action.chips_per_chirp)
    gamma = 10.0 ** ((state.ebn0_db - action.tx_power_backoff_db) / 10.0)
    # Exact noncoherent DBPSK AWGN reference before impairment penalties.
    p = 0.5 * np.exp(-gamma)
    cfo_phase = 2.0 * np.pi * state.residual_cfo_hz * cfg.chip_duration_s
    impairment = 1.0 + 0.5 * cfo_phase**2 + state.phase_noise_std_rad_per_sample**2
    if state.inr_db is not None:
        impairment *= 1.0 + 10.0 ** (state.inr_db / 10.0) / max(gamma, 1e-12)
    p = min(0.5, float(p * impairment))
    p = repetition_ber(p, action.repetition_factor)
    rate = cfg.raw_bit_rate_bps / action.repetition_factor * (1.0 - p)

    radar = profiles[action.profile_name]
    # Selector-side sensing guard uses physical bin scales plus SNR monotonicity;
    # held-out performance is always measured with the IF receiver above.
    snr_lin = 10.0 ** ((state.if_snr_db - action.tx_power_backoff_db) / 10.0)
    r_bound = radar.range_resolution_m / max(np.sqrt(max(snr_lin, 1e-9)), 1.0)
    v_bound = radar.velocity_resolution_mps / max(np.sqrt(max(snr_lin, 1e-9)), 1.0)
    q = FROZEN_PROTOCOL_V1.qos
    comm_ok = p <= q.ber_max and rate >= q.effective_rate_min_bps
    sensing_ok = r_bound <= q.range_rmse_max_m and v_bound <= q.velocity_rmse_max_mps
    return True, bool(comm_ok), bool(sensing_ok), normalized_resource_cost(action)


def _cheapest(actions: Iterable[PhyActionSpec]) -> PhyActionSpec:
    return min(actions, key=lambda a: (normalized_resource_cost(a), a.profile_name, a.chips_per_chirp, a.repetition_factor))


def select_action(policy: str, true_state: EvaluationState, *, robust_draws: int = 64) -> PhyActionSpec | None:
    actions = FROZEN_PROTOCOL_V1.actions()
    estimated = _estimated_state(true_state, true_state.state_uncertainty_scale)
    physics_actions = filter_physics_feasible_actions(actions, profile_registry(), estimated)
    if not physics_actions:
        return None

    if policy == "B0_FIXED":
        fixed = PhyActionSpec("ti_77ghz_high_mobility_capability_profile", 32, 0.0, 2)
        return fixed if fixed in physics_actions else None
    if policy == "ORACLE":
        candidates = []
        for a in filter_physics_feasible_actions(actions, profile_registry(), true_state):
            _, c_ok, s_ok, _ = _predict_metrics(a, true_state)
            if c_ok and s_ok:
                candidates.append(a)
        return _cheapest(candidates) if candidates else None
    if policy in ("B1_COMM_ONLY", "B2_SENSING_ONLY", "B3_DETERMINISTIC_JOINT"):
        candidates = []
        for a in physics_actions:
            _, c_ok, s_ok, _ = _predict_metrics(a, estimated)
            if policy == "B1_COMM_ONLY" and c_ok:
                candidates.append(a)
            elif policy == "B2_SENSING_ONLY" and s_ok:
                candidates.append(a)
            elif policy == "B3_DETERMINISTIC_JOINT" and c_ok and s_ok:
                candidates.append(a)
        return _cheapest(candidates) if candidates else None
    if policy != "B4_ROBUST_JOINT":
        raise ValueError(f"unknown policy {policy!r}")

    rng = np.random.default_rng(true_state.seed + 88_888)
    candidates = []
    for a in physics_actions:
        success = 0
        for _ in range(robust_draws):
            u = true_state.state_uncertainty_scale
            draw = replace(
                estimated,
                ebn0_db=estimated.ebn0_db + rng.normal(0.0, 1.5 * u),
                if_snr_db=estimated.if_snr_db + rng.normal(0.0, 1.5 * u),
                radial_velocity_mps=estimated.radial_velocity_mps + rng.normal(0.0, 1.0 * u),
                residual_cfo_hz=max(0.0, estimated.residual_cfo_hz + rng.normal(0.0, 250.0 * u)),
            )
            feasible, c_ok, s_ok, _ = _predict_metrics(a, draw)
            success += int(feasible and c_ok and s_ok)
        if success / robust_draws >= FROZEN_PROTOCOL_V1.qos.joint_reliability_target:
            candidates.append(a)
    return _cheapest(candidates) if candidates else None


def evaluate_policy(policy: str, state: EvaluationState, *, comm_bits: int = 20_000, sensing_trials: int = 3) -> dict:
    action = select_action(policy, state)
    if action is None:
        return {
            "policy": policy,
            "selected_action": None,
            "physics_feasible": False,
            "joint_qos": False,
            "outage": True,
        }
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
    }
