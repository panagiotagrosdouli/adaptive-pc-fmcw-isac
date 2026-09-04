"""Reproducible experiment-grid utilities for publication runs."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from itertools import product
import json
from pathlib import Path

@dataclass(frozen=True)
class ExperimentPoint:
    snr_db: float
    velocity_mps: float
    cfo_hz: float
    phase_noise_std_rad: float
    inr_db: float | None
    seed: int


def grid(snr_db=(-10, 0, 10, 20, 30), velocity_mps=(0, 10, 30, 50),
         cfo_hz=(0, 100, 500), phase_noise_std_rad=(0.0, 1e-3, 1e-2),
         inr_db=(None, -10, 0, 10), seeds=range(10)) -> list[ExperimentPoint]:
    return [ExperimentPoint(*v) for v in product(snr_db, velocity_mps, cfo_hz,
                                                  phase_noise_std_rad, inr_db, seeds)]


def write_manifest(points: list[ExperimentPoint], path: str | Path) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps([asdict(x) for x in points], indent=2), encoding="utf-8")
