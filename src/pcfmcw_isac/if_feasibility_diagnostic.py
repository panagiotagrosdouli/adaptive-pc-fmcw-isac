"""Independent, non-mutating IF feasibility diagnostic for post-freeze review.

This module deliberately does NOT replace the frozen publication gate.
"""
from __future__ import annotations

from dataclasses import dataclass

from .if_model import RadarProfile, Target, target_frequencies


@dataclass(frozen=True)
class IFDiagnostic:
    beat_hz: float
    nyquist_hz: float
    sampled_if_supported: bool
    canonical_gate_supported: bool
    gate_mismatch: bool


def diagnose_if(profile: RadarProfile, range_m: float, radial_velocity_mps: float) -> IFDiagnostic:
    """Check the signed beat against the project's declared +/-Fs/2 IF convention.

    This is a point-target representability check, not an automotive RF
    front-end certification; hardware passbands and safety margins are excluded.
    """
    from .publication_protocol import EvaluationState, is_physics_feasible

    profile.validate()
    beat_hz, _ = target_frequencies(profile, Target(range_m, radial_velocity_mps))
    nyquist_hz = profile.sample_rate_hz / 2.0
    sampled = -nyquist_hz <= beat_hz < nyquist_hz
    state = EvaluationState(
        ebn0_db=12.0, if_snr_db=10.0, range_m=range_m,
        radial_velocity_mps=radial_velocity_mps, residual_cfo_hz=0.0,
        inr_db=None, phase_noise_std_rad_per_sample=0.0,
        state_uncertainty_scale=0.0, seed=0,
    )
    canonical = is_physics_feasible(profile, state)
    return IFDiagnostic(beat_hz, nyquist_hz, sampled, canonical, canonical != sampled)
