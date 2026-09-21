"""Communication and sensing receivers for the PC-FMCW waveform."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from .waveform import WaveformConfig, differential_decode
from .channel import C0

@dataclass(frozen=True)
class SensingEstimate:
    range_m: float
    radial_velocity_mps: float
    range_bin: int
    doppler_bin: int


def dechirp(rx: np.ndarray, tx_reference: np.ndarray) -> np.ndarray:
    r = np.asarray(rx, dtype=complex)
    t = np.asarray(tx_reference, dtype=complex)
    if r.shape != t.shape:
        raise ValueError("rx and tx_reference shapes must match")
    return r * np.conj(t)


def communication_chirp_phasors(rx: np.ndarray, tx_unmodulated: np.ndarray) -> np.ndarray:
    """Matched integrate each chirp to recover differential phase."""
    r = np.asarray(rx, dtype=complex)
    ref = np.asarray(tx_unmodulated, dtype=complex)
    if r.shape != ref.shape or r.ndim != 2:
        raise ValueError("expected matching [chirp, fast-time] arrays")
    return np.sum(r * np.conj(ref), axis=1)


def decode_dbpsk(rx: np.ndarray, unmodulated_reference: np.ndarray) -> np.ndarray:
    return differential_decode(communication_chirp_phasors(rx, unmodulated_reference))


def range_doppler_map(rx: np.ndarray, tx_reference: np.ndarray,
                      range_fft: int | None = None, doppler_fft: int | None = None) -> np.ndarray:
    beat = dechirp(rx, tx_reference)
    nr = range_fft or beat.shape[1]
    nd = doppler_fft or beat.shape[0]
    rfft = np.fft.fft(beat, n=nr, axis=1)
    rd = np.fft.fftshift(np.fft.fft(rfft, n=nd, axis=0), axes=0)
    return rd


def estimate_range_velocity(rx: np.ndarray, tx_reference: np.ndarray, cfg: WaveformConfig,
                            carrier_hz: float, range_fft: int | None = None,
                            doppler_fft: int | None = None) -> SensingEstimate:
    rd = range_doppler_map(rx, tx_reference, range_fft, doppler_fft)
    mag = np.abs(rd)
    d_bin, r_bin = np.unravel_index(np.argmax(mag), mag.shape)
    nr = rd.shape[1]
    nd = rd.shape[0]
    beat_freq = (r_bin if r_bin <= nr // 2 else r_bin - nr) * cfg.sample_rate_hz / nr
    range_m = abs(C0 * beat_freq / (2.0 * cfg.slope_hz_per_s))
    d_center = d_bin - nd // 2
    slow_rate = 1.0 / cfg.chirp_duration_s
    doppler_hz = d_center * slow_rate / nd
    velocity = doppler_hz * C0 / (2.0 * carrier_hz)
    return SensingEstimate(float(range_m), float(velocity), int(r_bin), int(d_bin))
