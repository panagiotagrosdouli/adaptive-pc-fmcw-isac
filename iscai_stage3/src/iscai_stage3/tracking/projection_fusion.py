"""Three-projection AND fusion for Part-A-compatible MDHT segments."""

from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np

from iscai_stage3.tracking.projection_mdht import (
    ProjectionAccumulator,
    ProjectionHoughConfig,
    compute_projection_accumulator,
    detect_projection_peaks,
    smooth_accumulator_3x3,
    supporting_point_ids,
)


@dataclass(frozen=True)
class SpatiotemporalDetection:
    detection_key: str
    frame_index: int
    x_H0_m: float
    y_H0_m: float


@dataclass(frozen=True)
class SegmentGateConfig:
    minimum_common_support: int = 8
    minimum_distinct_frames: int = 8
    maximum_mean_residual_m: float = 1.8
    maximum_speed_mps: float = 3.0


@dataclass(frozen=True)
class ProjectionCandidate:
    plane: str
    support_ids: frozenset[str]
    score: float


@dataclass(frozen=True)
class MdhtSegment:
    window_start: int
    window_end: int
    support_ids: frozenset[str]
    frame_indices: tuple[int, ...]
    positions_H0_m: tuple[tuple[float, float], ...]
    velocity_H0_mps: tuple[float, float]
    mean_residual_m: float


def projection_points(detections: tuple[SpatiotemporalDetection, ...], plane: str) -> np.ndarray:
    if plane == "xy":
        return np.asarray([(d.x_H0_m, d.y_H0_m) for d in detections], dtype=float)
    if plane == "xt":
        return np.asarray([(d.frame_index, d.x_H0_m) for d in detections], dtype=float)
    if plane == "yt":
        return np.asarray([(d.frame_index, d.y_H0_m) for d in detections], dtype=float)
    raise ValueError("plane must be xy, xt, or yt.")


def projection_candidates(detections, plane, hough_config, minimum_support):
    points = projection_points(detections, plane)
    raw = compute_projection_accumulator(points, hough_config)
    smooth = ProjectionAccumulator(smooth_accumulator_3x3(raw.values), raw.rho_grid, raw.theta_grid_deg)
    peaks = detect_projection_peaks(smooth, hough_config)
    ids = tuple(d.detection_key for d in detections)
    result = []
    for peak in peaks:
        support = supporting_point_ids(points, ids, peak, hough_config)
        if len(support) >= minimum_support:
            result.append(ProjectionCandidate(plane, support, peak.score))
    return tuple(result)


def build_segment(detections, support_ids, window_start, window_end):
    selected = [d for d in detections if d.detection_key in support_ids]
    frames = sorted({d.frame_index for d in selected})
    positions = []
    for frame in frames:
        same = [d for d in selected if d.frame_index == frame]
        positions.append((sum(d.x_H0_m for d in same)/len(same), sum(d.y_H0_m for d in same)/len(same)))
    if len(frames) < 2:
        velocity = (0.0, 0.0)
        residual = math.inf
    else:
        fit_x = np.polyfit(frames, [p[0] for p in positions], 1)
        fit_y = np.polyfit(frames, [p[1] for p in positions], 1)
        velocity = (float(fit_x[0]), float(fit_y[0]))
        residual = float(np.mean(np.hypot(np.asarray([p[0] for p in positions])-np.polyval(fit_x,frames), np.asarray([p[1] for p in positions])-np.polyval(fit_y,frames))))
    return MdhtSegment(window_start, window_end, frozenset(support_ids), tuple(frames), tuple(positions), velocity, residual)


def segment_is_valid(segment: MdhtSegment, gate: SegmentGateConfig) -> bool:
    return (
        len(segment.support_ids) >= gate.minimum_common_support
        and len(segment.frame_indices) >= gate.minimum_distinct_frames
        and segment.mean_residual_m <= gate.maximum_mean_residual_m
        and math.hypot(*segment.velocity_H0_mps) <= gate.maximum_speed_mps
    )


def and_fused_segments(detections, *, window_start, window_end, hough_config=ProjectionHoughConfig(), gate=SegmentGateConfig()):
    if not detections:
        return ()
    candidates = {plane: projection_candidates(detections, plane, hough_config, gate.minimum_common_support) for plane in ("xy","xt","yt")}
    segments = []
    seen = set()
    for xy in candidates["xy"]:
        for xt in candidates["xt"]:
            pair = xy.support_ids & xt.support_ids
            if len(pair) < gate.minimum_common_support:
                continue
            for yt in candidates["yt"]:
                common = frozenset(pair & yt.support_ids)
                if common in seen or len(common) < gate.minimum_common_support:
                    continue
                segment = build_segment(detections, common, window_start, window_end)
                if segment_is_valid(segment, gate):
                    segments.append(segment)
                    seen.add(common)
    return tuple(sorted(segments, key=lambda s: (-len(s.support_ids), s.mean_residual_m, sorted(s.support_ids))))
