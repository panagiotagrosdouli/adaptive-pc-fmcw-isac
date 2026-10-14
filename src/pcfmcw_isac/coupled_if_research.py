"""Post-freeze receiver-passband-aware feasibility; NEVER edits frozen gate."""
from __future__ import annotations
from dataclasses import dataclass
from .if_model import RadarProfile, Target, target_frequencies

@dataclass(frozen=True)
class IFPassband:
    lower_hz: float
    upper_hz: float
    guard_hz: float = 0.0

    def validate(self) -> None:
        if self.lower_hz >= self.upper_hz or self.guard_hz < 0:
            raise ValueError("invalid IF passband")
        if 2*self.guard_hz >= self.upper_hz-self.lower_hz:
            raise ValueError("guard exceeds usable passband")

@dataclass(frozen=True)
class CoupledFeasibility:
    valid: bool
    reasons: tuple[str,...]
    beat_hz: float

def coupled_physics(profile: RadarProfile, range_m: float, radial_velocity_mps: float,
                    *, passband: IFPassband) -> CoupledFeasibility:
    """Hard support for one target under an EXPLICIT sampled IF convention.

    This does not cover front-end RF transfer functions, clutter, multi-target
    interference, range-Doppler estimator bias, or hardware implementation.
    """
    profile.validate()
    passband.validate()
    reasons=[]
    if range_m < 0:
        reasons.append("NEGATIVE_RANGE")
        return CoupledFeasibility(False,tuple(reasons),float("nan"))
    fb, _ = target_frequencies(profile, Target(range_m,radial_velocity_mps))
    if abs(radial_velocity_mps) > profile.max_unambiguous_velocity_mps:
        reasons.append("VELOCITY_AMBIGUOUS")
    if not (passband.lower_hz + passband.guard_hz <= fb <
            passband.upper_hz - passband.guard_hz):
        reasons.append("BEAT_OUTSIDE_IF_PASSBAND")
    return CoupledFeasibility(not reasons,tuple(reasons),fb)

def nominal_complex_if(profile: RadarProfile) -> IFPassband:
    """Explicit assumption: signed baseband alias-free interval [-Fs/2, Fs/2)."""
    profile.validate()
    return IFPassband(-profile.sample_rate_hz/2,profile.sample_rate_hz/2)

def nominal_positive_if(profile: RadarProfile) -> IFPassband:
    """Explicit separate convention, not a claim about the project's hardware."""
    profile.validate()
    return IFPassband(0.0,profile.sample_rate_hz/2)
