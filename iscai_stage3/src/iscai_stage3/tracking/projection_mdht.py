"""Projection-based Hough primitives reproduced from the Part-A MDHT method."""

from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np


@dataclass(frozen=True)
class ProjectionHoughConfig:
    theta_min_deg: float = -90.0
    theta_max_deg: float = 90.0
    theta_bins: int = 181
    rho_bin_width: float = 1.0
    peak_threshold_fraction: float = 0.50
    peak_threshold_min: float = 2.0
    max_peaks: int = 18
    nms_radius_bins: int = 4
    support_epsilon: float = 1.6
    rho_bound_mode: str = "origin_norm"

    def __post_init__(self) -> None:
        values = (self.theta_min_deg, self.theta_max_deg, self.rho_bin_width,
                  self.peak_threshold_fraction, self.peak_threshold_min,
                  self.support_epsilon)
        if not all(math.isfinite(value) for value in values):
            raise ValueError("Hough configuration values must be finite.")
        if self.theta_min_deg >= self.theta_max_deg or self.theta_bins < 2:
            raise ValueError("Invalid Hough theta grid.")
        if self.rho_bin_width <= 0.0 or self.support_epsilon <= 0.0:
            raise ValueError("Rho width and support epsilon must be positive.")
        if not 0.0 <= self.peak_threshold_fraction <= 1.0:
            raise ValueError("Peak threshold fraction must lie in [0,1].")
        if self.max_peaks < 1 or self.nms_radius_bins < 0:
            raise ValueError("Invalid peak-count or NMS configuration.")
        if self.rho_bound_mode not in ("origin_norm", "legacy_span"):
            raise ValueError("rho_bound_mode must be origin_norm or legacy_span.")


@dataclass(frozen=True)
class ProjectionAccumulator:
    values: np.ndarray
    rho_grid: np.ndarray
    theta_grid_deg: np.ndarray


@dataclass(frozen=True)
class ProjectionPeak:
    rho: float
    theta_deg: float
    score: float
    rho_index: int
    theta_index: int


def compute_projection_accumulator(points_uv: np.ndarray, config: ProjectionHoughConfig) -> ProjectionAccumulator:
    points = np.asarray(points_uv, dtype=float)
    if points.ndim != 2 or points.shape[1] != 2 or len(points) == 0:
        raise ValueError("Projection points must be a non-empty Nx2 array.")
    if not np.all(np.isfinite(points)):
        raise ValueError("Projection points must be finite.")
    theta_deg = np.linspace(config.theta_min_deg, config.theta_max_deg, config.theta_bins)
    theta = np.deg2rad(theta_deg)
    # The Part-A notebook used the point-cloud span here. That loses votes
    # whenever the cloud is translated away from the coordinate origin.
    # Cauchy-Schwarz gives |u cos(theta)+v sin(theta)| <= hypot(u,v), so this
    # bound conserves every point's vote for every theta.
    if config.rho_bound_mode == "legacy_span":
        spans = np.ptp(points, axis=0)
        rho_extent = float(np.hypot(spans[0], spans[1]))
    else:
        rho_extent = float(np.max(np.hypot(points[:, 0], points[:, 1])))
    rho_min = -rho_extent - 2.0 * config.rho_bin_width
    rho_max = rho_extent + 2.0 * config.rho_bin_width
    rho_grid = np.arange(rho_min, rho_max + config.rho_bin_width, config.rho_bin_width)
    accumulator = np.zeros((len(rho_grid), len(theta)), dtype=float)
    rho_values = points[:, 0, None] * np.cos(theta)[None, :] + points[:, 1, None] * np.sin(theta)[None, :]
    rho_indices = np.rint((rho_values - rho_min) / config.rho_bin_width).astype(int)
    for theta_index in range(len(theta)):
        valid = rho_indices[:, theta_index]
        valid = valid[(valid >= 0) & (valid < len(rho_grid))]
        np.add.at(accumulator[:, theta_index], valid, 1.0)
    return ProjectionAccumulator(accumulator, rho_grid, theta_deg)


def smooth_accumulator_3x3(accumulator: np.ndarray) -> np.ndarray:
    values = np.asarray(accumulator, dtype=float)
    if values.ndim != 2 or values.size == 0:
        raise ValueError("Accumulator must be a non-empty 2D array.")
    padded = np.pad(values, 1, mode="edge")
    return sum(padded[i:i+values.shape[0], j:j+values.shape[1]] for i in range(3) for j in range(3)) / 9.0


def detect_projection_peaks(accumulator: ProjectionAccumulator, config: ProjectionHoughConfig) -> tuple[ProjectionPeak, ...]:
    values = np.asarray(accumulator.values, dtype=float)
    threshold = max(config.peak_threshold_fraction * float(np.max(values)), config.peak_threshold_min)
    selected: list[ProjectionPeak] = []
    indices: list[tuple[int, int]] = []
    for flat_index in np.argsort(values.ravel())[::-1]:
        score = float(values.ravel()[flat_index])
        if score < threshold:
            break
        rho_index, theta_index = np.unravel_index(flat_index, values.shape)
        if any(abs(rho_index-r) <= config.nms_radius_bins and abs(theta_index-t) <= config.nms_radius_bins for r,t in indices):
            continue
        selected.append(ProjectionPeak(float(accumulator.rho_grid[rho_index]), float(accumulator.theta_grid_deg[theta_index]), score, int(rho_index), int(theta_index)))
        indices.append((int(rho_index), int(theta_index)))
        if len(selected) >= config.max_peaks:
            break
    return tuple(selected)


def supporting_point_ids(points_uv: np.ndarray, point_ids: tuple[str, ...], peak: ProjectionPeak, config: ProjectionHoughConfig) -> frozenset[str]:
    points = np.asarray(points_uv, dtype=float)
    if len(points) != len(point_ids):
        raise ValueError("Point IDs and projection points must have equal length.")
    theta = math.radians(peak.theta_deg)
    distance = np.abs(points[:,0]*math.cos(theta) + points[:,1]*math.sin(theta) - peak.rho)
    return frozenset(point_id for point_id, keep in zip(point_ids, distance < config.support_epsilon) if keep)
