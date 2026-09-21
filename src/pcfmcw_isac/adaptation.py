"""Finite-action reliability-constrained PHY adaptation."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Iterable
import numpy as np

@dataclass(frozen=True)
class PhyAction:
    name: str
    tx_power_scale: float = 1.0
    repetition: int = 1
    code_rate: float = 1.0
    code_length: int = 1

    @property
    def resource_cost(self) -> float:
        return float(self.tx_power_scale + 0.25 * self.repetition + 0.01 * self.code_length)

@dataclass(frozen=True)
class QoSTarget:
    ber_max: float = 1e-3
    rate_min_bps: float = 1e5
    range_rmse_max_m: float = 1.0
    velocity_rmse_max_mps: float = 1.0
    reliability: float = 0.95

@dataclass(frozen=True)
class PredictedOutcome:
    ber: float
    rate_bps: float
    range_rmse_m: float
    velocity_rmse_mps: float


def feasible(out: PredictedOutcome, q: QoSTarget) -> bool:
    return (out.ber <= q.ber_max and out.rate_bps >= q.rate_min_bps and
            out.range_rmse_m <= q.range_rmse_max_m and
            out.velocity_rmse_mps <= q.velocity_rmse_max_mps)


def select_fixed(actions: list[PhyAction], index: int = 0) -> PhyAction:
    return actions[index]


def select_nominal(actions: Iterable[PhyAction], predictor: Callable[[PhyAction], PredictedOutcome],
                   q: QoSTarget) -> PhyAction:
    acts = sorted(list(actions), key=lambda a: a.resource_cost)
    for a in acts:
        if feasible(predictor(a), q):
            return a
    return acts[-1]


def select_chance_constrained(actions: Iterable[PhyAction], sampler: Callable[[PhyAction, int], list[PredictedOutcome]],
                              q: QoSTarget, n_samples: int = 200) -> PhyAction:
    acts = sorted(list(actions), key=lambda a: a.resource_cost)
    for a in acts:
        outs = sampler(a, n_samples)
        p = np.mean([feasible(o, q) for o in outs])
        if p >= q.reliability:
            return a
    return acts[-1]
