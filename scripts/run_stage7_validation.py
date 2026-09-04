#!/usr/bin/env python3
"""Run the Stage-7 literature-grounded validation suite and write JSON evidence."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np

from pcfmcw_isac.if_model import RadarProfile, Target, synthesize_if, estimate_single_target
from pcfmcw_isac.comm_reference import CommConfig, dbpsk_awgn_theory, simulate_ber


def sensing_mc(profile: RadarProfile, snr_db: float, trials: int, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    range_true = 10.0
    velocity_true = 3.0
    re, ve = [], []
    for _ in range(trials):
        y = synthesize_if(
            profile,
            [Target(range_m=range_true, radial_velocity_mps=velocity_true)],
            snr_db=snr_db,
            rng=rng,
        )
        r_hat, v_hat = estimate_single_target(profile, y)
        re.append(r_hat - range_true)
        ve.append(v_hat - velocity_true)
    re = np.asarray(re)
    ve = np.asarray(ve)
    return {
        "snr_db": snr_db,
        "trials": trials,
        "range_rmse_m": float(np.sqrt(np.mean(re**2))),
        "velocity_rmse_mps": float(np.sqrt(np.mean(ve**2))),
        "range_bias_m": float(np.mean(re)),
        "velocity_bias_mps": float(np.mean(ve)),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sensing-trials", type=int, default=100)
    ap.add_argument("--comm-bits", type=int, default=200_000)
    ap.add_argument("--output", default="artifacts/stage7/literature_validation.json")
    args = ap.parse_args()

    p = RadarProfile()
    p.validate()
    snr_grid = [-10.0, -5.0, 0.0, 5.0, 10.0, 15.0, 20.0]
    sensing = [sensing_mc(p, s, args.sensing_trials, 20260905 + i) for i, s in enumerate(snr_grid)]

    ebn0_grid = [-2.0, 0.0, 2.0, 4.0, 6.0, 8.0]
    comm = []
    for i, eb in enumerate(ebn0_grid):
        ber = simulate_ber(eb, args.comm_bits, seed=20261000 + i)
        theory = float(dbpsk_awgn_theory(eb))
        comm.append({
            "ebn0_db": eb,
            "bits": args.comm_bits,
            "ber_sim": ber,
            "ber_theory": theory,
            "absolute_error": abs(ber - theory),
        })

    rates = {
        str(chips): CommConfig(chips_per_chirp=chips).raw_bit_rate_bps
        for chips in (16, 32, 64)
    }

    out = {
        "status": "SIMULATION_EVIDENCE_NOT_MEASUREMENT",
        "profile": {
            "carrier_hz": p.carrier_hz,
            "bandwidth_hz": p.bandwidth_hz,
            "chirp_duration_s": p.chirp_duration_s,
            "chirp_repetition_s": p.chirp_repetition_s,
            "sample_rate_hz": p.sample_rate_hz,
            "samples_per_chirp": p.samples_per_chirp,
            "n_chirps": p.n_chirps,
            "range_resolution_m": p.range_resolution_m,
            "positive_if_max_range_m": p.positive_if_max_range_m,
            "velocity_resolution_mps": p.velocity_resolution_mps,
            "max_unambiguous_velocity_mps": p.max_unambiguous_velocity_mps,
        },
        "communication_raw_bit_rates_bps": rates,
        "sensing_monte_carlo": sensing,
        "dbpsk_awgn_validation": comm,
        "claim_boundary": (
            "Hardware/chirp constants are literature-grounded. SNR and Eb/N0 are controlled simulation "
            "variables. Results are reproducible simulation evidence and are not measured RF results."
        ),
    }
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2) + "\n")
    print(path)


if __name__ == "__main__":
    main()
