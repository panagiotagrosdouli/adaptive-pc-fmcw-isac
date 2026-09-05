#!/usr/bin/env python3
"""Aggregate frozen publication-v2.1 shards and compute paired statistics."""
from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

from pcfmcw_isac.publication_benchmark import paired_bootstrap_difference
from pcfmcw_isac.publication_benchmark_v2 import aggregate_policy_metrics_v2, pareto_front
from pcfmcw_isac.publication_benchmark_v2_1 import POLICIES_V2_1
from pcfmcw_isac.statistics import wilson_lower_bound


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--glob", dest="pattern", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()

    files = sorted(glob.glob(args.pattern, recursive=True))
    if not files:
        raise SystemExit(f"no shard files matched {args.pattern!r}")

    records = []
    seed_ranges = []
    for name in files:
        data = json.loads(Path(name).read_text())
        if data.get("protocol_id") != "pcfmcw_isac_paper_v2_1":
            raise SystemExit(f"wrong protocol in {name}")
        records.extend(data["records"])
        seed_ranges.append((data["seed_start"], data["n_seeds"]))

    aggregate = aggregate_policy_metrics_v2(records)
    reliability_bounds = {}
    for policy in POLICIES_V2_1:
        rows = [r for r in records if r["policy"] == policy]
        successes = sum(bool(r.get("joint_qos", False)) for r in rows)
        selected = [r for r in rows if r.get("selected_action") is not None]
        selected_successes = sum(bool(r.get("joint_qos", False)) for r in selected)
        reliability_bounds[policy] = {
            "unconditional_successes": successes,
            "unconditional_trials": len(rows),
            "unconditional_wilson_lower_95": wilson_lower_bound(successes, len(rows), confidence=0.95),
            "conditional_successes": selected_successes,
            "conditional_trials": len(selected),
            "conditional_wilson_lower_95": (
                wilson_lower_bound(selected_successes, len(selected), confidence=0.95)
                if selected else None
            ),
        }

    paired_b4_b3 = paired_bootstrap_difference(
        records, "B4_ROBUST_JOINT", "B3_DETERMINISTIC_JOINT",
        n_resamples=10000, confidence=0.95, seed=20260905,
    )
    paired_b4_b0 = paired_bootstrap_difference(
        records, "B4_ROBUST_JOINT", "B0_FIXED",
        n_resamples=10000, confidence=0.95, seed=20260906,
    )

    oracle_q = aggregate["ORACLE"]["joint_qos_probability_unconditional"]
    deployable_best = max(
        aggregate[p]["joint_qos_probability_unconditional"]
        for p in POLICIES_V2_1 if p != "ORACLE"
    )
    b1 = aggregate["B1_COMM_ONLY"]
    b3 = aggregate["B3_DETERMINISTIC_JOINT"]
    distinguishable = (
        b1["selection_rate"] != b3["selection_rate"]
        or b1["joint_qos_probability_unconditional"] != b3["joint_qos_probability_unconditional"]
        or b1["mean_normalized_resource_cost_when_selected"] != b3["mean_normalized_resource_cost_when_selected"]
    )
    sanity_gate = {
        "oracle_not_below_best_deployable": bool(oracle_q >= deployable_best),
        "b1_b3_are_distinguishable": bool(distinguishable),
        "b4_superiority_over_b3_supported": bool(paired_b4_b3["ci_low"] > 0.0),
        "paper_ready_structural_gate": bool(oracle_q >= deployable_best and distinguishable),
    }

    out = {
        "evidence_class": "FROZEN_PUBLICATION_V2_1_SIMULATION_CANDIDATE_NOT_HARDWARE_MEASUREMENT",
        "protocol_id": "pcfmcw_isac_paper_v2_1",
        "shard_files": files,
        "seed_ranges": seed_ranges,
        "n_records": len(records),
        "aggregate": aggregate,
        "reliability_bounds": reliability_bounds,
        "paired_B4_minus_B3_joint_qos": paired_b4_b3,
        "paired_B4_minus_B0_joint_qos": paired_b4_b0,
        "pareto_B4": pareto_front(records, "B4_ROBUST_JOINT"),
        "sanity_gate": sanity_gate,
        "records": records,
    }
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, sort_keys=True))
    print(json.dumps({
        "output": str(path),
        "n_records": len(records),
        "sanity_gate": sanity_gate,
        "paired_B4_minus_B3_joint_qos": paired_b4_b3,
    }, indent=2))


if __name__ == "__main__":
    main()
