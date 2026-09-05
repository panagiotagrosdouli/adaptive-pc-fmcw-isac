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
    run_extended_ablations,
    run_impairment_stress,
    run_model_mismatch,
    run_physical_pareto,
    run_physics_only_maps,
    run_runtime_benchmark,
    run_same_seed_policy_check,
    run_uncertainty_sweep,
)


def _json_safe(value: Any) -> Any:
    """Recursively convert non-finite floats to JSON null.

    Physically infeasible actions intentionally use +/-inf internally for
    unbounded sensing errors.  Publication artifacts must remain standards-
    compliant JSON, so non-finite diagnostic sentinels are represented as null
    at serialization time rather than changing the underlying simulation model.
    """
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--experiment", required=True, choices=(
        "same-seed", "uncertainty", "stress", "physics", "pareto", "ablations", "mismatch", "runtime", "all-smoke"
    ))
    p.add_argument("--seed-start", type=int, default=10000)
    p.add_argument("--n-seeds", type=int, default=20)
    p.add_argument("--comm-bits", type=int, default=5000)
    p.add_argument("--sensing-trials", type=int, default=1)
    p.add_argument("--robust-draws", type=int, default=256)
    p.add_argument("--output", required=True)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    seeds = range(args.seed_start, args.seed_start + args.n_seeds)
    common = dict(seeds=seeds, comm_bits=args.comm_bits, sensing_trials=args.sensing_trials, robust_draws=args.robust_draws)
    if args.experiment == "same-seed":
        payload = run_same_seed_policy_check(**common)
    elif args.experiment == "uncertainty":
        payload = run_uncertainty_sweep(**common)
    elif args.experiment == "stress":
        payload = run_impairment_stress(**common)
    elif args.experiment == "physics":
        payload = run_physics_only_maps()
    elif args.experiment == "pareto":
        payload = run_physical_pareto(**common)
    elif args.experiment == "ablations":
        payload = run_extended_ablations(**common)
    elif args.experiment == "mismatch":
        payload = run_model_mismatch(**common)
    elif args.experiment == "runtime":
        payload = run_runtime_benchmark(seeds=seeds)
    else:
        smoke_common = dict(seeds=range(args.seed_start, args.seed_start + min(args.n_seeds, 2)), comm_bits=min(args.comm_bits, 2000), sensing_trials=1, robust_draws=min(args.robust_draws, 64))
        payload = {
            "same_seed": run_same_seed_policy_check(**smoke_common),
            "uncertainty": run_uncertainty_sweep(**smoke_common),
            "stress": run_impairment_stress(**smoke_common),
            "physics": run_physics_only_maps(),
            "pareto": run_physical_pareto(**smoke_common),
            "ablations": run_extended_ablations(**smoke_common),
            "mismatch": run_model_mismatch(**smoke_common),
            "runtime": run_runtime_benchmark(seeds=range(args.seed_start, args.seed_start + 1), robust_draws_values=(32, 64), repetitions=1),
        }
    envelope = {
        "evidence_class": "SUPPLEMENTAL_PUBLICATION_V2_1_SIMULATION_NOT_HARDWARE_MEASUREMENT",
        "frozen_parent_protocol": "pcfmcw_isac_paper_v2_1",
        "experiment": args.experiment,
        "seed_start": args.seed_start,
        "n_seeds": args.n_seeds,
        "comm_bits": args.comm_bits,
        "sensing_trials": args.sensing_trials,
        "robust_draws": args.robust_draws,
        "results": payload,
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(_json_safe(envelope), indent=2, allow_nan=False))
    print(out)


if __name__ == "__main__":
    main()
