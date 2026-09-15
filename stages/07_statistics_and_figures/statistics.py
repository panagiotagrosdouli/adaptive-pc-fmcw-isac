"""Predeclared, paired scenario-cluster inference for Stage 07."""
from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
from scipy import stats


@dataclass(frozen=True)
class PairedResult:
    clusters: int
    mean_delta: float
    ci_low: float
    ci_high: float
    wilcoxon_p: float
    paired_t_p: float
    cohen_dz: float | None
    win_fraction: float


def cluster_means(records: list[dict], group: str, metric: str, cluster: str = "scenario_id") -> dict:
    """Average repeated rows within scenario before any inferential test."""
    grouped: dict[tuple[str, str], list[float]] = {}
    for record in records:
        key = (str(record[cluster]), str(record[group]))
        value = float(record[metric])
        if not math.isfinite(value):
            raise ValueError(f"non-finite {metric} for {key}")
        grouped.setdefault(key, []).append(value)
    return {key: float(np.mean(values)) for key, values in grouped.items()}


def paired_deltas(
    records: list[dict],
    group: str,
    metric: str,
    treatment: str,
    control: str,
    higher_is_better: bool,
    cluster: str = "scenario_id",
) -> tuple[list[str], np.ndarray]:
    means = cluster_means(records, group, metric, cluster)
    treatment_clusters = {c for c, g in means if g == treatment}
    control_clusters = {c for c, g in means if g == control}
    if treatment_clusters != control_clusters:
        missing_treatment = sorted(control_clusters - treatment_clusters)
        missing_control = sorted(treatment_clusters - control_clusters)
        raise ValueError(
            f"unpaired clusters; missing treatment={missing_treatment}, missing control={missing_control}"
        )
    clusters = sorted(treatment_clusters)
    if not clusters:
        raise ValueError("comparison has no paired scenario clusters")
    sign = 1.0 if higher_is_better else -1.0
    delta = np.array([
        sign * (means[(c, treatment)] - means[(c, control)]) for c in clusters
    ])
    return clusters, delta


def bootstrap_mean_ci(delta: np.ndarray, repetitions: int = 10_000, seed: int = 20260904) -> tuple[float, float]:
    values = np.asarray(delta, float)
    if values.ndim != 1 or not len(values) or repetitions < 1:
        raise ValueError("bootstrap needs a non-empty 1-D delta and positive repetitions")
    rng = np.random.default_rng(seed)
    means = np.empty(repetitions)
    chunk = 1_000
    for start in range(0, repetitions, chunk):
        count = min(chunk, repetitions - start)
        indices = rng.integers(0, len(values), size=(count, len(values)))
        means[start:start + count] = values[indices].mean(axis=1)
    return tuple(float(x) for x in np.quantile(means, [0.025, 0.975]))


def analyze_delta(delta: np.ndarray, repetitions: int = 10_000, seed: int = 20260904) -> PairedResult:
    values = np.asarray(delta, float)
    if values.ndim != 1 or not len(values) or np.any(~np.isfinite(values)):
        raise ValueError("paired delta must be finite and non-empty")
    ci_low, ci_high = bootstrap_mean_ci(values, repetitions, seed)
    if np.all(values == 0):
        wilcoxon_p = paired_t_p = 1.0
    else:
        wilcoxon_p = float(stats.wilcoxon(values, alternative="two-sided").pvalue)
        paired_t_p = float(stats.ttest_1samp(values, 0.0).pvalue) if len(values) > 1 else 1.0
    sd = float(np.std(values, ddof=1)) if len(values) > 1 else 0.0
    dz = float(np.mean(values) / sd) if sd > 0 else None
    return PairedResult(
        clusters=len(values), mean_delta=float(np.mean(values)), ci_low=ci_low, ci_high=ci_high,
        wilcoxon_p=wilcoxon_p, paired_t_p=paired_t_p, cohen_dz=dz,
        win_fraction=float(np.mean(values > 0)),
    )


def holm_adjust(p_values: list[float]) -> list[float]:
    """Holm step-down adjusted p-values, returned in original order."""
    p = np.asarray(p_values, float)
    if p.ndim != 1 or np.any(~np.isfinite(p)) or np.any((p < 0) | (p > 1)):
        raise ValueError("p-values must be finite and in [0, 1]")
    order = np.argsort(p, kind="stable")
    adjusted_sorted = np.maximum.accumulate((len(p) - np.arange(len(p))) * p[order])
    adjusted = np.empty(len(p), float)
    adjusted[order] = np.minimum(adjusted_sorted, 1.0)
    return adjusted.tolist()
