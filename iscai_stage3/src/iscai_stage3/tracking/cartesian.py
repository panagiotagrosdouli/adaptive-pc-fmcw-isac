from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np

from iscai_stage1.geometry.rigid import RigidTransform
from iscai_stage2.observations.detection_set import UnlabeledDetectionFrame


@dataclass(frozen=True)
class CartesianDetection:
    detection_key: str
    position_H0_m: tuple[float, float, float]
    covariance_H0_m2: tuple[tuple[float, float, float], ...]


@dataclass(frozen=True)
class CartesianDetectionFrame:
    scenario_id: str
    time_index: int
    timestamp_s: float
    detections: tuple[CartesianDetection, ...]
    frame_name: str = "H0"
    truth_free: bool = True


def detection_frame_to_H0(
    frame: UnlabeledDetectionFrame,
    *,
    T_H0_from_Ht: RigidTransform,
) -> CartesianDetectionFrame:
    """Transform a truth-free spherical frame and its covariance into H0."""

    converted = []
    rotation = np.asarray(T_H0_from_Ht.rotation, dtype=float)
    for detection in frame.detections:
        r = detection.range_m
        az = detection.azimuth_rad
        el = detection.elevation_rad
        ce = math.cos(el)
        point_Ht = (r * ce * math.cos(az), r * ce * math.sin(az), r * math.sin(el))
        point_H0 = T_H0_from_Ht.apply_point(point_Ht)
        jacobian = np.asarray(
            (
                (ce * math.cos(az), -r * ce * math.sin(az), -r * math.sin(el) * math.cos(az)),
                (ce * math.sin(az), r * ce * math.cos(az), -r * math.sin(el) * math.sin(az)),
                (math.sin(el), 0.0, r * ce),
            ),
            dtype=float,
        )
        source = np.asarray(detection.covariance.matrix, dtype=float)
        spherical_position_covariance = source[np.ix_((0, 2, 3), (0, 2, 3))]
        covariance_Ht = jacobian @ spherical_position_covariance @ jacobian.T
        covariance_H0 = rotation @ covariance_Ht @ rotation.T
        covariance_H0 = 0.5 * (covariance_H0 + covariance_H0.T)
        converted.append(
            CartesianDetection(
                detection_key=detection.detection_key,
                position_H0_m=tuple(float(v) for v in point_H0),
                covariance_H0_m2=tuple(tuple(float(v) for v in row) for row in covariance_H0),
            )
        )
    return CartesianDetectionFrame(
        scenario_id=frame.scenario_id,
        time_index=frame.time_index,
        timestamp_s=frame.timestamp_s,
        detections=tuple(converted),
    )
