"""Paired synthetic crossing-target benchmark for association baselines."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import math
import random

from iscai_stage3.tracking.cartesian import CartesianDetection, CartesianDetectionFrame
from iscai_stage3.validation.association_benchmark import evaluate_gnn_association


@dataclass(frozen=True)
class CrossingBenchmarkConfig:
    trials: int = 200
    frames: int = 21
    dt_s: float = 0.1
    noise_scale: float = 1.0
    miss_probability: float = 0.05
    mean_false_alarms_per_frame: float = 0.2
    euclidean_gate_m: float = 3.0
    chi_square_gate: float = 11.3448667301

    def __post_init__(self) -> None:
        if self.trials < 2 or self.frames < 3 or self.dt_s <= 0.0:
            raise ValueError("Benchmark requires >=2 trials, >=3 frames and positive dt.")
        if self.noise_scale <= 0.0 or not math.isfinite(self.noise_scale):
            raise ValueError("noise_scale must be finite and positive.")
        if not 0.0 <= self.miss_probability < 1.0:
            raise ValueError("miss_probability must lie in [0,1).")
        if self.mean_false_alarms_per_frame < 0.0:
            raise ValueError("false-alarm mean must be non-negative.")


@dataclass(frozen=True)
class MethodSummary:
    mean_association_accuracy: float
    mean_tracklet_count: float


@dataclass(frozen=True)
class PairedDifference:
    mean: float
    ci95_low: float
    ci95_high: float


@dataclass(frozen=True)
class CrossingBenchmarkReport:
    trials: int
    euclidean: MethodSummary
    covariance_aware: MethodSummary
    accuracy_difference_cov_minus_euclidean: PairedDifference
    tracklet_difference_cov_minus_euclidean: PairedDifference
    synthetic_only: bool = True


def _poisson(rng: random.Random, mean: float) -> int:
    if mean == 0.0:
        return 0
    threshold = math.exp(-mean)
    product = 1.0
    count = -1
    while product > threshold:
        count += 1
        product *= rng.random()
    return count


def _paired_ci(values: list[float]) -> PairedDifference:
    mean = sum(values) / len(values)
    variance = sum((value - mean) ** 2 for value in values) / (len(values) - 1)
    half_width = 1.96 * math.sqrt(variance / len(values))
    return PairedDifference(mean, mean - half_width, mean + half_width)


def _trial(seed: int, config: CrossingBenchmarkConfig):
    rng = random.Random(seed)
    frames = []
    truth = {}
    midpoint = 0.5 * (config.frames - 1)
    for time_index in range(config.frames):
        detections = []
        for identity, sign in (("A", 1.0), ("B", -1.0)):
            if rng.random() < config.miss_probability:
                continue
            tau = time_index - midpoint
            true_x = 20.0 + 0.15 * tau
            true_y = sign * 0.45 * tau
            # Heteroscedastic, anisotropic uncertainty mimics changing CRLB and
            # angular error; the same covariance generates and scores the noise.
            sigma_x = config.noise_scale * (0.12 + 0.015 * abs(tau))
            sigma_y = config.noise_scale * (0.20 + 0.045 * abs(tau))
            key = f"{identity}-{time_index}"
            covariance = ((sigma_x**2,0.0,0.0),(0.0,sigma_y**2,0.0),(0.0,0.0,0.04))
            detections.append(CartesianDetection(key, (true_x+rng.gauss(0,sigma_x), true_y+rng.gauss(0,sigma_y), 0.0), covariance))
            truth[key] = identity
        for false_index in range(_poisson(rng, config.mean_false_alarms_per_frame)):
            key = f"FA-{time_index}-{false_index}"
            covariance = ((0.25,0,0),(0,0.25,0),(0,0,0.25))
            detections.append(CartesianDetection(key, (rng.uniform(16,24),rng.uniform(-5,5),0.0), covariance))
            truth[key] = key
        detections.sort(key=lambda item: hashlib.sha256(f"{seed}|{item.detection_key}".encode()).hexdigest())
        frames.append(CartesianDetectionFrame("synthetic-crossing",time_index,time_index*config.dt_s,tuple(detections)))
    common = dict(frames=tuple(frames), evaluator_identity_by_detection_key=truth)
    euclidean = evaluate_gnn_association(**common, association_metric="euclidean", euclidean_gate_m=config.euclidean_gate_m)
    covariance = evaluate_gnn_association(**common, association_metric="mahalanobis", chi_square_gate=config.chi_square_gate)
    return euclidean, covariance


def run_crossing_benchmark(config: CrossingBenchmarkConfig) -> CrossingBenchmarkReport:
    pairs = [_trial(seed, config) for seed in range(config.trials)]
    e_accuracy = [pair[0].association_accuracy for pair in pairs]
    c_accuracy = [pair[1].association_accuracy for pair in pairs]
    e_tracks = [float(pair[0].tracklet_count) for pair in pairs]
    c_tracks = [float(pair[1].tracklet_count) for pair in pairs]
    return CrossingBenchmarkReport(
        trials=config.trials,
        euclidean=MethodSummary(sum(e_accuracy)/config.trials,sum(e_tracks)/config.trials),
        covariance_aware=MethodSummary(sum(c_accuracy)/config.trials,sum(c_tracks)/config.trials),
        accuracy_difference_cov_minus_euclidean=_paired_ci([c-e for c,e in zip(c_accuracy,e_accuracy)]),
        tracklet_difference_cov_minus_euclidean=_paired_ci([c-e for c,e in zip(c_tracks,e_tracks)]),
    )
