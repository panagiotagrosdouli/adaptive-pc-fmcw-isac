"""Independent post-freeze research methods. No changes to frozen policies."""
from __future__ import annotations
from dataclasses import dataclass
from math import log, sqrt
from typing import Sequence

def hoeffding_upper_failures(failures: int, n: int, alpha: float) -> float:
    """Upper bound under independent Bernoulli trials."""
    if n < 1 or not 0 <= failures <= n or not 0 < alpha < 1:
        raise ValueError("invalid failures, n, or alpha")
    return min(1.0, failures / n + sqrt(log(1 / alpha) / (2 * n)))

@dataclass(frozen=True)
class CalibrationResult:
    threshold: float | None
    selected: int
    failures: int
    upper_failure_bound: float | None

def calibrate_fixed_thresholds(scores: Sequence[float], outcomes: Sequence[bool],
    *, thresholds: Sequence[float], risk_target: float = .05,
    alpha: float = .05, minimum_selected: int = 1) -> CalibrationResult:
    """Select the highest-coverage certified threshold on a PREDECLARED finite grid.

    Interpretation requires i.i.d. independent calibration units and a fixed
    score-producing policy. Pre-specified thresholds receive Bonferroni-adjusted
    Hoeffding bounds. Validation must use separate held-out samples.
    """
    if len(scores) != len(outcomes) or not scores or not thresholds:
        raise ValueError("nonempty equal-size input and thresholds required")
    if not 0 < risk_target < 1 or not 0 < alpha < 1 or minimum_selected < 1:
        raise ValueError("invalid risk or confidence")
    if any(not 0 <= s <= 1 for s in scores) or any(not 0 <= t <= 1 for t in thresholds):
        raise ValueError("scores/thresholds outside [0,1]")
    candidates = sorted(set(thresholds))
    best = None
    for t in candidates:
        selected = [bool(y) for s, y in zip(scores, outcomes) if s >= t]
        if len(selected) < minimum_selected:
            continue
        failures = len(selected) - sum(selected)
        upper = hoeffding_upper_failures(failures, len(selected), alpha / len(candidates))
        if upper <= risk_target and (best is None or len(selected) > best.selected):
            best = CalibrationResult(t, len(selected), failures, upper)
    return best if best is not None else CalibrationResult(None, 0, 0, None)

@dataclass(frozen=True)
class SequentialDecision:
    accepted: bool
    rejected: bool
    draws: int
    lower_success: float
    upper_success: float

def anytime_bernoulli_decision(outcomes: Sequence[bool], *, target: float = .95,
    alpha: float = .05, min_draws: int = 32, max_draws: int = 512) -> SequentialDecision:
    """Optional-stopping-safe sequence of Hoeffding intervals via union bound.

    For each t, alpha_t = alpha/(t(t+1)); the sum is <= alpha.
    Assumes independent Bernoulli draws of fixed unknown success probability.
    """
    if not 0 < target < 1 or not 0 < alpha < 1 or not 1 <= min_draws <= max_draws:
        raise ValueError("invalid stopping configuration")
    k, lo, hi = 0, 0.0, 1.0
    n_seen = 0
    for n, outcome in enumerate(outcomes, start=1):
        if n > max_draws:
            break
        n_seen = n
        k += bool(outcome)
        eps = sqrt(log(2 * n * (n + 1) / alpha) / (2 * n))
        lo, hi = max(0.0, k/n - eps), min(1.0, k/n + eps)
        if n >= min_draws:
            if lo >= target:
                return SequentialDecision(True, False, n, lo, hi)
            if hi < target:
                return SequentialDecision(False, True, n, lo, hi)
    return SequentialDecision(False, False, n_seen, lo, hi)
