"""Supplemental Part-B completion experiments for publication v2.1.

These analyses are explicitly post-freeze reviewer evidence. They do not modify
the frozen v2.1 controller, action space, QoS thresholds, primary seeds, or
archived primary results. All outputs are model-based simulation/analytical
evidence, never RF hardware measurements.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import asdict, replace
from typing import Iterable

import numpy as np

from .policy_evaluation import _cheapest, _estimated_state, profile_registry
from .policy_v2_1 import _action_seed, _predict_metrics_v2_1, evaluate_policy_v2_1, select_action_v2_1
from .publication_benchmark import benchmark_states
from .publication_protocol import FROZEN_PROTOCOL_V1, filter_physics_feasible_actions
from .statistics import wilson_lower_bound
from .supplemental_evidence_v2_1 import POLICIES, _evaluate_selected, _state_category


def _safe_mean(values: list[float]) -> float | None:
    return float(np.mean(values)) if values else None


def _full_metrics(rows: list[dict]) -> dict:
    n = len(rows)
    selected = [r for r in rows if r.get("selected_action") is not None]
    ns = len(selected)
    successes = sum(bool(r.get("joint_qos", False)) for r in rows)
    selected_successes = sum(bool(r.get("joint_qos", False)) for r in selected)
    infeasible = sum(r.get("state_category") == "PHYSICALLY_INFEASIBLE" for r in rows)
    abstained = sum(r.get("state_category") == "POLICY_ABSTENTION" for r in rows)
    profiles = Counter((r.get("selected_action") or {}).get("profile_name") for r in selected)
    return {
        "n": n, "selected": ns, "selection_rate": ns / n if n else None,
        "outage_probability": 1.0 - successes / n if n else None,
        "joint_qos_probability_unconditional": successes / n if n else None,
        "joint_qos_probability_conditional": selected_successes / ns if ns else None,
        "reliability_violation_rate_conditional": 1.0 - selected_successes / ns if ns else None,
        "wilson_lower_95_conditional": wilson_lower_bound(selected_successes, ns, confidence=0.95) if ns else None,
        "physically_infeasible_probability": infeasible / n if n else None,
        "policy_abstention_probability": abstained / n if n else None,
        "mean_ber_selected": _safe_mean([float(r["ber"]) for r in selected if r.get("ber") is not None]),
        "mean_effective_rate_bps_selected": _safe_mean([float(r["effective_rate_bps"]) for r in selected if r.get("effective_rate_bps") is not None]),
        "mean_range_rmse_m_selected": _safe_mean([float(r["range_rmse_m"]) for r in selected if r.get("range_rmse_m") is not None and np.isfinite(r["range_rmse_m"])]),
        "mean_velocity_rmse_mps_selected": _safe_mean([float(r["velocity_rmse_mps"]) for r in selected if r.get("velocity_rmse_mps") is not None and np.isfinite(r["velocity_rmse_mps"])]),
        "mean_normalized_resource_cost_selected": _safe_mean([float(r["normalized_resource_cost"]) for r in selected if r.get("normalized_resource_cost") is not None]),
        "profile_frequency_selected": {str(k): v / ns for k, v in sorted(profiles.items(), key=lambda x: str(x[0]))} if ns else {},
        "per_note": "PER is not independently estimated by this receiver model; do not derive or report a packet-level PER without a declared packet model.",
    }


def _robust_success_table(state, estimated, *, robust_draws: int, std_scales=(1.0, 1.0, 1.0, 1.0)):
    """Return action -> (Wilson lower bound, successes) using frozen action-local RNG.

    std_scales order is Eb/N0, IF-SNR, radial velocity, CFO. Setting one scale
    to zero is a true selector-side variance ablation; controller coordinates
    and receiver truth are otherwise unchanged.
    """
    actions = filter_physics_feasible_actions(FROZEN_PROTOCOL_V1.actions(), profile_registry(), estimated)
    table = {}
    u = state.state_uncertainty_scale
    se, si, sv, sc = std_scales
    for action in actions:
        rng = np.random.default_rng(_action_seed(state, action))
        success = 0
        for _ in range(robust_draws):
            draw = replace(
                estimated,
                ebn0_db=estimated.ebn0_db + rng.normal(0.0, 1.5 * u * se),
                if_snr_db=estimated.if_snr_db + rng.normal(0.0, 1.5 * u * si),
                radial_velocity_mps=estimated.radial_velocity_mps + rng.normal(0.0, 1.0 * u * sv),
                residual_cfo_hz=max(0.0, estimated.residual_cfo_hz + rng.normal(0.0, 250.0 * u * sc)),
            )
            feasible, c_ok, s_ok, _ = _predict_metrics_v2_1(action, draw)
            success += int(feasible and c_ok and s_ok)
        table[action] = (wilson_lower_bound(success, robust_draws, confidence=0.95), success)
    return table


def _select_from_table(table, target: float):
    return _cheapest([a for a, (lower, _) in table.items() if lower >= target]) if table else None


def run_full_metric_table(*, seeds: Iterable[int], comm_bits: int = 5000, sensing_trials: int = 1, robust_draws: int = 256) -> dict:
    rows = []
    for seed in seeds:
        for scenario_id, state in enumerate(benchmark_states(int(seed))):
            for policy in POLICIES:
                out = evaluate_policy_v2_1(policy, state, comm_bits=comm_bits, sensing_trials=sensing_trials, robust_draws=robust_draws)
                out["state_category"] = _state_category(state, out.get("selected_action"))
                rows.append({"seed": int(seed), "scenario_id": scenario_id, "state": asdict(state), **out})
    return {"records": rows, "summary": {p: _full_metrics([r for r in rows if r["policy"] == p]) for p in POLICIES}}


def run_reliability_target_sweep(*, seeds: Iterable[int], targets: Iterable[float] = (0.80, 0.85, 0.90, 0.925, 0.95, 0.975, 0.99), comm_bits: int = 5000, sensing_trials: int = 1, robust_draws: int = 256) -> dict:
    """Paired counterfactual sweep: every target sees identical robust draws."""
    targets = tuple(float(t) for t in targets)
    if any(not 0.0 < t < 1.0 for t in targets):
        raise ValueError("reliability targets must be in (0,1)")
    rows = []
    original = FROZEN_PROTOCOL_V1.qos.joint_reliability_target
    for seed in seeds:
        for scenario_id, state in enumerate(benchmark_states(int(seed))):
            estimated = _estimated_state(state, state.state_uncertainty_scale)
            table = _robust_success_table(state, estimated, robust_draws=robust_draws)
            for target in targets:
                action = _select_from_table(table, target)
                out = _evaluate_selected("B4_TARGET_SWEEP", action, state, comm_bits=comm_bits, sensing_trials=sensing_trials)
                rows.append({"target": target, "frozen_target": original, "seed": int(seed), "scenario_id": scenario_id, "state": asdict(state), **out})
    return {
        "records": rows,
        "summary": {str(t): _full_metrics([r for r in rows if r["target"] == t]) for t in targets},
        "claim_boundary": "Counterfactual supplemental sensitivity analysis with common action-local robust draws across targets; only target=0.95 is the frozen primary policy.",
        "finite_draw_note": "At finite robust_draws, high reliability targets can be unattainable under the one-sided Wilson acceptance rule even with zero observed failures.",
    }


def run_confidence_maps(*, seeds: Iterable[int], comm_bits: int = 5000, sensing_trials: int = 1, robust_draws: int = 256) -> dict:
    axes = {"ebn0_velocity": {"x": (-4., 0., 4., 8., 12., 16.), "y": (0., 10., 20., 30., 40., 50.)}, "inr_cfo": {"x": (-10., 0., 10., 20.), "y": (0., 500., 1000., 2000., 5000.)}}
    output = {}
    for name, grid in axes.items():
        cells = []
        for x in grid["x"]:
            for y in grid["y"]:
                rows = []
                for seed in seeds:
                    state = benchmark_states(int(seed))[0]
                    if name == "ebn0_velocity":
                        state = replace(state, ebn0_db=x, radial_velocity_mps=y, if_snr_db=10.0, range_m=20.0, residual_cfo_hz=500.0, inr_db=-10.0, phase_noise_std_rad_per_sample=0.001, state_uncertainty_scale=1.0)
                    else:
                        state = replace(state, ebn0_db=12.0, if_snr_db=10.0, range_m=20.0, radial_velocity_mps=20.0, inr_db=x, residual_cfo_hz=y, phase_noise_std_rad_per_sample=0.001, state_uncertainty_scale=1.0)
                    out = evaluate_policy_v2_1("B4_ROBUST_JOINT", state, comm_bits=comm_bits, sensing_trials=sensing_trials, robust_draws=robust_draws)
                    out["state_category"] = _state_category(state, out.get("selected_action")); rows.append(out)
                m = _full_metrics(rows)
                cells.append({"x": x, "y": y, **m, "confidence_qualified_target_0p95": bool(m["wilson_lower_95_conditional"] is not None and m["wilson_lower_95_conditional"] >= 0.95)})
        output[name] = {"x": grid["x"], "y": grid["y"], "cells": cells}
    return output


def run_uncertainty_source_ablations(*, seeds: Iterable[int], comm_bits: int = 5000, sensing_trials: int = 1, robust_draws: int = 256) -> dict:
    variants = {
        "FULL_B4": (1., 1., 1., 1.), "NO_EBN0_UNCERTAINTY": (0., 1., 1., 1.),
        "NO_IF_SNR_UNCERTAINTY": (1., 0., 1., 1.), "NO_VELOCITY_UNCERTAINTY": (1., 1., 0., 1.),
        "NO_CFO_UNCERTAINTY": (1., 1., 1., 0.),
    }
    rows = []
    target = FROZEN_PROTOCOL_V1.qos.joint_reliability_target
    for seed in seeds:
        for scenario_id, state in enumerate(benchmark_states(int(seed))):
            estimated = _estimated_state(state, state.state_uncertainty_scale)
            for label, scales in variants.items():
                if label == "FULL_B4":
                    action = select_action_v2_1("B4_ROBUST_JOINT", state, robust_draws=robust_draws)
                else:
                    action = _select_from_table(_robust_success_table(state, estimated, robust_draws=robust_draws, std_scales=scales), target)
                out = _evaluate_selected(label, action, state, comm_bits=comm_bits, sensing_trials=sensing_trials)
                rows.append({"ablation": label, "seed": int(seed), "scenario_id": scenario_id, "state": asdict(state), **out})
    return {
        "records": rows,
        "summary": {label: _full_metrics([r for r in rows if r["ablation"] == label]) for label in variants},
        "claim_boundary": "Selector-side source-variance ablation with unchanged controller coordinates and receiver truth; it is not a calibrated sensor-error experiment.",
    }
