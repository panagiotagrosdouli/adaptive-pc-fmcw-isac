from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np
from typing import Literal

from iscai_stage3.tracking.cartesian import CartesianDetection, CartesianDetectionFrame


@dataclass(frozen=True)
class Tracklet:
    tracklet_id: int
    timestamps_s: tuple[float, ...]
    positions_H0_m: tuple[tuple[float, float, float], ...]
    covariances_H0_m2: tuple[tuple[tuple[float, float, float], ...], ...]
    source_detection_keys: tuple[str, ...]


AssociationMetric = Literal["euclidean", "mahalanobis"]


def _cost(
    tracklet: Tracklet,
    detection: CartesianDetection,
    timestamp_s: float,
    metric: AssociationMetric,
) -> float:
    dt = timestamp_s - tracklet.timestamps_s[-1]
    if dt <= 0.0:
        raise ValueError("Tracking frames must have strictly increasing timestamps.")
    last = np.asarray(tracklet.positions_H0_m[-1])
    if len(tracklet.positions_H0_m) >= 2:
        previous = np.asarray(tracklet.positions_H0_m[-2])
        previous_dt = tracklet.timestamps_s[-1] - tracklet.timestamps_s[-2]
        velocity = (last - previous) / previous_dt
        predicted = last + velocity * dt
    else:
        predicted = last
    residual = np.asarray(detection.position_H0_m) - predicted
    if metric == "euclidean":
        return float(residual @ residual)
    if metric != "mahalanobis":
        raise ValueError("Unknown association metric.")
    innovation = np.asarray(tracklet.covariances_H0_m2[-1]) + np.asarray(detection.covariance_H0_m2)
    innovation += np.eye(3) * 1e-9
    return float(residual @ np.linalg.solve(innovation, residual))


def build_gnn_tracklets(
    frames: tuple[CartesianDetectionFrame, ...],
    *,
    chi_square_gate: float = 11.3448667301,
    association_metric: AssociationMetric = "mahalanobis",
    euclidean_gate_m: float = 5.0,
) -> tuple[Tracklet, ...]:
    """Deterministic causal global-nearest-neighbour baseline.

    The default gate is the 99% chi-square threshold for three dimensions.
    This is an association baseline, not a claim of full joint MHT.
    """

    if not math.isfinite(chi_square_gate) or chi_square_gate <= 0.0:
        raise ValueError("chi_square_gate must be finite and positive.")
    if not math.isfinite(euclidean_gate_m) or euclidean_gate_m <= 0.0:
        raise ValueError("euclidean_gate_m must be finite and positive.")
    if association_metric not in ("euclidean", "mahalanobis"):
        raise ValueError("Unknown association metric.")
    association_gate = (
        euclidean_gate_m ** 2
        if association_metric == "euclidean"
        else chi_square_gate
    )
    active: list[Tracklet] = []
    next_id = 0
    previous_timestamp = None
    for frame in frames:
        if previous_timestamp is not None and frame.timestamp_s <= previous_timestamp:
            raise ValueError("Tracking frames must have strictly increasing timestamps.")
        previous_timestamp = frame.timestamp_s
        candidates = []
        for track_index, tracklet in enumerate(active):
            for detection_index, detection in enumerate(frame.detections):
                cost = _cost(tracklet, detection, frame.timestamp_s, association_metric)
                if cost <= association_gate:
                    candidates.append((cost, tracklet.tracklet_id, detection.detection_key, track_index, detection_index))
        used_tracks: set[int] = set()
        used_detections: set[int] = set()
        for _, _, _, track_index, detection_index in sorted(candidates):
            if track_index in used_tracks or detection_index in used_detections:
                continue
            tracklet = active[track_index]
            detection = frame.detections[detection_index]
            active[track_index] = Tracklet(
                tracklet_id=tracklet.tracklet_id,
                timestamps_s=tracklet.timestamps_s + (frame.timestamp_s,),
                positions_H0_m=tracklet.positions_H0_m + (detection.position_H0_m,),
                covariances_H0_m2=tracklet.covariances_H0_m2 + (detection.covariance_H0_m2,),
                source_detection_keys=tracklet.source_detection_keys + (detection.detection_key,),
            )
            used_tracks.add(track_index)
            used_detections.add(detection_index)
        for detection_index, detection in enumerate(frame.detections):
            if detection_index in used_detections:
                continue
            active.append(Tracklet(next_id, (frame.timestamp_s,), (detection.position_H0_m,), (detection.covariance_H0_m2,), (detection.detection_key,)))
            next_id += 1
    return tuple(sorted(active, key=lambda item: item.tracklet_id))
