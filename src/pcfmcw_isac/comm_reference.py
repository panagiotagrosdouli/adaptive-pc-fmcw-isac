"""Reference communication chain for phase-coded FMCW.

The remote receiver is assumed to remove the known FMCW chirp, leaving the
phase-code sequence at baseband.  Multiple phase-code chips may occupy one
chirp.  This is a transparent reference modem, not a measured modem claim.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class CommConfig:
    chirp_duration_s: float = 25.6e-6
    chirp_repetition_s: float = 115.8e-6
    chips_per_chirp: int = 32
    n_chirps: int = 64

    def validate(self) -> None:
        if self.chips_per_chirp < 2 or self.n_chirps < 1:
            raise ValueError("chips_per_chirp >= 2 and n_chirps >= 1 required")
        if self.chirp_duration_s <= 0 or self.chirp_repetition_s < self.chirp_duration_s:
            raise ValueError("invalid chirp timing")

    @property
    def chip_duration_s(self) -> float:
        return self.chirp_duration_s / self.chips_per_chirp

    @property
    def raw_bit_rate_bps(self) -> float:
        # One differential information bit per phase-code chip after the initial reference.
        return self.chips_per_chirp / self.chirp_repetition_s


def differential_encode(bits: np.ndarray) -> np.ndarray:
    b = np.asarray(bits, dtype=int).reshape(-1)
    if np.any((b != 0) & (b != 1)):
        raise ValueError("bits must be binary")
    s = np.empty(b.size + 1, dtype=complex)
    s[0] = 1.0 + 0.0j
    for k, bit in enumerate(b, start=1):
        s[k] = s[k - 1] * (-1.0 if bit else 1.0)
    return s


def differential_decode(samples: np.ndarray) -> np.ndarray:
    z = np.asarray(samples, dtype=complex).reshape(-1)
    if z.size < 2:
        raise ValueError("at least two samples required")
    return (np.real(z[1:] * np.conj(z[:-1])) < 0.0).astype(int)


def transmit_awgn(bits: np.ndarray, ebn0_db: float, *, residual_frequency_hz: float = 0.0,
                  cfg: CommConfig | None = None, rng: np.random.Generator | None = None) -> np.ndarray:
    """Return noisy dechirped phase-code chip samples.

    The Eb/N0 normalization uses unit-energy DBPSK chip symbols.  A residual
    frequency error rotates the phase continuously over active chips and chirp
    gaps, allowing mobility/synchronization sensitivity studies.
    """
    cfg = cfg or CommConfig()
    cfg.validate()
    rng = rng or np.random.default_rng()
    s = differential_encode(bits)
    total_chips = s.size
    # Map serialized chips to their physical times including the inter-chirp idle gap.
    chip_index = np.arange(total_chips)
    chirp_index = chip_index // cfg.chips_per_chirp
    within = chip_index % cfg.chips_per_chirp
    t = chirp_index * cfg.chirp_repetition_s + within * cfg.chip_duration_s
    y = s * np.exp(1j * 2.0 * np.pi * residual_frequency_hz * t)
    gamma = 10.0 ** (ebn0_db / 10.0)
    n0 = 1.0 / gamma
    sigma = np.sqrt(n0 / 2.0)
    noise = sigma * (rng.standard_normal(total_chips) + 1j * rng.standard_normal(total_chips))
    return y + noise


def simulate_ber(ebn0_db: float, n_bits: int, *, residual_frequency_hz: float = 0.0,
                 cfg: CommConfig | None = None, seed: int = 0) -> float:
    rng = np.random.default_rng(seed)
    bits = rng.integers(0, 2, size=n_bits, dtype=int)
    rx = transmit_awgn(bits, ebn0_db, residual_frequency_hz=residual_frequency_hz, cfg=cfg, rng=rng)
    bhat = differential_decode(rx)
    return float(np.mean(bhat != bits))


def dbpsk_awgn_theory(ebn0_db: float | np.ndarray) -> np.ndarray:
    gamma = 10.0 ** (np.asarray(ebn0_db, dtype=float) / 10.0)
    return 0.5 * np.exp(-gamma)
