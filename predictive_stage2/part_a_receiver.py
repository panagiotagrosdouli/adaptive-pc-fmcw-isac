"""Part-A-derived PC-FMCW/DBPSK communication receiver kernel.

Ported from the submitted Part-A notebook communication branch. The notebook
uses fc=193.4 THz, B=10 GHz, T_chirp=10 us and 1 Gbit/s DBPSK timing. Its
receiver estimates a local carrier per symbol by FFT, refines the spectral
peak parabolically, compensates adjacent-symbol carrier phase rotation, and
makes a differential real-axis DBPSK decision.

This module intentionally preserves that receiver rather than replacing it
with an analytic textbook BER expression.
"""
from __future__ import annotations

import numpy as np

EPS = 1e-12


def symbol_intervals(t_fast: np.ndarray, symbol_period_s: float):
    n_symbols = int(np.floor((t_fast[-1] + (t_fast[1] - t_fast[0])) / symbol_period_s))
    edges = np.searchsorted(t_fast, np.arange(n_symbols + 1) * symbol_period_s, side="left")
    start, stop = edges[:-1], edges[1:]
    valid = stop > start
    return start[valid], stop[valid]


def recover_dbpsk(rx: np.ndarray, fs_hz: float, symbol_period_s: float, zeropad_factor: int = 8):
    t_fast = np.arange(rx.size, dtype=np.float64) / fs_hz
    start, stop = symbol_intervals(t_fast, symbol_period_s)
    lengths = stop - start
    centers = 0.5 * (start + stop - 1)
    fft_len = 1 << int(np.ceil(np.log2(zeropad_factor * lengths.max())))
    coeff = np.zeros(len(start), dtype=np.complex128)
    mu = np.zeros(len(start), dtype=np.float64)
    for k, (a, b) in enumerate(zip(start, stop, strict=True)):
        samples = rx[int(a):int(b)]
        mag = np.abs(np.fft.fft(samples, n=fft_len))
        peak = int(np.argmax(mag))
        delta = 0.0
        if 0 < peak < fft_len - 1:
            left, center, right = np.log(mag[peak-1] + EPS), np.log(mag[peak] + EPS), np.log(mag[peak+1] + EPS)
            denom = left - 2.0 * center + right
            if abs(denom) > EPS:
                delta = float(np.clip(0.5 * (left - right) / denom, -0.5, 0.5))
        mu[k] = (peak + delta) / fft_len
        n = np.arange(a, b) - centers[k]
        coeff[k] = np.mean(samples * np.exp(-1j * 2.0 * np.pi * mu[k] * n))
    raw = coeff[1:] * np.conj(coeff[:-1])
    mu_unwrapped = np.unwrap(2.0 * np.pi * mu) / (2.0 * np.pi)
    phase_step = 2.0 * np.pi * 0.5 * (mu_unwrapped[1:] + mu_unwrapped[:-1]) * np.diff(centers)
    obs = raw * np.exp(-1j * phase_step)
    return np.real(obs) < 0.0, obs
