"""Complex-baseband propagation and impairment models for PC-FMCW ISAC."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np

C0 = 299_792_458.0

@dataclass(frozen=True)
class ChannelState:
    range_m: float = 50.0
    radial_velocity_mps: float = 0.0
    snr_db: float = 20.0
    cfo_hz: float = 0.0
    phase_noise_std_rad: float = 0.0
    interference_to_noise_db: float | None = None
    timing_offset_samples: int = 0

    def validate(self) -> None:
        if self.range_m < 0:
            raise ValueError("range_m must be non-negative")
        if self.phase_noise_std_rad < 0:
            raise ValueError("phase_noise_std_rad must be non-negative")


def apply_delay_doppler(x: np.ndarray, sample_rate_hz: float, carrier_hz: float,
                        state: ChannelState) -> np.ndarray:
    """Apply integer sample delay and narrowband Doppler to a flattened signal."""
    state.validate()
    s = np.asarray(x, dtype=complex).reshape(-1)
    geometric_delay = int(round((2.0 * state.range_m / C0) * sample_rate_hz))
    delay = max(0, geometric_delay + state.timing_offset_samples)
    y = np.zeros_like(s)
    if delay < s.size:
        y[delay:] = s[: s.size - delay]
    fd = 2.0 * state.radial_velocity_mps * carrier_hz / C0
    t = np.arange(s.size) / sample_rate_hz
    return y * np.exp(1j * 2.0 * np.pi * (fd + state.cfo_hz) * t)


def add_phase_noise(x: np.ndarray, std_rad: float, rng: np.random.Generator) -> np.ndarray:
    if std_rad <= 0:
        return np.asarray(x, dtype=complex)
    increments = rng.normal(0.0, std_rad, size=np.asarray(x).size)
    phase = np.cumsum(increments)
    return np.asarray(x, dtype=complex) * np.exp(1j * phase)


def add_awgn(x: np.ndarray, snr_db: float, rng: np.random.Generator) -> np.ndarray:
    s = np.asarray(x, dtype=complex)
    p = float(np.mean(np.abs(s) ** 2))
    if p <= 0:
        return s.copy()
    noise_power = p / (10.0 ** (snr_db / 10.0))
    sigma = np.sqrt(noise_power / 2.0)
    n = sigma * (rng.standard_normal(s.shape) + 1j * rng.standard_normal(s.shape))
    return s + n


def add_interference(x: np.ndarray, inr_db: float | None, rng: np.random.Generator) -> np.ndarray:
    s = np.asarray(x, dtype=complex)
    if inr_db is None:
        return s.copy()
    p = float(np.mean(np.abs(s) ** 2))
    ip = p * 10.0 ** (inr_db / 10.0)
    q = np.exp(1j * rng.uniform(-np.pi, np.pi, size=s.shape))
    return s + np.sqrt(ip) * q


def propagate(x: np.ndarray, sample_rate_hz: float, carrier_hz: float,
              state: ChannelState, rng: np.random.Generator) -> np.ndarray:
    y = apply_delay_doppler(x, sample_rate_hz, carrier_hz, state)
    y = add_phase_noise(y, state.phase_noise_std_rad, rng)
    y = add_interference(y, state.interference_to_noise_db, rng)
    return add_awgn(y, state.snr_db, rng)
