"""Truth-free Stage-2 Cartesian frames to projection-MDHT adapter."""

from __future__ import annotations

from dataclasses import dataclass

from iscai_stage3.tracking.cartesian import CartesianDetectionFrame
from iscai_stage3.tracking.projection_fusion import SpatiotemporalDetection


@dataclass(frozen=True)
class MdhtPointCloud:
    scenario_id: str
    points: tuple[SpatiotemporalDetection, ...]
    timestamps_s: tuple[float, ...]
    observation_frame: str = "H0"
    truth_free: bool = True


def cartesian_frames_to_mdht_cloud(frames: tuple[CartesianDetectionFrame, ...]) -> MdhtPointCloud:
    if not frames:
        raise ValueError("At least one Cartesian detection frame is required.")
    scenario_id = frames[0].scenario_id
    previous_time = None
    points = []
    timestamps = []
    for local_index, frame in enumerate(frames):
        if frame.scenario_id != scenario_id:
            raise ValueError("All MDHT frames must belong to one scenario.")
        if frame.frame_name != "H0" or not frame.truth_free:
            raise ValueError("MDHT requires truth-free detections in H0.")
        if previous_time is not None and frame.timestamp_s <= previous_time:
            raise ValueError("MDHT frame timestamps must be strictly increasing.")
        previous_time = frame.timestamp_s
        timestamps.append(frame.timestamp_s)
        for detection in frame.detections:
            points.append(
                SpatiotemporalDetection(
                    detection_key=detection.detection_key,
                    frame_index=local_index,
                    x_H0_m=detection.position_H0_m[0],
                    y_H0_m=detection.position_H0_m[1],
                )
            )
    return MdhtPointCloud(scenario_id, tuple(points), tuple(timestamps))
