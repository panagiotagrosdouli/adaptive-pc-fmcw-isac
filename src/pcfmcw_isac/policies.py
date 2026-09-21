from __future__ import annotations

from dataclasses import replace
import numpy as np
from .models import PhyConfig, QoS, State
from .physics import dbpsk_ber, effective_rate_mbps, range_rmse_m, velocity_rmse_mps


def default_codebook() -> list[PhyConfig]:
    return [
        PhyConfig(p, l, n, r)
        for p in (0.5, 1.0, 2.0)
        for l in (16, 32, 64)
        for n in (16, 32, 64)
        for r in (1, 2, 4)
    ]


def communication_ok(s: State, c: PhyConfig, q: QoS) -> bool:
    return dbpsk_ber(s, c) <= q.ber_max and effective_rate_mbps(s, c) >= q.min_effective_rate_mbps


def sensing_ok(s: State, c: PhyConfig, q: QoS) -> bool:
    return range_rmse_m(s, c) <= q.range_rmse_max_m and velocity_rmse_mps(s, c) <= q.velocity_rmse_max_mps


def _cheapest(configs: list[PhyConfig]) -> PhyConfig:
    return min(configs, key=lambda c: (c.resource_cost, c.code_length))


def select_configuration(policy: str, estimated: State, qos: QoS, configs: list[PhyConfig] | None = None,
                         rng: np.random.Generator | None = None, uncertainty_scale: float = 0.0,
                         oracle_state: State | None = None) -> PhyConfig:
    configs = configs or default_codebook()
    if policy == "B0_fixed":
        return max(configs, key=lambda c: (c.resource_cost, c.code_length))
    if policy == "oracle":
        if oracle_state is None:
            raise ValueError("oracle_state is required for oracle policy")
        valid = [c for c in configs if communication_ok(oracle_state, c, qos) and sensing_ok(oracle_state, c, qos)]
        return _cheapest(valid or configs)
    if policy == "B1_comm":
        valid = [c for c in configs if communication_ok(estimated, c, qos)]
        return _cheapest(valid or configs)
    if policy == "B2_sensing":
        valid = [c for c in configs if sensing_ok(estimated, c, qos)]
        return _cheapest(valid or configs)
    if policy == "B3_joint":
        valid = [c for c in configs if communication_ok(estimated, c, qos) and sensing_ok(estimated, c, qos)]
        return _cheapest(valid or configs)
    if policy != "B4_robust":
        raise ValueError(f"unknown policy: {policy}")
    rng = rng or np.random.default_rng(0)
    samples = []
    for _ in range(64):
        samples.append(replace(
            estimated,
            snr_db=estimated.snr_db + rng.normal(0.0, 1.5 * uncertainty_scale),
            doppler_hz=estimated.doppler_hz + rng.normal(0.0, 100.0 * uncertainty_scale),
            cfo_hz=estimated.cfo_hz + rng.normal(0.0, 50.0 * uncertainty_scale),
        ))
    valid = []
    for c in configs:
        success = np.mean([communication_ok(s, c, qos) and sensing_ok(s, c, qos) for s in samples])
        if success >= qos.joint_success_probability:
            valid.append(c)
    return _cheapest(valid or configs)
