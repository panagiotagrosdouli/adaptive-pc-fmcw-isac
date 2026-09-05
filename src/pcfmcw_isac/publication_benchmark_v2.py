"""Publication-v2 benchmark orchestration.

This module preserves v1 outputs and implements the corrected v2 semantics for
paired evaluation, feasible operating regions (E9), physical resource reporting
and Pareto analysis (E10), and predeclared ablations (E11).

All outputs are simulation evidence, never hardware measurements.
"""
from __future__ import annotations

from dataclasses import asdict, replace
from typing import Iterable

import numpy as np

from .policy_v2 import evaluate_policy_v2, select_action_v2
from .policy_evaluation import normalized_resource_cost
from .publication_benchmark import benchmark_states, paired_bootstrap_difference
from .publication_protocol import EvaluationState, FROZEN_PROTOCOL_V1, PhyActionSpec

POLICIES_V2 = (
    "B0_FIXED",
    "B1_COMM_ONLY",
    "B2_SENSING_ONLY",
    "B3_DETERMINISTIC_JOINT",
    "B4_ROBUST_JOINT",
    "ORACLE",
)


def physical_resource_vector(action: PhyActionSpec) -> dict:
    """Report interpretable resource coordinates, not a claim of physical energy."""
    profile_adc_samples = 256 * 64 if action.profile_name == "ti_77ghz_parking_profile" else 750 * 128
    return {
        "tx_power_fraction": float(10.0 ** (-action.tx_power_backoff_db / 10.0)),
        "repetition_factor": int(action.repetition_factor),
        "chips_per_chirp": int(action.chips_per_chirp),
        "profile_adc_samples_per_frame": int(profile_adc_samples),
        "normalized_resource_cost": float(normalized_resource_cost(action)),
    }


def run_paired_benchmark_v2(
    seeds: Iterable[int],
    *,
    comm_bits: int = 20_000,
    sensing_trials: int = 3,
    robust_draws: int = 512,
) -> list[dict]:
    records: list[dict] = []
    for seed in seeds:
        for scenario_id, state in enumerate(benchmark_states(int(seed))):
            for policy in POLICIES_V2:
                out = evaluate_policy_v2(
                    policy,
                    state,
                    comm_bits=comm_bits,
                    sensing_trials=sensing_trials,
                    robust_draws=robust_draws,
                )
                resource = None
                if out.get("selected_action") is not None:
                    a = out["selected_action"]
                    action = PhyActionSpec(a["profile_name"], a["chips_per_chirp"], a["tx_power_backoff_db"], a["repetition_factor"])
                    resource = physical_resource_vector(action)
                records.append({"scenario_id": scenario_id, "state": asdict(state), "resource_vector": resource, **out})
    return records


def aggregate_policy_metrics_v2(records: list[dict]) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for policy in POLICIES_V2:
        rows = [r for r in records if r["policy"] == policy]
        if not rows:
            continue
        selected = [r for r in rows if r.get("selected_action") is not None]
        joint_all = np.asarray([float(r.get("joint_qos", False)) for r in rows])
        joint_selected = np.asarray([float(r.get("joint_qos", False)) for r in selected]) if selected else np.asarray([])
        costs = np.asarray([float(r["normalized_resource_cost"]) for r in selected]) if selected else np.asarray([])
        result[policy] = {
            "n": len(rows),
            "selection_rate": float(len(selected) / len(rows)),
            "abstention_rate": float(1.0 - len(selected) / len(rows)),
            "joint_qos_probability_unconditional": float(np.mean(joint_all)),
            "joint_qos_probability_conditional_on_selection": float(np.mean(joint_selected)) if joint_selected.size else None,
            "mean_normalized_resource_cost_when_selected": float(np.mean(costs)) if costs.size else None,
        }
    return result


def feasible_region_slice(
    *,
    axis_x: str,
    values_x: Iterable[float],
    axis_y: str,
    values_y: Iterable[float],
    base_state: EvaluationState,
    policy: str = "B4_ROBUST_JOINT",
    seeds: Iterable[int] = range(10000, 10020),
    comm_bits: int = 5_000,
    sensing_trials: int = 1,
    robust_draws: int = 256,
) -> dict:
    """E9 machine-readable 2-D reliability map for a predeclared state slice."""
    cells = []
    for x in values_x:
        for y in values_y:
            outcomes = []
            selections = []
            for seed in seeds:
                state = replace(base_state, **{axis_x: x, axis_y: y, "seed": int(seed)})
                out = evaluate_policy_v2(policy, state, comm_bits=comm_bits, sensing_trials=sensing_trials, robust_draws=robust_draws)
                outcomes.append(float(out.get("joint_qos", False)))
                selections.append(float(out.get("selected_action") is not None))
            cells.append({
                axis_x: x,
                axis_y: y,
                "joint_qos_probability": float(np.mean(outcomes)),
                "selection_rate": float(np.mean(selections)),
                "empirically_meets_declared_target": bool(np.mean(outcomes) >= FROZEN_PROTOCOL_V1.qos.joint_reliability_target),
            })
    return {"policy": policy, "axis_x": axis_x, "axis_y": axis_y, "cells": cells}


def pareto_front(records: list[dict], policy: str) -> list[dict]:
    """E10 non-dominated aggregate points: maximize QoS, minimize cost and occupancy."""
    rows = [r for r in records if r["policy"] == policy and r.get("resource_vector") is not None]
    if not rows:
        return []
    grouped: dict[tuple, list[dict]] = {}
    for r in rows:
        rv = r["resource_vector"]
        key = (rv["tx_power_fraction"], rv["repetition_factor"], rv["chips_per_chirp"], rv["profile_adc_samples_per_frame"])
        grouped.setdefault(key, []).append(r)
    points = []
    for key, g in grouped.items():
        points.append({
            "tx_power_fraction": key[0],
            "repetition_factor": key[1],
            "chips_per_chirp": key[2],
            "profile_adc_samples_per_frame": key[3],
            "joint_qos_probability": float(np.mean([float(r.get("joint_qos", False)) for r in g])),
            "mean_normalized_resource_cost": float(np.mean([r["normalized_resource_cost"] for r in g])),
            "n": len(g),
        })
    front = []
    for p in points:
        dominated = False
        for q in points:
            if q is p:
                continue
            no_worse = q["joint_qos_probability"] >= p["joint_qos_probability"] and q["mean_normalized_resource_cost"] <= p["mean_normalized_resource_cost"] and q["repetition_factor"] <= p["repetition_factor"]
            strictly = q["joint_qos_probability"] > p["joint_qos_probability"] or q["mean_normalized_resource_cost"] < p["mean_normalized_resource_cost"] or q["repetition_factor"] < p["repetition_factor"]
            if no_worse and strictly:
                dominated = True
                break
        if not dominated:
            front.append(p)
    return sorted(front, key=lambda p: (p["mean_normalized_resource_cost"], -p["joint_qos_probability"]))


def run_e11_ablations(
    states: Iterable[EvaluationState],
    *,
    comm_bits: int = 5_000,
    sensing_trials: int = 1,
    robust_draws: int = 256,
) -> list[dict]:
    """Predeclared v2 ablations without changing QoS thresholds."""
    records = []
    for idx, state in enumerate(states):
        variants = {
            "FULL_B4": state,
            "NO_STATE_UNCERTAINTY": replace(state, state_uncertainty_scale=0.0),
            "NO_CFO": replace(state, residual_cfo_hz=0.0),
            "NO_INTERFERENCE": replace(state, inr_db=None),
        }
        for name, variant_state in variants.items():
            out = evaluate_policy_v2("B4_ROBUST_JOINT", variant_state, comm_bits=comm_bits, sensing_trials=sensing_trials, robust_draws=robust_draws)
            records.append({"ablation": name, "state_id": idx, "state": asdict(variant_state), **out})
    return records


def run_v2_smoke() -> dict:
    seeds = range(FROZEN_PROTOCOL_V1.final_seed_start, FROZEN_PROTOCOL_V1.final_seed_start + 2)
    records = run_paired_benchmark_v2(seeds, comm_bits=2_000, sensing_trials=1, robust_draws=64)
    return {
        "evidence_class": "PUBLICATION_V2_SMOKE_SIMULATION_NOT_FINAL_PAPER_RESULT",
        "protocol_parent": FROZEN_PROTOCOL_V1.protocol_id,
        "records": records,
        "aggregate": aggregate_policy_metrics_v2(records),
        "paired_B4_minus_B3_joint_qos": paired_bootstrap_difference(records, "B4_ROBUST_JOINT", "B3_DETERMINISTIC_JOINT", n_resamples=500),
    }
