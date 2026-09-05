"""E6-E12 benchmark orchestration for the frozen publication protocol.

The benchmark uses predeclared states from the frozen axes and evaluates all
policies on paired seeds.  It produces machine-readable simulation evidence;
it does not contain hand-entered paper results.
"""
from __future__ import annotations

from dataclasses import asdict, replace
from typing import Iterable

import numpy as np

from .policy_evaluation import evaluate_policy
from .publication_protocol import EvaluationState, FROZEN_PROTOCOL_V1

POLICIES = (
    "B0_FIXED",
    "B1_COMM_ONLY",
    "B2_SENSING_ONLY",
    "B3_DETERMINISTIC_JOINT",
    "B4_ROBUST_JOINT",
    "ORACLE",
)


def benchmark_states(seed: int) -> tuple[EvaluationState, ...]:
    """Sparse, predeclared paired design spanning easy, boundary and stress regimes."""
    rows = (
        # nominal short-range
        (8, -20, 10, 0, 0, None, 0.0, 0.0),
        (8, -20, 10, 10, 500, None, 0.0, 0.5),
        # high mobility / residual CFO
        (8, -20, 20, 30, 2000, None, 0.001, 1.0),
        (12, -20, 20, 50, 5000, None, 0.001, 1.0),
        # communication-limited
        (0, -10, 10, 3, 1000, 0, 0.001, 1.0),
        (-4, -10, 10, 3, 2000, 10, 0.01, 2.0),
        # range/velocity physics boundaries
        (12, -10, 20, 10, 0, None, 0.0, 0.5),
        (12, -10, 30, 30, 500, None, 0.0, 0.5),
        (12, -10, 50, 30, 500, -10, 0.001, 1.0),
        # interference/synchronization stress
        (12, -5, 20, 10, 5000, 10, 0.01, 2.0),
        (16, 0, 20, 30, 2000, 0, 0.001, 1.0),
        (16, 10, 40, 30, 1000, None, 0.0, 0.5),
    )
    return tuple(EvaluationState(*x, seed=seed) for x in rows)


def run_paired_benchmark(
    seeds: Iterable[int],
    *,
    comm_bits: int = 20_000,
    sensing_trials: int = 3,
) -> list[dict]:
    records: list[dict] = []
    for seed in seeds:
        for scenario_id, state in enumerate(benchmark_states(int(seed))):
            for policy in POLICIES:
                out = evaluate_policy(policy, state, comm_bits=comm_bits, sensing_trials=sensing_trials)
                records.append({
                    "scenario_id": scenario_id,
                    "state": asdict(state),
                    **out,
                })
    return records


def aggregate_policy_metrics(records: list[dict]) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for policy in POLICIES:
        rows = [r for r in records if r["policy"] == policy]
        if not rows:
            continue
        joint = np.asarray([float(r.get("joint_qos", False)) for r in rows])
        outage = np.asarray([float(r.get("outage", True)) for r in rows])
        costs = np.asarray([
            float(r["normalized_resource_cost"])
            for r in rows
            if "normalized_resource_cost" in r
        ])
        result[policy] = {
            "n": len(rows),
            "joint_qos_probability": float(np.mean(joint)),
            "violation_probability": float(np.mean(outage)),
            "mean_normalized_resource_cost_when_selected": float(np.mean(costs)) if costs.size else None,
            "selection_rate": float(costs.size / len(rows)),
        }
    return result


def paired_bootstrap_difference(
    records: list[dict],
    policy_a: str,
    policy_b: str,
    *,
    metric: str = "joint_qos",
    confidence: float | None = None,
    n_resamples: int | None = None,
    seed: int = 20260905,
) -> dict:
    """Paired bootstrap over identical (seed, scenario) units."""
    confidence = confidence or FROZEN_PROTOCOL_V1.bootstrap_confidence
    n_resamples = n_resamples or FROZEN_PROTOCOL_V1.bootstrap_resamples
    key = lambda r: (r["state"]["seed"], r["scenario_id"])
    a = {key(r): float(r.get(metric, 0.0)) for r in records if r["policy"] == policy_a}
    b = {key(r): float(r.get(metric, 0.0)) for r in records if r["policy"] == policy_b}
    common = sorted(set(a) & set(b))
    if not common:
        raise ValueError("no paired observations")
    diffs = np.asarray([a[k] - b[k] for k in common], dtype=float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, diffs.size, size=(n_resamples, diffs.size))
    boots = np.mean(diffs[idx], axis=1)
    alpha = 1.0 - confidence
    lo, hi = np.quantile(boots, [alpha / 2.0, 1.0 - alpha / 2.0])
    return {
        "policy_a": policy_a,
        "policy_b": policy_b,
        "metric": metric,
        "n_pairs": int(diffs.size),
        "mean_paired_difference": float(np.mean(diffs)),
        "confidence": float(confidence),
        "ci_low": float(lo),
        "ci_high": float(hi),
        "bootstrap_resamples": int(n_resamples),
    }


def run_e6_e12_smoke() -> dict:
    """Fast deterministic smoke bundle; not final paper statistics."""
    seeds = range(FROZEN_PROTOCOL_V1.final_seed_start, FROZEN_PROTOCOL_V1.final_seed_start + 2)
    records = run_paired_benchmark(seeds, comm_bits=2_000, sensing_trials=1)
    return {
        "evidence_class": "SMOKE_SIMULATION_NOT_FINAL_PAPER_RESULT",
        "protocol_id": FROZEN_PROTOCOL_V1.protocol_id,
        "records": records,
        "aggregate": aggregate_policy_metrics(records),
        "paired_B4_minus_B3_joint_qos": paired_bootstrap_difference(
            records,
            "B4_ROBUST_JOINT",
            "B3_DETERMINISTIC_JOINT",
            n_resamples=500,
        ),
    }
