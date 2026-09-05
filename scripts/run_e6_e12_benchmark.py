#!/usr/bin/env python3
"""Run paired B0-B4+Oracle benchmark and write machine-readable JSON."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from pcfmcw_isac.publication_benchmark import (
    aggregate_policy_metrics,
    paired_bootstrap_difference,
    run_paired_benchmark,
)
from pcfmcw_isac.publication_protocol import FROZEN_PROTOCOL_V1


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="artifacts/publication/e6_e12_benchmark.json")
    parser.add_argument("--n-seeds", type=int, default=10)
    parser.add_argument("--comm-bits", type=int, default=20_000)
    parser.add_argument("--sensing-trials", type=int, default=3)
    args = parser.parse_args()

    if args.n_seeds <= 0 or args.n_seeds > FROZEN_PROTOCOL_V1.n_final_seeds:
        raise ValueError("n-seeds must be in [1, frozen n_final_seeds]")

    seeds = range(
        FROZEN_PROTOCOL_V1.final_seed_start,
        FROZEN_PROTOCOL_V1.final_seed_start + args.n_seeds,
    )
    records = run_paired_benchmark(
        seeds,
        comm_bits=args.comm_bits,
        sensing_trials=args.sensing_trials,
    )
    result = {
        "evidence_class": "SIMULATION_BENCHMARK_NOT_HARDWARE_MEASUREMENT",
        "protocol_id": FROZEN_PROTOCOL_V1.protocol_id,
        "n_seeds": args.n_seeds,
        "records": records,
        "aggregate": aggregate_policy_metrics(records),
        "paired_B4_minus_B3_joint_qos": paired_bootstrap_difference(
            records,
            "B4_ROBUST_JOINT",
            "B3_DETERMINISTIC_JOINT",
        ),
    }

    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(path)


if __name__ == "__main__":
    main()
