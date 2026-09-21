"""Statistical utilities for reliability-constrained publication experiments.

All functions operate on simulation outcomes.  A reliability target is declared
satisfied only when a one-sided confidence lower bound clears the target; the
raw Monte-Carlo success fraction alone is not sufficient.
"""
from __future__ import annotations

from math import sqrt
from statistics import NormalDist


def wilson_lower_bound(successes: int, trials: int, *, confidence: float = 0.95) -> float:
    """One-sided Wilson lower confidence bound for a Bernoulli probability."""
    if trials <= 0:
        raise ValueError("trials must be positive")
    if successes < 0 or successes > trials:
        raise ValueError("successes must lie in [0, trials]")
    if not 0.5 < confidence < 1.0:
        raise ValueError("confidence must lie in (0.5, 1)")
    p = successes / trials
    z = NormalDist().inv_cdf(confidence)
    z2 = z * z
    denominator = 1.0 + z2 / trials
    centre = p + z2 / (2.0 * trials)
    radius = z * sqrt((p * (1.0 - p) + z2 / (4.0 * trials)) / trials)
    return float(max(0.0, (centre - radius) / denominator))


def reliability_target_satisfied(
    successes: int,
    trials: int,
    *,
    target: float,
    confidence: float = 0.95,
) -> bool:
    """Return True iff the one-sided Wilson lower bound reaches ``target``."""
    if not 0.0 < target < 1.0:
        raise ValueError("target must lie in (0, 1)")
    return wilson_lower_bound(successes, trials, confidence=confidence) >= target
