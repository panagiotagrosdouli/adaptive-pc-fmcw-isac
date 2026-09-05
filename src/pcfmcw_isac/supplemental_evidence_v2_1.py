"""Reviewer-grade supplemental evidence for publication v2.1.

This module does not modify the frozen v2.1 protocol, thresholds, action space,
or frozen result artifacts.  It adds predeclared supplemental analyses requested
for robustness/reviewer scrutiny: uncertainty sweeps, impairment stress tests,
physics-only feasibility maps, physical-resource Pareto reporting, component
ablations, model-mismatch tests, and decision-runtime measurements.

All outputs are controlled simulation/analytical evidence, never hardware
measurements.  The hindsight Oracle remains a non-deployable reference.
"""
from __future__ import annotations

from dataclasses import asdict, replace
import hashlib
import math
import platform
import sys
import time
from typing import Iterable

import numpy as np

from .policy_evaluation import (
    _cheapest,
    _estimated_state,
    evaluate_action,
    normalized_resource_cost,
    profile_registry,
    repetition_ber,
)
from .policy_v2_1 import _predict_metrics_v2_1, evaluate_policy_v2_1, select_action_v2_1
from .publication_benchmark import benchmark_states, paired_bootstrap_difference
from .publication_benchmark_v2 import physical_resource_vector
from .publication_protocol import (
    EvaluationState,
    FROZEN_PROTOCOL_V1,
    PhyActionSpec,
    filter_physics_feasible_actions,
    is_physics_feasible,
)
from .publication_validation import _comm_cfg
from .statistics import wilson_lower_bound

POLICIES = ("B0_FIXED", "B1_COMM_ONLY", "B2_SENSING_ONLY", "B3_DETERMINISTIC_JOINT", "B4_ROBUST_JOINT", "ORACLE")


def _seed_for(*parts: object) -> int:
    digest = hashlib.sha256("|".join(map(str, parts)).encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "little") % (2**32 - 1)


def _state_category(state: EvaluationState, selected_action: dict | None) -> str:
    actions = FROZEN_PROTOCOL_V1.actions()
    physically_possible = bool(filter_physics_feasible_actions(actions, profile_registry(), state))
    if not physically_possible:
        return "PHYSICALLY_INFEASIBLE"
    if selected_action is None:
        return "POLICY_ABSTENTION"
    return "SELECTED"


def _aggregate(rows: list[dict]) -> dict:
    if not rows:
        return {"n": 0}
    selected = [r for r in rows if r.get("selected_action") is not None]
    success = sum(bool(r.get("joint_qos", False)) for r in rows)
    selected_success = sum(bool(r.get("joint_qos", False)) for r in selected)
    n = len(rows)
    ns = len(selected)
    categories = {k: 0 for k in ("PHYSICALLY_INFEASIBLE", "POLICY_ABSTENTION", "SELECTED")}
    for r in rows:
        categories[r["state_category"]] += 1
    return {
        "n": n,
        "selected": ns,
        "selection_rate": ns / n,
        "joint_qos_successes": success,
        "joint_qos_unconditional": success / n,
        "joint_qos_conditional_on_selection": (selected_success / ns) if ns else None,
        "wilson_lower_95_unconditional": wilson_lower_bound(success, n, confidence=0.95),
        "wilson_lower_95_conditional": wilson_lower_bound(selected_success, ns, confidence=0.95) if ns else None,
        "state_categories": categories,
    }


def _evaluate_selected(label: str, action: PhyActionSpec | None, state: EvaluationState, *, comm_bits: int, sensing_trials: int) -> dict:
    if action is None:
        out = {
            "policy": label,
            "selected_action": None,
            "joint_qos": False,
            "outage": True,
        }
    else:
        m = evaluate_action(action, state, comm_bits=comm_bits, sensing_trials=sensing_trials)
        out = {
            "policy": label,
            "selected_action": asdict(action),
            "physics_feasible": m.physics_feasible,
            "ber": m.ber,
            "effective_rate_bps": m.effective_rate_bps,
            "range_rmse_m": m.range_error_m,
            "velocity_rmse_mps": m.velocity_error_mps,
            "joint_qos": m.joint_qos,
            "outage": not m.joint_qos,
            "normalized_resource_cost": m.normalized_resource_cost,
            "resource_vector": physical_resource_vector(action),
        }
    out["state_category"] = _state_category(state, out.get("selected_action"))
    return out


def _predict_without_physics_gate(action: PhyActionSpec, state: EvaluationState) -> tuple[bool, bool, float]:
    """Selector-only predictor intentionally omitting the hard range/velocity gate.

    This is an ablation, not a deployable policy.  Receiver-level evaluation
    still enforces real physical feasibility via evaluate_action().
    """
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

    radar = profile_registry()[action.profile_name]
    snr_lin = 10.0 ** ((state.if_snr_db - action.tx_power_backoff_db) / 10.0)
    scale = np.sqrt(max(snr_lin, 1e-12))
    r_bound = radar.range_resolution_m / scale
    v_bound = radar.velocity_resolution_mps / scale
    q = FROZEN_PROTOCOL_V1.qos
    comm_ok = p <= q.ber_max and rate >= q.effective_rate_min_bps
    sensing_ok = r_bound <= q.range_rmse_max_m and v_bound <= q.velocity_rmse_max_mps
    return bool(comm_ok), bool(sensing_ok), normalized_resource_cost(action)


def _robust_select_custom(
    true_state: EvaluationState,
    controller_state: EvaluationState,
    *,
    robust_draws: int,
    use_physics_gate: bool = True,
    require_joint_constraint: bool = True,
    uncertainty_scale: float | None = None,
) -> PhyActionSpec | None:
    actions = FROZEN_PROTOCOL_V1.actions()
    candidates_actions = (
        filter_physics_feasible_actions(actions, profile_registry(), controller_state)
        if use_physics_gate else actions
    )
    if not candidates_actions:
        return None
    u = controller_state.state_uncertainty_scale if uncertainty_scale is None else float(uncertainty_scale)
    accepted: list[PhyActionSpec] = []
    for action in candidates_actions:
        rng = np.random.default_rng(_seed_for("supp-v2.1", true_state.seed, action, use_physics_gate, require_joint_constraint, u))
        success = 0
        for _ in range(robust_draws):
            draw = replace(
                controller_state,
                ebn0_db=controller_state.ebn0_db + rng.normal(0.0, 1.5 * u),
                if_snr_db=controller_state.if_snr_db + rng.normal(0.0, 1.5 * u),
                radial_velocity_mps=controller_state.radial_velocity_mps + rng.normal(0.0, 1.0 * u),
                residual_cfo_hz=max(0.0, controller_state.residual_cfo_hz + rng.normal(0.0, 250.0 * u)),
            )
            if use_physics_gate:
                feasible, c_ok, s_ok, _ = _predict_metrics_v2_1(action, draw)
            else:
                c_ok, s_ok, _ = _predict_without_physics_gate(action, draw)
                feasible = True
            pass_qos = c_ok and (s_ok if require_joint_constraint else True)
            success += int(feasible and pass_qos)
        lower = wilson_lower_bound(success, robust_draws, confidence=0.95)
        if lower >= FROZEN_PROTOCOL_V1.qos.joint_reliability_target:
            accepted.append(action)
    return _cheapest(accepted) if accepted else None


def _deterministic_select_from_controller_state(controller_state: EvaluationState) -> PhyActionSpec | None:
    actions = filter_physics_feasible_actions(FROZEN_PROTOCOL_V1.actions(), profile_registry(), controller_state)
    candidates = []
    for action in actions:
        _, c_ok, s_ok, _ = _predict_metrics_v2_1(action, controller_state)
        if c_ok and s_ok:
            candidates.append(action)
    return _cheapest(candidates) if candidates else None


def run_uncertainty_sweep(
    *,
    seeds: Iterable[int],
    uncertainty_scales: Iterable[float] = (0.0, 0.5, 1.0, 1.5, 2.0, 3.0),
    comm_bits: int = 5_000,
    sensing_trials: int = 1,
    robust_draws: int = 256,
) -> dict:
    records = []
    for u in uncertainty_scales:
        for seed in seeds:
            for scenario_id, base in enumerate(benchmark_states(int(seed))):
                state = replace(base, state_uncertainty_scale=float(u))
                for policy in ("B3_DETERMINISTIC_JOINT", "B4_ROBUST_JOINT"):
                    out = evaluate_policy_v2_1(policy, state, comm_bits=comm_bits, sensing_trials=sensing_trials, robust_draws=robust_draws)
                    out["state_category"] = _state_category(state, out.get("selected_action"))
                    records.append({"uncertainty_scale": float(u), "scenario_id": scenario_id, "state": asdict(state), **out})
    summary = {}
    for u in uncertainty_scales:
        summary[str(float(u))] = {}
        for p in ("B3_DETERMINISTIC_JOINT", "B4_ROBUST_JOINT"):
            summary[str(float(u))][p] = _aggregate([r for r in records if r["policy"] == p and r["uncertainty_scale"] == float(u)])
    return {"records": records, "summary": summary}


def run_impairment_stress(
    *,
    seeds: Iterable[int],
    comm_bits: int = 5_000,
    sensing_trials: int = 1,
    robust_draws: int = 256,
) -> dict:
    sweeps = {
        "residual_cfo_hz": (0.0, 500.0, 1000.0, 2000.0, 5000.0, 8000.0),
        "inr_db": (None, -10.0, 0.0, 10.0, 20.0),
        "phase_noise_std_rad_per_sample": (0.0, 0.001, 0.003, 0.01, 0.03),
    }
    base_template = EvaluationState(12.0, 5.0, 20.0, 30.0, 500.0, -10.0, 0.001, 1.0, 0)
    result = {}
    for axis, values in sweeps.items():
        records = []
        for value in values:
            for seed in seeds:
                state = replace(base_template, seed=int(seed), **{axis: value})
                for policy in ("B3_DETERMINISTIC_JOINT", "B4_ROBUST_JOINT"):
                    out = evaluate_policy_v2_1(policy, state, comm_bits=comm_bits, sensing_trials=sensing_trials, robust_draws=robust_draws)
                    out["state_category"] = _state_category(state, out.get("selected_action"))
                    records.append({axis: value, "state": asdict(state), **out})
        summary = {}
        for value in values:
            key = "None" if value is None else str(float(value))
            summary[key] = {}
            for p in ("B3_DETERMINISTIC_JOINT", "B4_ROBUST_JOINT"):
                summary[key][p] = _aggregate([r for r in records if r["policy"] == p and r[axis] == value])
        result[axis] = {"records": records, "summary": summary}
    return result


def run_physics_only_maps() -> dict:
    profiles = profile_registry()
    ranges = (0.0, 5.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0)
    velocities = (-60.0, -50.0, -30.0, -10.0, 0.0, 10.0, 30.0, 50.0, 60.0)
    cells = []
    for r in ranges:
        for v in velocities:
            state = EvaluationState(12.0, 10.0, r, v, 0.0, None, 0.0, 0.0, 0)
            support = {name: bool(is_physics_feasible(profile, state)) for name, profile in profiles.items()}
            cells.append({"range_m": r, "radial_velocity_mps": v, "profiles": support, "any_profile_feasible": any(support.values())})
    derived_limits = {
        name: {
            "range_resolution_m": p.range_resolution_m,
            "positive_if_max_range_m": p.positive_if_max_range_m,
            "velocity_resolution_mps": p.velocity_resolution_mps,
            "max_unambiguous_velocity_mps": p.max_unambiguous_velocity_mps,
        }
        for name, p in profiles.items()
    }
    return {"axes": {"range_m": ranges, "radial_velocity_mps": velocities}, "derived_profile_limits": derived_limits, "cells": cells}


def run_extended_ablations(
    *,
    seeds: Iterable[int],
    comm_bits: int = 5_000,
    sensing_trials: int = 1,
    robust_draws: int = 256,
) -> dict:
    variants = ("FULL_B4", "NO_PHYSICS_GATE", "NO_STATE_UNCERTAINTY", "NO_JOINT_CONSTRAINT")
    records = []
    for seed in seeds:
        for scenario_id, state in enumerate(benchmark_states(int(seed))):
            estimated = _estimated_state(state, state.state_uncertainty_scale)
            actions = {
                "FULL_B4": select_action_v2_1("B4_ROBUST_JOINT", state, robust_draws=robust_draws),
                "NO_PHYSICS_GATE": _robust_select_custom(state, estimated, robust_draws=robust_draws, use_physics_gate=False, require_joint_constraint=True),
                "NO_STATE_UNCERTAINTY": _robust_select_custom(state, replace(estimated, state_uncertainty_scale=0.0), robust_draws=robust_draws, use_physics_gate=True, require_joint_constraint=True, uncertainty_scale=0.0),
                "NO_JOINT_CONSTRAINT": _robust_select_custom(state, estimated, robust_draws=robust_draws, use_physics_gate=True, require_joint_constraint=False),
            }
            for name in variants:
                out = _evaluate_selected(name, actions[name], state, comm_bits=comm_bits, sensing_trials=sensing_trials)
                records.append({"ablation": name, "scenario_id": scenario_id, "state": asdict(state), **out})
    return {"records": records, "summary": {name: _aggregate([r for r in records if r["ablation"] == name]) for name in variants}}


def run_model_mismatch(
    *,
    seeds: Iterable[int],
    comm_bits: int = 5_000,
    sensing_trials: int = 1,
    robust_draws: int = 256,
) -> dict:
    """Paired B3/B4 tests where controller assumptions differ from the true state."""
    cases = {
        "CFO_UNDERMODELING": ((500.0, 1000.0), (500.0, 2000.0), (500.0, 5000.0)),
        "SNR_BIAS": ((12.0, 10.0), (12.0, 8.0), (12.0, 6.0)),
        "DOPPLER_BIAS": ((20.0, 25.0), (20.0, 30.0), (20.0, 40.0)),
        "INTERFERENCE_UNDERMODELING": ((-10.0, 0.0), (-10.0, 10.0), (-10.0, 20.0)),
    }
    records = []
    for family, pairs in cases.items():
        for assumed, actual in pairs:
            for seed in seeds:
                true_state = EvaluationState(12.0, 5.0, 20.0, 20.0, 500.0, -10.0, 0.001, 1.0, int(seed))
                controller_state = _estimated_state(true_state, true_state.state_uncertainty_scale)
                if family == "CFO_UNDERMODELING":
                    controller_state = replace(controller_state, residual_cfo_hz=float(assumed))
                    true_state = replace(true_state, residual_cfo_hz=float(actual))
                elif family == "SNR_BIAS":
                    controller_state = replace(controller_state, ebn0_db=float(assumed))
                    true_state = replace(true_state, ebn0_db=float(actual))
                elif family == "DOPPLER_BIAS":
                    controller_state = replace(controller_state, radial_velocity_mps=float(assumed))
                    true_state = replace(true_state, radial_velocity_mps=float(actual))
                elif family == "INTERFERENCE_UNDERMODELING":
                    controller_state = replace(controller_state, inr_db=float(assumed))
                    true_state = replace(true_state, inr_db=float(actual))
                b3 = _deterministic_select_from_controller_state(controller_state)
                b4 = _robust_select_custom(true_state, controller_state, robust_draws=robust_draws, use_physics_gate=True, require_joint_constraint=True)
                for policy, action in (("B3_DETERMINISTIC_JOINT", b3), ("B4_ROBUST_JOINT", b4)):
                    out = _evaluate_selected(policy, action, true_state, comm_bits=comm_bits, sensing_trials=sensing_trials)
                    records.append({
                        "mismatch_family": family,
                        "assumed": assumed,
                        "actual": actual,
                        "state": asdict(true_state),
                        "controller_state": asdict(controller_state),
                        **out,
                    })
    summary = {}
    for family, pairs in cases.items():
        summary[family] = {}
        for assumed, actual in pairs:
            key = f"assumed={assumed}|actual={actual}"
            summary[family][key] = {
                p: _aggregate([r for r in records if r["mismatch_family"] == family and r["assumed"] == assumed and r["actual"] == actual and r["policy"] == p])
                for p in ("B3_DETERMINISTIC_JOINT", "B4_ROBUST_JOINT")
            }
    return {"records": records, "summary": summary}


def run_physical_pareto(
    *,
    seeds: Iterable[int],
    comm_bits: int = 5_000,
    sensing_trials: int = 1,
    robust_draws: int = 256,
) -> dict:
    rows = []
    for seed in seeds:
        for scenario_id, state in enumerate(benchmark_states(int(seed))):
            out = evaluate_policy_v2_1("B4_ROBUST_JOINT", state, comm_bits=comm_bits, sensing_trials=sensing_trials, robust_draws=robust_draws)
            if out.get("selected_action") is None:
                continue
            a = out["selected_action"]
            action = PhyActionSpec(a["profile_name"], a["chips_per_chirp"], a["tx_power_backoff_db"], a["repetition_factor"])
            rv = physical_resource_vector(action)
            rows.append({"scenario_id": scenario_id, "state": asdict(state), "joint_qos": bool(out["joint_qos"]), "effective_rate_bps": out.get("effective_rate_bps"), "range_rmse_m": out.get("range_rmse_m"), "velocity_rmse_mps": out.get("velocity_rmse_mps"), **rv})
    grouped: dict[tuple, list[dict]] = {}
    for row in rows:
        key = (row["tx_power_fraction"], row["repetition_factor"], row["chips_per_chirp"], row["profile_adc_samples_per_frame"])
        grouped.setdefault(key, []).append(row)
    points = []
    for key, g in grouped.items():
        points.append({
            "tx_power_fraction": key[0],
            "repetition_factor": key[1],
            "chips_per_chirp": key[2],
            "profile_adc_samples_per_frame": key[3],
            "n": len(g),
            "joint_qos_probability": float(np.mean([float(r["joint_qos"]) for r in g])),
            "mean_effective_rate_bps": float(np.mean([r["effective_rate_bps"] for r in g])),
            "mean_range_rmse_m": float(np.mean([r["range_rmse_m"] for r in g])),
            "mean_velocity_rmse_mps": float(np.mean([r["velocity_rmse_mps"] for r in g])),
        })
    return {"selected_records": rows, "physical_points": sorted(points, key=lambda p: (p["tx_power_fraction"], p["repetition_factor"], p["chips_per_chirp"]))}


def run_runtime_benchmark(
    *,
    seeds: Iterable[int],
    robust_draws_values: Iterable[int] = (64, 128, 256, 512),
    repetitions: int = 3,
) -> dict:
    measurements = []
    states = []
    for seed in seeds:
        states.extend(benchmark_states(int(seed)))
    for draws in robust_draws_values:
        for policy in ("B0_FIXED", "B1_COMM_ONLY", "B2_SENSING_ONLY", "B3_DETERMINISTIC_JOINT", "B4_ROBUST_JOINT"):
            for rep in range(repetitions):
                for idx, state in enumerate(states):
                    t0 = time.perf_counter_ns()
                    action = select_action_v2_1(policy, state, robust_draws=int(draws))
                    elapsed_us = (time.perf_counter_ns() - t0) / 1000.0
                    estimated = _estimated_state(state, state.state_uncertainty_scale)
                    survivors = len(filter_physics_feasible_actions(FROZEN_PROTOCOL_V1.actions(), profile_registry(), estimated))
                    measurements.append({
                        "policy": policy,
                        "robust_draws": int(draws),
                        "rep": rep,
                        "state_index": idx,
                        "elapsed_us": elapsed_us,
                        "candidate_actions": len(FROZEN_PROTOCOL_V1.actions()),
                        "physics_gate_survivors": survivors,
                        "selected": action is not None,
                    })
    summary = {}
    for draws in robust_draws_values:
        summary[str(int(draws))] = {}
        for policy in ("B0_FIXED", "B1_COMM_ONLY", "B2_SENSING_ONLY", "B3_DETERMINISTIC_JOINT", "B4_ROBUST_JOINT"):
            vals = np.asarray([m["elapsed_us"] for m in measurements if m["policy"] == policy and m["robust_draws"] == int(draws)], dtype=float)
            summary[str(int(draws))][policy] = {
                "n": int(vals.size),
                "median_us": float(np.median(vals)),
                "p95_us": float(np.quantile(vals, 0.95)),
                "p99_us": float(np.quantile(vals, 0.99)),
                "mean_us": float(np.mean(vals)),
            }
    return {
        "environment": {"python": sys.version, "platform": platform.platform(), "processor": platform.processor()},
        "measurements": measurements,
        "summary": summary,
        "claim_boundary": "Host-runtime benchmark only; it is not an embedded ECU real-time certification.",
    }


def run_same_seed_policy_check(*, seeds: Iterable[int], comm_bits: int = 5_000, sensing_trials: int = 1, robust_draws: int = 256) -> dict:
    records = []
    for seed in seeds:
        for scenario_id, state in enumerate(benchmark_states(int(seed))):
            for p in POLICIES:
                out = evaluate_policy_v2_1(p, state, comm_bits=comm_bits, sensing_trials=sensing_trials, robust_draws=robust_draws)
                out["state_category"] = _state_category(state, out.get("selected_action"))
                records.append({"scenario_id": scenario_id, "state": asdict(state), **out})
    aggregate = {p: _aggregate([r for r in records if r["policy"] == p]) for p in POLICIES}
    paired = paired_bootstrap_difference(records, "B4_ROBUST_JOINT", "B3_DETERMINISTIC_JOINT", n_resamples=2000)
    return {"records": records, "aggregate": aggregate, "paired_B4_minus_B3": paired}
