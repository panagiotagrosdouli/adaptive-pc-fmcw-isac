#!/usr/bin/env python3
"""Run the Stage-7 literature-grounded validation suite and write JSON evidence."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np

from pcfmcw_isac.if_model import RadarProfile, Target, synthesize_if, estimate_single_target
from pcfmcw_isac.comm_reference import CommConfig, dbpsk_awgn_theory, simulate_ber
from pcfmcw_isac.profiles import short_range_profile, high_mobility_profile

C0 = 299_792_458.0


def profile_dict(p: RadarProfile) -> dict:
    return {
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
    }


def sensing_mc(profile: RadarProfile, target: Target, snr_db: float, trials: int,
               seed: int, range_fft: int, doppler_fft: int) -> dict:
    rng = np.random.default_rng(seed)
    re, ve = [], []
    for _ in range(trials):
        y = synthesize_if(profile, [target], snr_db=snr_db, rng=rng)
        r_hat, v_hat = estimate_single_target(profile, y, range_fft=range_fft, doppler_fft=doppler_fft)
        re.append(r_hat - target.range_m)
        ve.append(v_hat - target.radial_velocity_mps)
    re = np.asarray(re)
    ve = np.asarray(ve)
    return {
        "snr_db": snr_db,
        "trials": trials,
        "range_rmse_m": float(np.sqrt(np.mean(re**2))),
        "velocity_rmse_mps": float(np.sqrt(np.mean(ve**2))),
        "range_bias_m": float(np.mean(re)),
        "velocity_bias_mps": float(np.mean(ve)),
        "within_one_range_resolution": float(np.mean(np.abs(re) <= profile.range_resolution_m)),
        "within_one_velocity_resolution": float(np.mean(np.abs(ve) <= profile.velocity_resolution_mps)),
    }


def comm_awgn(bits: int) -> list[dict]:
    out = []
    for i, eb in enumerate([-2.0, 0.0, 2.0, 4.0, 6.0, 8.0, 10.0]):
        ber = simulate_ber(eb, bits, seed=20265000 + i)
        theory = float(dbpsk_awgn_theory(eb))
        out.append({
            "ebn0_db": eb,
            "bits": bits,
            "ber_sim": ber,
            "ber_theory": theory,
            "absolute_error": abs(ber - theory),
        })
    return out


def residual_frequency_sweep(bits: int, ebn0_db: float = 8.0) -> list[dict]:
    out = []
    for i, f_hz in enumerate([0.0, 100.0, 500.0, 1000.0, 2000.0, 5000.0, 5100.0]):
        out.append({
            "residual_frequency_hz": f_hz,
            "ber": simulate_ber(
                ebn0_db,
                bits,
                residual_frequency_hz=f_hz,
                cfg=CommConfig(chips_per_chirp=32),
                seed=20266000 + i,
            ),
        })
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sensing-trials", type=int, default=100)
    ap.add_argument("--high-mobility-trials", type=int, default=50)
    ap.add_argument("--comm-bits", type=int, default=300_000)
    ap.add_argument("--output", default="artifacts/stage7/literature_validation.json")
    args = ap.parse_args()

    sr = short_range_profile()
    hm = high_mobility_profile()
    sr_target = Target(range_m=10.0, radial_velocity_mps=3.0)
    published_speed = 5100.0 * C0 / 77e9
    hm_target = Target(range_m=20.28, radial_velocity_mps=published_speed)

    sr_snr = [-40.0, -35.0, -30.0, -25.0, -20.0, -15.0, -10.0]
    hm_snr = [-35.0, -30.0, -25.0, -20.0, -15.0, -10.0, 0.0, 10.0]

    short_results = [
        sensing_mc(sr, sr_target, s, args.sensing_trials, 20263000 + i, 2048, 256)
        for i, s in enumerate(sr_snr)
    ]
    high_results = [
        sensing_mc(hm, hm_target, s, args.high_mobility_trials, 20264000 + i, 4096, 512)
        for i, s in enumerate(hm_snr)
    ]

    rates = {
        str(chips): CommConfig(chips_per_chirp=chips).raw_bit_rate_bps
        for chips in (16, 32, 64)
    }

    out = {
        "status": "SIMULATION_EVIDENCE_NOT_MEASUREMENT",
        "source_profiles": {
            "P-SR": profile_dict(sr),
            "P-HM": profile_dict(hm),
        },
        "published_channel_scale_cross_check": {
            "distance_m": 20.28,
            "one_way_doppler_hz": 5100.0,
            "derived_radial_speed_mps_at_77ghz": published_speed,
            "source_waveform_warning": "external benchmark is PMCW-CDMA; channel scale only",
        },
        "communication_raw_bit_rates_bps": rates,
        "short_range_sensing_monte_carlo": short_results,
        "high_mobility_sensing_monte_carlo": high_results,
        "dbpsk_awgn_validation": comm_awgn(args.comm_bits),
        "residual_frequency_sensitivity_at_8db": residual_frequency_sweep(args.comm_bits),
        "claim_boundary": (
            "Hardware/chirp constants are literature-grounded. SNR, Eb/N0 and residual frequency error "
            "are controlled simulation variables. Results are reproducible simulation evidence and are not measured RF results."
        ),
    }
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2) + "\n")
    print(path)


if __name__ == "__main__":
    main()
