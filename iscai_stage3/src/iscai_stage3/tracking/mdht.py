"""Truth-free fixed-bin multidimensional Hough baseline."""

from __future__ import annotations

from dataclasses import dataclass
import math

from iscai_stage3.tracking.cartesian import CartesianDetectionFrame


@dataclass(frozen=True)
class MdhtConfig:
    position_bin_m: float = 1.0
    velocity_bin_mps: float = 1.0
    minimum_time_separation_s: float = 0.1
    minimum_votes: int = 2

    def __post_init__(self) -> None:
        if any(not math.isfinite(v) or v <= 0.0 for v in (self.position_bin_m, self.velocity_bin_mps, self.minimum_time_separation_s)):
            raise ValueError("MDHT bin widths and time separation must be positive.")
        if self.minimum_votes < 1:
            raise ValueError("minimum_votes must be positive.")


@dataclass(frozen=True)
class MdhtPeak:
    x0_m: float
    y0_m: float
    vx_mps: float
    vy_mps: float
    votes: int
    supporting_detection_keys: tuple[str, ...]


def _quantize(value: float, width: float) -> int:
    return math.floor(value / width + 0.5)


def fixed_bin_mdht(
    frames: tuple[CartesianDetectionFrame, ...],
    *,
    config: MdhtConfig = MdhtConfig(),
) -> tuple[MdhtPeak, ...]:
    """Vote from causal detection pairs for constant-velocity trajectories."""

    if len(frames) < 2:
        return ()
    for previous, current in zip(frames, frames[1:]):
        if current.timestamp_s <= previous.timestamp_s:
            raise ValueError("MDHT frames must have strictly increasing timestamps.")
    reference_time = frames[0].timestamp_s
    accumulator: dict[tuple[int, int, int, int], tuple[int, set[str]]] = {}
    for left_index, left_frame in enumerate(frames[:-1]):
        for right_frame in frames[left_index + 1:]:
            dt = right_frame.timestamp_s - left_frame.timestamp_s
            if dt < config.minimum_time_separation_s:
                continue
            for left in left_frame.detections:
                for right in right_frame.detections:
                    vx = (right.position_H0_m[0] - left.position_H0_m[0]) / dt
                    vy = (right.position_H0_m[1] - left.position_H0_m[1]) / dt
                    x0 = left.position_H0_m[0] - vx * (left_frame.timestamp_s - reference_time)
                    y0 = left.position_H0_m[1] - vy * (left_frame.timestamp_s - reference_time)
                    key = (_quantize(x0, config.position_bin_m), _quantize(y0, config.position_bin_m), _quantize(vx, config.velocity_bin_mps), _quantize(vy, config.velocity_bin_mps))
                    votes, support = accumulator.get(key, (0, set()))
                    accumulator[key] = (votes + 1, support | {left.detection_key, right.detection_key})
    peaks = []
    for key, (votes, support) in accumulator.items():
        if votes >= config.minimum_votes:
            peaks.append(MdhtPeak(key[0]*config.position_bin_m,key[1]*config.position_bin_m,key[2]*config.velocity_bin_mps,key[3]*config.velocity_bin_mps,votes,tuple(sorted(support))))
    return tuple(sorted(peaks, key=lambda peak: (-peak.votes, peak.x0_m, peak.y0_m, peak.vx_mps, peak.vy_mps)))
