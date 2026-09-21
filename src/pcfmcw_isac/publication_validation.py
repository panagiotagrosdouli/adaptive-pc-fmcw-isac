"""Executable E1-E5 validation for the frozen PC-FMCW publication protocol.

The functions in this module generate simulation evidence only. They do not
represent hardware measurements. Every experiment is deterministic for a given
seed and uses the frozen protocol ranges defined in publication_protocol.py.
"""
from __future__ import annotations

from dataclasses import asdict
from math import sqrt
from typing import Iterable

import numpy as np

from .comm_reference import CommConfig, dbpsk_awgn_theory, differential_decode, differential_encode, simulate_ber
from .if_model import Target, estimate_single_target, synthesize_if
from .profiles import high_mobility_profile, short_range_profile
from .publication_protocol import FROZEN_PROTOCOL_V1


def profile_registry():
    return {
        "ti_77ghz_parking_profile": short_range_profile(),
        "ti_77ghz_high_mobility_capability_profile": high_mobility_profile(),
    }


def _comm_cfg(profile_name: str, chips_per_chirp: int) -> CommConfig:
    p = profile_registry()[profile_name]
    return CommConfig(
        chirp_duration_s=p.chirp_duration_s,
        chirp_repetition_s=p.chirp_repetition_s,
        chips_per_chirp=chips_per_chirp,
        n_chirps=p.n_chirps,
    )


def simulate_dbpsk_impaired(
    ebn0_db: float,
    n_bits: int,
    *,
    cfg: CommConfig,
    residual_frequency_hz: float = 0.0,
    phase_noise_std_rad_per_chip: float = 0.0,
    inr_db: float | None = None,
    seed: int = 0,
) -> float:
    """DBPSK BER with controlled residual CFO, random-walk phase noise and INR.

    Interference is normalized relative to thermal-noise power, so ``inr_db``
    is genuinely interference-to-noise ratio. The phase-noise parameter is a
    controlled random-walk innovation standard deviation per chip; it is not
    inferred from a hardware dBc/Hz specification.
    """
    cfg.validate()
    if n_bits <= 0:
        raise ValueError("n_bits must be positive")
    if phase_noise_std_rad_per_chip < 0:
        raise ValueError("phase-noise standard deviation must be non-negative")

    rng = np.random.default_rng(seed)
    bits = rng.integers(0, 2, size=n_bits, dtype=int)
    s = differential_encode(bits)

    idx = np.arange(s.size)
    chirp_index = idx // cfg.chips_per_chirp
    within = idx % cfg.chips_per_chirp
    t = chirp_index * cfg.chirp_repetition_s + within * cfg.chip_duration_s
    y = s * np.exp(1j * 2.0 * np.pi * residual_frequency_hz * t)

    if phase_noise_std_rad_per_chip > 0:
        dphi = rng.normal(0.0, phase_noise_std_rad_per_chip, size=s.size)
        y = y * np.exp(1j * np.cumsum(dphi))

    gamma = 10.0 ** (ebn0_db / 10.0)
    n0 = 1.0 / gamma
    sigma_n = np.sqrt(n0 / 2.0)
    noise = sigma_n * (rng.standard_normal(s.size) + 1j * rng.standard_normal(s.size))

    if inr_db is not None:
        interference_power = n0 * 10.0 ** (inr_db / 10.0)
        sigma_i = np.sqrt(interference_power / 2.0)
        interference = sigma_i * (
            rng.standard_normal(s.size) + 1j * rng.standard_normal(s.size)
        )
    else:
        interference = 0.0

    bhat = differential_decode(y + noise + interference)
    return float(np.mean(bhat != bits))


def e1_waveform_sanity() -> dict:
    """Analytical profile quantities used as physical invariants."""
    result = {}
    for name, p in profile_registry().items():
        p.validate()
        result[name] = {
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
    return result


def e2_communication_awgn(
    *,
    ebn0_db: Iterable[float] | None = None,
    chips_per_chirp: Iterable[int] = (16, 32, 64),
    n_bits: int = 200_000,
    seed: int = 10_001,
) -> list[dict]:
    """Monte-Carlo DBPSK BER versus the analytical AWGN reference."""
    if ebn0_db is None:
        ebn0_db = FROZEN_PROTOCOL_V1.ebn0_db
    rows = []
    for chips in chips_per_chirp:
        cfg = _comm_cfg("ti_77ghz_parking_profile", chips)
        for x in ebn0_db:
            sim = simulate_ber(float(x), n_bits, cfg=cfg, seed=seed + chips + int(round(10*x)))
            theory = float(dbpsk_awgn_theory(float(x)))
            rows.append({
                "chips_per_chirp": chips,
                "ebn0_db": float(x),
                "simulated_ber": sim,
                "analytical_ber": theory,
                "absolute_error": abs(sim - theory),
                "raw_bit_rate_bps": cfg.raw_bit_rate_bps,
                "n_bits": n_bits,
            })
    return rows


def e3_sensing_single_target(
    *,
    seeds: Iterable[int] = range(10_000, 10_020),
    if_snr_db: Iterable[float] = (-30.0, -25.0, -20.0, -10.0),
) -> list[dict]:
    """Single-target range/velocity RMSE on physically feasible profile states."""
    cases = [
        ("ti_77ghz_parking_profile", 10.0, 3.0),
        ("ti_77ghz_high_mobility_capability_profile", 20.28, 19.8564),
    ]
    profiles = profile_registry()
    rows = []
    for name, r_true, v_true in cases:
        p = profiles[name]
        for snr in if_snr_db:
            r_err = []
            v_err = []
            for seed in seeds:
                rng = np.random.default_rng(seed)
                y = synthesize_if(p, [Target(r_true, v_true)], snr_db=float(snr), rng=rng)
                r_hat, v_hat = estimate_single_target(p, y)
                r_err.append(r_hat - r_true)
                v_err.append(v_hat - v_true)
            rows.append({
                "profile_name": name,
                "if_snr_db": float(snr),
                "target_range_m": r_true,
                "target_velocity_mps": v_true,
                "range_rmse_m": sqrt(float(np.mean(np.square(r_err)))),
                "velocity_rmse_mps": sqrt(float(np.mean(np.square(v_err)))),
                "range_resolution_m": p.range_resolution_m,
                "velocity_resolution_mps": p.velocity_resolution_mps,
                "n_trials": len(r_err),
            })
    return rows


def e4_residual_cfo_stress(
    *,
    ebn0_db: float = 8.0,
    chips_per_chirp: int = 32,
    n_bits: int = 200_000,
    seed: int = 10_101,
) -> list[dict]:
    cfg = _comm_cfg("ti_77ghz_parking_profile", chips_per_chirp)
    rows = []
    for cfo in FROZEN_PROTOCOL_V1.residual_cfo_hz:
        ber = simulate_dbpsk_impaired(
            ebn0_db,
            n_bits,
            cfg=cfg,
            residual_frequency_hz=float(cfo),
            seed=seed + int(cfo),
        )
        rows.append({
            "ebn0_db": ebn0_db,
            "chips_per_chirp": chips_per_chirp,
            "residual_cfo_hz": float(cfo),
            "ber": ber,
            "n_bits": n_bits,
        })
    return rows


def e5_phase_noise_interference_stress(
    *,
    ebn0_db: float = 8.0,
    chips_per_chirp: int = 32,
    n_bits: int = 100_000,
    seed: int = 10_501,
) -> list[dict]:
    """Controlled sensitivity sweep; phase-noise values are not hardware-calibrated."""
    cfg = _comm_cfg("ti_77ghz_parking_profile", chips_per_chirp)
    rows = []
    for pn in FROZEN_PROTOCOL_V1.phase_noise_std_rad_per_sample:
        for inr in FROZEN_PROTOCOL_V1.inr_db:
            ber = simulate_dbpsk_impaired(
                ebn0_db,
                n_bits,
                cfg=cfg,
                phase_noise_std_rad_per_chip=float(pn),
                inr_db=inr,
                seed=seed + int(round(pn * 1e6)) + (0 if inr is None else int(inr + 20)),
            )
            rows.append({
                "ebn0_db": ebn0_db,
                "chips_per_chirp": chips_per_chirp,
                "phase_noise_std_rad_per_chip": float(pn),
                "inr_db": inr,
                "ber": ber,
                "n_bits": n_bits,
                "phase_noise_label": "CONTROLLED_SIMULATION_PARAMETER_NOT_HARDWARE_DERIVED",
            })
    return rows


def run_e1_e5() -> dict:
    """Return one machine-readable validation bundle without inventing results."""
    FROZEN_PROTOCOL_V1.validate()
    return {
        "evidence_class": "SIMULATION_AND_ANALYTICAL_VALIDATION_NOT_MEASUREMENT",
        "protocol_id": FROZEN_PROTOCOL_V1.protocol_id,
        "qos": asdict(FROZEN_PROTOCOL_V1.qos),
        "E1_waveform_sanity": e1_waveform_sanity(),
        "E2_communication_awgn": e2_communication_awgn(),
        "E3_sensing_single_target": e3_sensing_single_target(),
        "E4_residual_cfo_stress": e4_residual_cfo_stress(),
        "E5_phase_noise_interference_stress": e5_phase_noise_interference_stress(),
    }
