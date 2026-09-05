#!/usr/bin/env python3
"""Run one deterministic publication-v2.1 seed shard and write JSON records."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from pcfmcw_isac.publication_benchmark_v2_1 import run_paired_benchmark_v2_1


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--seed-start", type=int, required=True)
    p.add_argument("--n-seeds", type=int, required=True)
    p.add_argument("--comm-bits", type=int, default=20000)
    p.add_argument("--sensing-trials", type=int, default=3)
    p.add_argument("--robust-draws", type=int, default=512)
    p.add_argument("--output", required=True)
    args = p.parse_args()
    if args.n_seeds <= 0:
        raise SystemExit("n-seeds must be positive")
    seeds = range(args.seed_start, args.seed_start + args.n_seeds)
    records = run_paired_benchmark_v2_1(
        seeds,
        comm_bits=args.comm_bits,
        sensing_trials=args.sensing_trials,
        robust_draws=args.robust_draws,
    )
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    bundle = {
        "evidence_class": "FROZEN_PUBLICATION_V2_1_SIMULATION_SHARD_NOT_HARDWARE_MEASUREMENT",
        "protocol_id": "pcfmcw_isac_paper_v2_1",
        "seed_start": args.seed_start,
        "n_seeds": args.n_seeds,
        "comm_bits": args.comm_bits,
        "sensing_trials": args.sensing_trials,
        "robust_draws": args.robust_draws,
        "records": records,
    }
    out.write_text(json.dumps(bundle, sort_keys=True))
    print(json.dumps({"output": str(out), "records": len(records), "seed_start": args.seed_start, "n_seeds": args.n_seeds}, indent=2))


if __name__ == "__main__":
    main()
