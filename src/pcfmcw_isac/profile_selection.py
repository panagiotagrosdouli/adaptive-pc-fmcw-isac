"""Physics-gated profile selection before stochastic PHY optimization."""
from __future__ import annotations
from dataclasses import dataclass
from .profiles import OperatingProfile


@dataclass(frozen=True)
class PhysicalRequirement:
    range_m: float
    radial_velocity_mps: float
    min_raw_rate_bps: float = 0.0


def physically_feasible(profile: OperatingProfile, req: PhysicalRequirement) -> bool:
    """Check hard unambiguous-region and raw-rate limits.

    These are necessary conditions only. They do not replace BER/SNR/detection
    constraints and therefore must not be described as complete QoS feasibility.
    """
    profile.validate()
    return (
        req.range_m >= 0.0
        and req.range_m <= profile.radar.positive_if_max_range_m
        and abs(req.radial_velocity_mps) <= profile.radar.max_unambiguous_velocity_mps
        and profile.comm.raw_bit_rate_bps >= req.min_raw_rate_bps
    )


def select_min_cost_physical_profile(profiles: list[OperatingProfile], req: PhysicalRequirement) -> OperatingProfile | None:
    feasible = [p for p in profiles if physically_feasible(p, req)]
    if not feasible:
        return None
    return min(feasible, key=lambda p: p.normalized_cost)
