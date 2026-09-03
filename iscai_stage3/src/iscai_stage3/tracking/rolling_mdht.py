"""Rolling-window segment suppression and deterministic stitching."""

from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np

from iscai_stage3.tracking.projection_fusion import MdhtSegment


@dataclass(frozen=True)
class StitchingConfig:
    duplicate_jaccard_min: float = 0.45
    maximum_position_gap_m: float = 12.0
    maximum_velocity_gap_mps: float = 1.0
    maximum_time_gap_frames: int = 7
    position_weight: float = 1.0
    kinematic_weight: float = 6.0
    cost_threshold: float = 14.0


@dataclass(frozen=True)
class StitchedTrack:
    track_id: int
    segments: tuple[MdhtSegment, ...]


def support_jaccard(left: MdhtSegment, right: MdhtSegment) -> float:
    union = left.support_ids | right.support_ids
    return len(left.support_ids & right.support_ids) / len(union) if union else 0.0


def suppress_duplicate_segments(segments: tuple[MdhtSegment, ...], threshold: float) -> tuple[MdhtSegment, ...]:
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("Jaccard threshold must lie in [0,1].")
    ranked = sorted(segments, key=lambda s: (-len(s.support_ids), s.mean_residual_m, s.frame_indices))
    kept = []
    for segment in ranked:
        if not any(support_jaccard(segment, previous) >= threshold for previous in kept):
            kept.append(segment)
    return tuple(sorted(kept, key=lambda s: (s.window_start, s.frame_indices, sorted(s.support_ids))))


def track_points_by_frame(track: StitchedTrack) -> dict[int, np.ndarray]:
    grouped = {}
    for segment in track.segments:
        for frame, position in zip(segment.frame_indices, segment.positions_H0_m):
            grouped.setdefault(frame, []).append(position)
    return {frame: np.mean(points, axis=0) for frame, points in grouped.items()}


def stitching_cost(track: StitchedTrack, segment: MdhtSegment, config: StitchingConfig):
    points = track_points_by_frame(track)
    incoming = {frame: np.asarray(position) for frame, position in zip(segment.frame_indices, segment.positions_H0_m)}
    common = sorted(set(points) & set(incoming))
    if common:
        position_gap = float(np.mean([np.linalg.norm(points[f]-incoming[f]) for f in common]))
        time_gap = 0
    else:
        last_frame = max(points)
        first_frame = min(incoming)
        time_gap = max(0, first_frame-last_frame)
        velocity = np.asarray(track.segments[-1].velocity_H0_mps)
        predicted = points[last_frame] + velocity*(first_frame-last_frame)
        position_gap = float(np.linalg.norm(predicted-incoming[first_frame]))
    velocity_gap = float(np.linalg.norm(np.asarray(track.segments[-1].velocity_H0_mps)-np.asarray(segment.velocity_H0_mps)))
    feasible = position_gap < config.maximum_position_gap_m and velocity_gap < config.maximum_velocity_gap_mps and time_gap <= config.maximum_time_gap_frames
    cost = config.position_weight*position_gap + config.kinematic_weight*velocity_gap
    return feasible and cost < config.cost_threshold, cost


def stitch_segments(segments: tuple[MdhtSegment, ...], config: StitchingConfig = StitchingConfig()) -> tuple[StitchedTrack, ...]:
    tracks: list[StitchedTrack] = []
    next_id = 1
    for segment in sorted(segments, key=lambda s: (s.window_start, s.frame_indices, sorted(s.support_ids))):
        feasible = []
        for index, track in enumerate(tracks):
            accepted, cost = stitching_cost(track, segment, config)
            if accepted:
                feasible.append((cost, track.track_id, index))
        if not feasible:
            tracks.append(StitchedTrack(next_id, (segment,)))
            next_id += 1
        else:
            _, _, index = min(feasible)
            tracks[index] = StitchedTrack(tracks[index].track_id, tracks[index].segments+(segment,))
    return tuple(tracks)
