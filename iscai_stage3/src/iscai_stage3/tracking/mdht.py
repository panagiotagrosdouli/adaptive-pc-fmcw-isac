"""Truth-free fixed-bin multidimensional Hough baseline."""

from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np

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


@dataclass(frozen=True)
class ProbabilisticMdhtPeak:
    x0_m: float
    y0_m: float
    vx_mps: float
    vy_mps: float
    normalized_score: float
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


def probabilistic_mdht(
    frames: tuple[CartesianDetectionFrame, ...],
    *,
    config: MdhtConfig = MdhtConfig(),
    process_variance_m2: float = 0.25,
) -> tuple[ProbabilisticMdhtPeak, ...]:
    """Score fixed-grid MDHT candidates with normalized covariance-aware votes."""

    if not math.isfinite(process_variance_m2) or process_variance_m2 < 0.0:
        raise ValueError("process_variance_m2 must be finite and non-negative.")
    candidate_config = MdhtConfig(
        position_bin_m=config.position_bin_m,
        velocity_bin_mps=config.velocity_bin_mps,
        minimum_time_separation_s=config.minimum_time_separation_s,
        minimum_votes=1,
    )
    candidates = fixed_bin_mdht(frames, config=candidate_config)
    if not candidates:
        return ()
    reference_time = frames[0].timestamp_s
    scores = np.zeros(len(candidates), dtype=float)
    supports = [set() for _ in candidates]
    for frame in frames:
        dt = frame.timestamp_s - reference_time
        for detection in frame.detections:
            covariance = np.asarray(detection.covariance_H0_m2, dtype=float)[:2, :2]
            covariance += np.eye(2) * process_variance_m2
            inverse = np.linalg.inv(covariance)
            log_weights = []
            for candidate in candidates:
                predicted = np.asarray((candidate.x0_m + candidate.vx_mps * dt, candidate.y0_m + candidate.vy_mps * dt))
                residual = np.asarray(detection.position_H0_m[:2]) - predicted
                log_weights.append(-0.5 * float(residual @ inverse @ residual))
            maximum = max(log_weights)
            weights = np.exp(np.asarray(log_weights) - maximum)
            total = float(np.sum(weights))
            if total <= 0.0 or not math.isfinite(total):
                raise RuntimeError("Invalid probabilistic MDHT normalization.")
            weights /= total
            scores += weights
            for index, weight in enumerate(weights):
                if weight >= 1.0 / len(candidates):
                    supports[index].add(detection.detection_key)
    peaks = tuple(
        ProbabilisticMdhtPeak(c.x0_m,c.y0_m,c.vx_mps,c.vy_mps,float(scores[i]),tuple(sorted(supports[i])))
        for i,c in enumerate(candidates)
    )
    return tuple(sorted(peaks,key=lambda p:(-p.normalized_score,p.x0_m,p.y0_m,p.vx_mps,p.vy_mps)))
