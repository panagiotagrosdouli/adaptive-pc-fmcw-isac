"""Literature-grounded FMCW IF-domain model.

The ADC in a practical FMCW radar samples the dechirped IF/beat signal.  This
module therefore avoids generating an RF/858-MHz sweep at a 10-MSPS ADC rate.
It analytically forms the sampled beat signal from range and Doppler.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np

C0 = 299_792_458.0


@dataclass(frozen=True)
class RadarProfile:
    carrier_hz: float = 77e9
    bandwidth_hz: float = 858e6
    chirp_duration_s: float = 25.6e-6
    chirp_repetition_s: float = 115.8e-6
    sample_rate_hz: float = 10e6
    samples_per_chirp: int = 256
    n_chirps: int = 64

    def validate(self) -> None:
        if min(self.carrier_hz, self.bandwidth_hz, self.chirp_duration_s,
               self.chirp_repetition_s, self.sample_rate_hz) <= 0:
            raise ValueError("profile values must be positive")
        if self.chirp_repetition_s < self.chirp_duration_s:
            raise ValueError("chirp repetition interval must be >= active chirp duration")
        expected = self.sample_rate_hz * self.chirp_duration_s
        if abs(expected - self.samples_per_chirp) > 0.5:
            raise ValueError("samples_per_chirp is inconsistent with Fs * chirp_duration")
        if self.n_chirps < 2:
            raise ValueError("n_chirps must be >= 2")

    @property
    def slope_hz_per_s(self) -> float:
        return self.bandwidth_hz / self.chirp_duration_s

    @property
    def wavelength_m(self) -> float:
        return C0 / self.carrier_hz

    @property
    def range_resolution_m(self) -> float:
        return C0 / (2.0 * self.bandwidth_hz)

    @property
    def positive_if_max_range_m(self) -> float:
        # Positive complex-IF convention with usable beat frequency up to Fs/2.
        return C0 * self.sample_rate_hz / (4.0 * self.slope_hz_per_s)

    @property
    def velocity_resolution_mps(self) -> float:
        return self.wavelength_m / (2.0 * self.n_chirps * self.chirp_repetition_s)

    @property
    def max_unambiguous_velocity_mps(self) -> float:
        return self.wavelength_m / (4.0 * self.chirp_repetition_s)


@dataclass(frozen=True)
class Target:
    range_m: float
    radial_velocity_mps: float
    amplitude: complex = 1.0 + 0.0j


def target_frequencies(profile: RadarProfile, target: Target) -> tuple[float, float]:
    """Return (fast-time beat frequency, slow-time monostatic Doppler)."""
    profile.validate()
    if target.range_m < 0:
        raise ValueError("range_m must be non-negative")
    tau = 2.0 * target.range_m / C0
    fd = 2.0 * target.radial_velocity_mps * profile.carrier_hz / C0
    fb = profile.slope_hz_per_s * tau + fd
    return float(fb), float(fd)


def synthesize_if(profile: RadarProfile, targets: list[Target], *, snr_db: float | None = None,
                  rng: np.random.Generator | None = None) -> np.ndarray:
    """Create [slow-time, fast-time] dechirped IF samples for point targets."""
    profile.validate()
    n = np.arange(profile.samples_per_chirp, dtype=float)
    m = np.arange(profile.n_chirps, dtype=float)
    t_fast = n / profile.sample_rate_hz
    t_slow = m * profile.chirp_repetition_s
    y = np.zeros((profile.n_chirps, profile.samples_per_chirp), dtype=complex)
    for target in targets:
        fb, fd = target_frequencies(profile, target)
        phase = 2.0 * np.pi * (fd * t_slow[:, None] + fb * t_fast[None, :])
        y += target.amplitude * np.exp(1j * phase)
    if snr_db is not None:
        if rng is None:
            rng = np.random.default_rng()
        p = float(np.mean(np.abs(y) ** 2))
        if p > 0:
            noise_power = p / (10.0 ** (snr_db / 10.0))
            sigma = np.sqrt(noise_power / 2.0)
            y = y + sigma * (rng.standard_normal(y.shape) + 1j * rng.standard_normal(y.shape))
    return y


def estimate_single_target(profile: RadarProfile, if_samples: np.ndarray,
                           range_fft: int = 2048, doppler_fft: int = 256) -> tuple[float, float]:
    """Estimate range and radial velocity from an IF matrix.

    Slow-time Doppler is estimated first, then removed from the fast-time beat
    frequency to reduce the standard FMCW range-Doppler coupling bias.
    """
    profile.validate()
    x = np.asarray(if_samples, dtype=complex)
    if x.shape != (profile.n_chirps, profile.samples_per_chirp):
        raise ValueError("unexpected IF matrix shape")
    win_r = np.hanning(profile.samples_per_chirp)[None, :]
    win_d = np.hanning(profile.n_chirps)[:, None]
    rd = np.fft.fftshift(
        np.fft.fft(np.fft.fft(x * win_r * win_d, n=range_fft, axis=1), n=doppler_fft, axis=0),
        axes=0,
    )
    d_bin, r_bin = np.unravel_index(np.argmax(np.abs(rd)), rd.shape)
    fd_axis = np.fft.fftshift(np.fft.fftfreq(doppler_fft, d=profile.chirp_repetition_s))
    fb_axis = np.fft.fftfreq(range_fft, d=1.0 / profile.sample_rate_hz)
    fd_hat = float(fd_axis[d_bin])
    fb_hat = float(fb_axis[r_bin])
    tau_hat = (fb_hat - fd_hat) / profile.slope_hz_per_s
    range_hat = max(0.0, C0 * tau_hat / 2.0)
    velocity_hat = fd_hat * C0 / (2.0 * profile.carrier_hz)
    return float(range_hat), float(velocity_hat)
