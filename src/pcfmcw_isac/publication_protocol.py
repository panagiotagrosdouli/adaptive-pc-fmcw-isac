"""Executable publication protocol for paper-grade PC-FMCW ISAC experiments.

This module turns the predeclared paper protocol into code so that final runs
cannot silently drift from the frozen action space, QoS targets, grids, seed
family, or physics-feasibility rules.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Iterable

from .if_model import RadarProfile


@dataclass(frozen=True)
class QoSTargets:
    ber_max: float = 1e-3
    effective_rate_min_bps: float = 1e5
    range_rmse_max_m: float = 1.0
    velocity_rmse_max_mps: float = 1.0
    joint_reliability_target: float = 0.95

    def validate(self) -> None:
        if not (0.0 < self.ber_max < 1.0):
            raise ValueError("ber_max must be in (0,1)")
        if self.effective_rate_min_bps <= 0:
            raise ValueError("effective_rate_min_bps must be positive")
        if self.range_rmse_max_m <= 0 or self.velocity_rmse_max_mps <= 0:
            raise ValueError("sensing RMSE limits must be positive")
        if not (0.0 < self.joint_reliability_target < 1.0):
            raise ValueError("joint_reliability_target must be in (0,1)")


@dataclass(frozen=True)
class PhyActionSpec:
    profile_name: str
    chips_per_chirp: int
    tx_power_backoff_db: float
    repetition_factor: int

    def validate(self) -> None:
        if self.chips_per_chirp not in (16, 32, 64):
            raise ValueError("chips_per_chirp outside frozen action set")
        if self.tx_power_backoff_db not in (0.0, 3.0, 6.0):
            raise ValueError("tx_power_backoff_db outside frozen action set")
        if self.repetition_factor not in (1, 2, 4):
            raise ValueError("repetition_factor outside frozen action set")
        if not self.profile_name:
            raise ValueError("profile_name is required")


@dataclass(frozen=True)
class EvaluationState:
    ebn0_db: float
    if_snr_db: float
    range_m: float
    radial_velocity_mps: float
    residual_cfo_hz: float
    inr_db: float | None
    phase_noise_std_rad_per_sample: float
    state_uncertainty_scale: float
    seed: int


@dataclass(frozen=True)
class FrozenPublicationProtocol:
    protocol_id: str = "pcfmcw_isac_paper_v1"
    qos: QoSTargets = QoSTargets()
    profile_names: tuple[str, ...] = (
        "ti_77ghz_parking_profile",
        "ti_77ghz_high_mobility_capability_profile",
    )
    chips_per_chirp: tuple[int, ...] = (16, 32, 64)
    tx_power_backoff_db: tuple[float, ...] = (0.0, 3.0, 6.0)
    repetition_factor: tuple[int, ...] = (1, 2, 4)
    ebn0_db: tuple[float, ...] = (-4, 0, 4, 8, 12, 16)
    if_snr_db: tuple[float, ...] = (-10, -5, 0, 5, 10, 15, 20)
    range_m: tuple[float, ...] = (5, 10, 20, 30, 40, 50)
    radial_velocity_mps: tuple[float, ...] = (-50, -30, -10, 0, 10, 30, 50)
    residual_cfo_hz: tuple[float, ...] = (0, 500, 1000, 2000, 5000)
    inr_db: tuple[float | None, ...] = (None, -10, 0, 10)
    phase_noise_std_rad_per_sample: tuple[float, ...] = (0.0, 0.001, 0.01)
    state_uncertainty_scale: tuple[float, ...] = (0.0, 0.5, 1.0, 2.0)
    final_seed_start: int = 10_000
    n_final_seeds: int = 1_000
    bootstrap_confidence: float = 0.95
    bootstrap_resamples: int = 10_000

    def validate(self) -> None:
        self.qos.validate()
        if self.final_seed_start < 0 or self.n_final_seeds <= 0:
            raise ValueError("invalid final seed family")
        if not (0.0 < self.bootstrap_confidence < 1.0):
            raise ValueError("bootstrap_confidence must be in (0,1)")
        if self.bootstrap_resamples <= 0:
            raise ValueError("bootstrap_resamples must be positive")
        for action in self.actions():
            action.validate()

    def actions(self) -> tuple[PhyActionSpec, ...]:
        return tuple(
            PhyActionSpec(*x)
            for x in product(
                self.profile_names,
                self.chips_per_chirp,
                self.tx_power_backoff_db,
                self.repetition_factor,
            )
        )

    def final_seeds(self) -> range:
        return range(self.final_seed_start, self.final_seed_start + self.n_final_seeds)

    def states(self, seeds: Iterable[int] | None = None) -> Iterable[EvaluationState]:
        if seeds is None:
            seeds = self.final_seeds()
        for values in product(
            self.ebn0_db,
            self.if_snr_db,
            self.range_m,
            self.radial_velocity_mps,
            self.residual_cfo_hz,
            self.inr_db,
            self.phase_noise_std_rad_per_sample,
            self.state_uncertainty_scale,
            seeds,
        ):
            yield EvaluationState(*values)


def is_physics_feasible(profile: RadarProfile, state: EvaluationState) -> bool:
    """Hard gate based only on declared FMCW support limits.

    This is intentionally deterministic: if a state is outside the profile's
    representable range/velocity support, no stochastic policy is allowed to
    rescue that action by exploiting noise or predictor optimism.
    """
    profile.validate()
    return (
        0.0 <= state.range_m <= profile.positive_if_max_range_m
        and abs(state.radial_velocity_mps) <= profile.max_unambiguous_velocity_mps
    )


def filter_physics_feasible_actions(
    actions: Iterable[PhyActionSpec],
    profiles: dict[str, RadarProfile],
    state: EvaluationState,
) -> tuple[PhyActionSpec, ...]:
    feasible: list[PhyActionSpec] = []
    for action in actions:
        action.validate()
        try:
            profile = profiles[action.profile_name]
        except KeyError as exc:
            raise KeyError(f"missing profile {action.profile_name!r}") from exc
        if is_physics_feasible(profile, state):
            feasible.append(action)
    return tuple(feasible)


FROZEN_PROTOCOL_V1 = FrozenPublicationProtocol()
