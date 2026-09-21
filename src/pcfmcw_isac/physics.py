from __future__ import annotations

from math import erfc, log2, sqrt
from .models import PhyConfig, State


def effective_snr_linear(state: State, cfg: PhyConfig) -> float:
    """Auditable surrogate SINR including interference and implementation loss.

    This is a protocol-development model, not yet a publication-grade waveform
    receiver. Its assumptions must be replaced/validated before physical claims.
    """
    signal = 10.0 ** (state.snr_db / 10.0) * cfg.tx_power_scale
    interference = 10.0 ** (state.interference_db / 10.0)
    sync_loss = 1.0 + (abs(state.cfo_hz) / 1000.0) ** 2 + state.phase_noise_std_rad**2 * 25.0
    return signal / ((1.0 + interference) * sync_loss)


def dbpsk_ber(state: State, cfg: PhyConfig) -> float:
    gamma = effective_snr_linear(state, cfg)
    processing = max(1.0, sqrt(cfg.code_length * cfg.repetitions) / 2.0)
    return min(0.5, 0.5 * erfc(sqrt(max(gamma * processing, 0.0))))


def effective_rate_mbps(state: State, cfg: PhyConfig) -> float:
    gamma = effective_snr_linear(state, cfg)
    raw = log2(1.0 + gamma)
    overhead = cfg.repetitions * (1.0 + cfg.code_length / 128.0)
    return raw / overhead


def range_rmse_m(state: State, cfg: PhyConfig) -> float:
    gamma = max(effective_snr_linear(state, cfg), 1e-12)
    return 1.5 / sqrt(gamma * max(cfg.chirps, 1))


def velocity_rmse_mps(state: State, cfg: PhyConfig) -> float:
    gamma = max(effective_snr_linear(state, cfg), 1e-12)
    doppler_stress = 1.0 + abs(state.doppler_hz) / 5000.0
    return 1.0 * doppler_stress / sqrt(gamma * max(cfg.chirps, 1))
