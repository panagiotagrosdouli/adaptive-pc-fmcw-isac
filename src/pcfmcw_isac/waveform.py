"""Normalized complex-baseband PC-FMCW waveform primitives.

Stage 1 deliberately separates waveform generation from propagation and receiver
processing.  RF carrier sampling is not attempted; carrier-dependent Doppler is
represented explicitly by the channel model.
"""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class WaveformConfig:
    bandwidth_hz: float = 200e6
    chirp_duration_s: float = 40e-6
    sample_rate_hz: float = 10e6
    n_chirps: int = 64
    tx_power: float = 1.0

    def validate(self) -> None:
        if self.bandwidth_hz <= 0 or self.chirp_duration_s <= 0:
            raise ValueError("bandwidth and chirp duration must be positive")
        if self.sample_rate_hz <= 0 or self.n_chirps < 2 or self.tx_power <= 0:
            raise ValueError("sample rate/power must be positive and n_chirps >= 2")
        if self.samples_per_chirp < 8:
            raise ValueError("at least eight fast-time samples per chirp are required")

    @property
    def samples_per_chirp(self) -> int:
        return int(round(self.sample_rate_hz * self.chirp_duration_s))

    @property
    def slope_hz_per_s(self) -> float:
        return self.bandwidth_hz / self.chirp_duration_s


def differential_bpsk_phases(bits: np.ndarray, initial_phase: float = 0.0) -> np.ndarray:
    """Map N-1 binary information bits to N differential chirp phases."""
    b = np.asarray(bits, dtype=int).reshape(-1)
    if np.any((b != 0) & (b != 1)):
        raise ValueError("bits must be binary")
    phases = np.empty(b.size + 1, dtype=float)
    phases[0] = initial_phase
    increments = np.where(b == 0, 0.0, np.pi)
    phases[1:] = initial_phase + np.cumsum(increments)
    return np.mod(phases + np.pi, 2 * np.pi) - np.pi


def generate_pc_fmcw(cfg: WaveformConfig, phases: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Generate [chirp, fast-time] normalized complex-baseband samples."""
    cfg.validate()
    p = np.asarray(phases, dtype=float).reshape(-1)
    if p.size != cfg.n_chirps:
        raise ValueError("one phase value is required per chirp")
    t = np.arange(cfg.samples_per_chirp, dtype=float) / cfg.sample_rate_hz
    chirp_phase = np.pi * cfg.slope_hz_per_s * t**2
    signal = np.sqrt(cfg.tx_power) * np.exp(1j * (chirp_phase[None, :] + p[:, None]))
    return t, signal


def differential_decode(chirp_phasors: np.ndarray) -> np.ndarray:
    """Hard-decode DBPSK information from one complex phasor per chirp."""
    z = np.asarray(chirp_phasors, dtype=complex).reshape(-1)
    if z.size < 2:
        raise ValueError("at least two chirp phasors are required")
    products = z[1:] * np.conj(z[:-1])
    return (np.real(products) < 0.0).astype(int)
