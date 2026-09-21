#!/usr/bin/env python3
"""Run frozen publication-v2.1 E9 feasible-region slices and E11 ablations."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from pcfmcw_isac.publication_benchmark import benchmark_states
from pcfmcw_isac.publication_benchmark_v2_1 import (
    feasible_region_slice_v2_1,
    run_e11_ablations_v2_1,
)
from pcfmcw_isac.publication_protocol import EvaluationState


def base_state() -> EvaluationState:
    return EvaluationState(
        ebn0_db=12.0,
        if_snr_db=0.0,
        range_m=20.0,
        radial_velocity_mps=10.0,
        residual_cfo_hz=1000.0,
        inr_db=None,
        phase_noise_std_rad_per_sample=0.001,
        state_uncertainty_scale=1.0,
        seed=10000,
    )


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--output", default="artifacts/publication/v2_1_e9_e11.json")
    args = p.parse_args()
    seeds = range(10000, 10020)
    base = base_state()
    e9 = {
        "ebn0_vs_velocity": feasible_region_slice_v2_1(
            axis_x="ebn0_db",
            values_x=(-4, 0, 4, 8, 12, 16),
            axis_y="radial_velocity_mps",
            values_y=(-50, -30, -10, 0, 10, 30, 50),
            base_state=base,
            seeds=seeds,
            robust_draws=256,
        ),
        "cfo_vs_inr": feasible_region_slice_v2_1(
            axis_x="residual_cfo_hz",
            values_x=(0, 500, 1000, 2000, 5000),
            axis_y="inr_db",
            values_y=(-10, 0, 10),
            base_state=base,
            seeds=seeds,
            robust_draws=256,
        ),
        "if_snr_vs_range": feasible_region_slice_v2_1(
            axis_x="if_snr_db",
            values_x=(-10, -5, 0, 5, 10, 15, 20),
            axis_y="range_m",
            values_y=(5, 10, 20, 30, 40, 50),
            base_state=base,
            seeds=seeds,
            robust_draws=256,
        ),
    }
    ablation_states = []
    for seed in seeds:
        ablation_states.extend(benchmark_states(seed))
    e11 = run_e11_ablations_v2_1(
        ablation_states,
        comm_bits=5000,
        sensing_trials=1,
        robust_draws=256,
    )
    out = {
        "evidence_class": "FROZEN_PUBLICATION_V2_1_E9_E11_SIMULATION_NOT_HARDWARE_MEASUREMENT",
        "protocol_id": "pcfmcw_isac_paper_v2_1",
        "e9": e9,
        "e11": e11,
    }
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, sort_keys=True))
    print(json.dumps({"output": str(path), "e11_records": len(e11)}, indent=2))


if __name__ == "__main__":
    main()
