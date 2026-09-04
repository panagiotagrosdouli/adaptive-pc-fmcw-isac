"""Publication metrics and reliability summaries."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class JointMetrics:
    ber: float
    effective_rate_bps: float
    outage: bool
    range_error_m: float
    velocity_error_mps: float
    resource_cost: float
    qos_satisfied: bool


def bit_error_rate(bits: np.ndarray, decoded: np.ndarray) -> float:
    a = np.asarray(bits, dtype=int).reshape(-1)
    b = np.asarray(decoded, dtype=int).reshape(-1)
    if a.size != b.size or a.size == 0:
        raise ValueError("bit arrays must be non-empty and equal length")
    return float(np.mean(a != b))


def effective_rate(raw_rate_bps: float, ber: float, repetition: int = 1, code_rate: float = 1.0) -> float:
    return float(raw_rate_bps * code_rate / max(1, repetition) * max(0.0, 1.0 - ber))


def bootstrap_ci(values: np.ndarray, confidence: float = 0.95, n_boot: int = 2000,
                 seed: int = 0) -> tuple[float, float]:
    x = np.asarray(values, dtype=float).reshape(-1)
    if x.size < 2:
        raise ValueError("at least two samples required")
    rng = np.random.default_rng(seed)
    means = np.empty(n_boot)
    for i in range(n_boot):
        means[i] = np.mean(rng.choice(x, size=x.size, replace=True))
    alpha = (1.0 - confidence) / 2.0
    return float(np.quantile(means, alpha)), float(np.quantile(means, 1.0 - alpha))
