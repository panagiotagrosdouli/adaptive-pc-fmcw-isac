"""Publication-v2.1 benchmark orchestration after selector calibration.

V2.1 preserves all QoS thresholds and receiver-level evaluation from v2 while
using the corrected SNR-sensitive sensing guard in policy_v2_1. Outputs are
simulation evidence, not hardware measurements.
"""
from __future__ import annotations

from dataclasses import asdict, replace
from typing import Iterable

import numpy as np

from .policy_v2_1 import evaluate_policy_v2_1
from .publication_benchmark import benchmark_states, paired_bootstrap_difference
from .publication_benchmark_v2 import (
    POLICIES_V2,
    aggregate_policy_metrics_v2,
    pareto_front,
    physical_resource_vector,
)
from .publication_protocol import EvaluationState, FROZEN_PROTOCOL_V1, PhyActionSpec

POLICIES_V2_1 = POLICIES_V2


def run_paired_benchmark_v2_1(
    seeds: Iterable[int],
    *,
    comm_bits: int = 20_000,
    sensing_trials: int = 3,
    robust_draws: int = 512,
) -> list[dict]:
    records: list[dict] = []
    for seed in seeds:
        for scenario_id, state in enumerate(benchmark_states(int(seed))):
            for policy in POLICIES_V2_1:
                out = evaluate_policy_v2_1(
                    policy,
                    state,
                    comm_bits=comm_bits,
                    sensing_trials=sensing_trials,
                    robust_draws=robust_draws,
                )
                resource = None
                if out.get("selected_action") is not None:
                    a = out["selected_action"]
                    action = PhyActionSpec(
                        a["profile_name"],
                        a["chips_per_chirp"],
                        a["tx_power_backoff_db"],
                        a["repetition_factor"],
                    )
                    resource = physical_resource_vector(action)
                records.append(
                    {
                        "scenario_id": scenario_id,
                        "state": asdict(state),
                        "resource_vector": resource,
                        **out,
                    }
                )
    return records


def feasible_region_slice_v2_1(
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
    cells = []
    for x in values_x:
        for y in values_y:
            outcomes = []
            selections = []
            for seed in seeds:
                state = replace(base_state, **{axis_x: x, axis_y: y, "seed": int(seed)})
                out = evaluate_policy_v2_1(
                    policy,
                    state,
                    comm_bits=comm_bits,
                    sensing_trials=sensing_trials,
                    robust_draws=robust_draws,
                )
                outcomes.append(float(out.get("joint_qos", False)))
                selections.append(float(out.get("selected_action") is not None))
            cells.append(
                {
                    axis_x: x,
                    axis_y: y,
                    "joint_qos_probability": float(np.mean(outcomes)),
                    "selection_rate": float(np.mean(selections)),
                    "empirically_meets_declared_target": bool(
                        np.mean(outcomes) >= FROZEN_PROTOCOL_V1.qos.joint_reliability_target
                    ),
                }
            )
    return {
        "policy": policy,
        "protocol_semantics": "publication_v2_1",
        "axis_x": axis_x,
        "axis_y": axis_y,
        "cells": cells,
    }


def run_e11_ablations_v2_1(
    states: Iterable[EvaluationState],
    *,
    comm_bits: int = 5_000,
    sensing_trials: int = 1,
    robust_draws: int = 256,
) -> list[dict]:
    records = []
    for idx, state in enumerate(states):
        variants = {
            "FULL_B4": state,
            "NO_STATE_UNCERTAINTY": replace(state, state_uncertainty_scale=0.0),
            "NO_CFO": replace(state, residual_cfo_hz=0.0),
            "NO_INTERFERENCE": replace(state, inr_db=None),
        }
        for name, variant_state in variants.items():
            out = evaluate_policy_v2_1(
                "B4_ROBUST_JOINT",
                variant_state,
                comm_bits=comm_bits,
                sensing_trials=sensing_trials,
                robust_draws=robust_draws,
            )
            records.append(
                {
                    "ablation": name,
                    "state_id": idx,
                    "state": asdict(variant_state),
                    **out,
                }
            )
    return records


def run_v2_1_smoke() -> dict:
    seeds = range(FROZEN_PROTOCOL_V1.final_seed_start, FROZEN_PROTOCOL_V1.final_seed_start + 2)
    records = run_paired_benchmark_v2_1(
        seeds,
        comm_bits=2_000,
        sensing_trials=1,
        robust_draws=64,
    )
    aggregate = aggregate_policy_metrics_v2(records)
    oracle = aggregate.get("ORACLE", {})
    deployable_max = max(
        aggregate[p]["joint_qos_probability_unconditional"]
        for p in POLICIES_V2_1
        if p != "ORACLE"
    )
    b1 = aggregate["B1_COMM_ONLY"]
    b3 = aggregate["B3_DETERMINISTIC_JOINT"]
    sanity = {
        "oracle_not_below_best_deployable": bool(
            oracle.get("joint_qos_probability_unconditional", 0.0) >= deployable_max
        ),
        "b1_b3_are_distinguishable": bool(
            b1["selection_rate"] != b3["selection_rate"]
            or b1["joint_qos_probability_unconditional"]
            != b3["joint_qos_probability_unconditional"]
            or b1["mean_normalized_resource_cost_when_selected"]
            != b3["mean_normalized_resource_cost_when_selected"]
        ),
    }
    return {
        "evidence_class": "PUBLICATION_V2_1_SMOKE_SIMULATION_NOT_FINAL_PAPER_RESULT",
        "protocol_parent": "pcfmcw_isac_paper_v2",
        "records": records,
        "aggregate": aggregate,
        "paired_B4_minus_B3_joint_qos": paired_bootstrap_difference(
            records,
            "B4_ROBUST_JOINT",
            "B3_DETERMINISTIC_JOINT",
            n_resamples=500,
        ),
        "sanity_gate": sanity,
        "pareto_B4": pareto_front(records, "B4_ROBUST_JOINT"),
    }
