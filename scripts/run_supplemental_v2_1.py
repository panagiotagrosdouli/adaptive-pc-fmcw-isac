#!/usr/bin/env python3
"""Run reviewer-grade supplemental publication-v2.1 experiments.

These experiments are supplemental to, and do not replace, the immutable frozen
v2.1 benchmark. Outputs are simulation/analytical evidence, not measurements.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from pcfmcw_isac.supplemental_evidence_v2_1 import (
    run_extended_ablations, run_impairment_stress, run_model_mismatch,
    run_physical_pareto, run_physics_only_maps, run_runtime_benchmark,
    run_same_seed_policy_check, run_uncertainty_sweep,
)
from pcfmcw_isac.part_b_completion import (
    run_confidence_maps, run_full_metric_table, run_reliability_target_sweep,
    run_uncertainty_source_ablations,
)


def _json_safe(value: Any) -> Any:
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, dict): return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)): return [_json_safe(item) for item in value]
    return value


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--experiment", required=True, choices=(
        "same-seed", "uncertainty", "stress", "physics", "pareto", "ablations", "mismatch", "runtime",
        "full-metrics", "reliability-targets", "confidence-maps", "uncertainty-sources", "all-smoke"
    ))
    p.add_argument("--seed-start", type=int, default=10000)
    p.add_argument("--n-seeds", type=int, default=20)
    p.add_argument("--comm-bits", type=int, default=5000)
    p.add_argument("--sensing-trials", type=int, default=1)
    p.add_argument("--robust-draws", type=int, default=256)
    p.add_argument("--output", required=True)
    return p.parse_args()


def main() -> None:
    args = parse_args(); seeds = range(args.seed_start, args.seed_start + args.n_seeds)
    common = dict(seeds=seeds, comm_bits=args.comm_bits, sensing_trials=args.sensing_trials, robust_draws=args.robust_draws)
    runners = {
        "same-seed": run_same_seed_policy_check, "uncertainty": run_uncertainty_sweep,
        "stress": run_impairment_stress, "pareto": run_physical_pareto,
        "ablations": run_extended_ablations, "mismatch": run_model_mismatch,
        "full-metrics": run_full_metric_table, "reliability-targets": run_reliability_target_sweep,
        "confidence-maps": run_confidence_maps, "uncertainty-sources": run_uncertainty_source_ablations,
    }
    if args.experiment == "physics": payload = run_physics_only_maps()
    elif args.experiment == "runtime": payload = run_runtime_benchmark(seeds=seeds)
    elif args.experiment in runners: payload = runners[args.experiment](**common)
    else:
        smoke_common = dict(seeds=range(args.seed_start, args.seed_start + min(args.n_seeds, 2)), comm_bits=min(args.comm_bits, 1000), sensing_trials=1, robust_draws=min(args.robust_draws, 32))
        payload = {name: fn(**smoke_common) for name, fn in runners.items()}
        payload["physics"] = run_physics_only_maps()
        payload["runtime"] = run_runtime_benchmark(seeds=range(args.seed_start, args.seed_start + 1), robust_draws_values=(32,), repetitions=1)
    envelope = {
        "evidence_class": "SUPPLEMENTAL_PUBLICATION_V2_1_SIMULATION_NOT_HARDWARE_MEASUREMENT",
        "frozen_parent_protocol": "pcfmcw_isac_paper_v2_1", "experiment": args.experiment,
        "seed_start": args.seed_start, "n_seeds": args.n_seeds, "comm_bits": args.comm_bits,
        "sensing_trials": args.sensing_trials, "robust_draws": args.robust_draws, "results": payload,
    }
    out = Path(args.output); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(_json_safe(envelope), indent=2, allow_nan=False)); print(out)


if __name__ == "__main__": main()
