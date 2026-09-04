"""Named literature-grounded operating profiles used by the paper protocol."""
from __future__ import annotations
from dataclasses import dataclass

from .if_model import RadarProfile
from .comm_reference import CommConfig


def short_range_profile() -> RadarProfile:
    """TI automated-parking-style literature-grounded chirp profile (P-SR)."""
    return RadarProfile(
        carrier_hz=77e9,
        bandwidth_hz=858e6,
        chirp_duration_s=25.6e-6,
        chirp_repetition_s=115.8e-6,
        sample_rate_hz=10e6,
        samples_per_chirp=256,
        n_chirps=64,
    )


def high_mobility_profile() -> RadarProfile:
    """Composite 77-GHz high-mobility capability profile (P-HM)."""
    return RadarProfile(
        carrier_hz=77e9,
        bandwidth_hz=1e9,
        chirp_duration_s=20e-6,
        chirp_repetition_s=20e-6,
        sample_rate_hz=37.5e6,
        samples_per_chirp=750,
        n_chirps=128,
    )


@dataclass(frozen=True)
class OperatingProfile:
    name: str
    radar: RadarProfile
    comm: CommConfig
    normalized_cost: float

    def validate(self) -> None:
        self.radar.validate()
        self.comm.validate()
        if self.normalized_cost <= 0:
            raise ValueError("normalized_cost must be positive")


def default_operating_profiles() -> list[OperatingProfile]:
    """Finite profile set used for profile-selection experiments.

    Costs are declared normalized experiment costs rather than monetary/hardware
    measurements.  They are intentionally separated from source-derived constants.
    """
    sr = short_range_profile()
    hm = high_mobility_profile()
    return [
        OperatingProfile("P-SR-C16", sr, CommConfig(chips_per_chirp=16), 1.00),
        OperatingProfile("P-SR-C32", sr, CommConfig(chips_per_chirp=32), 1.10),
        OperatingProfile("P-SR-C64", sr, CommConfig(chips_per_chirp=64), 1.25),
        OperatingProfile("P-HM-C16", hm, CommConfig(chirp_duration_s=20e-6, chirp_repetition_s=20e-6, chips_per_chirp=16, n_chirps=128), 1.75),
        OperatingProfile("P-HM-C32", hm, CommConfig(chirp_duration_s=20e-6, chirp_repetition_s=20e-6, chips_per_chirp=32, n_chirps=128), 1.95),
        OperatingProfile("P-HM-C64", hm, CommConfig(chirp_duration_s=20e-6, chirp_repetition_s=20e-6, chips_per_chirp=64, n_chirps=128), 2.20),
    ]
