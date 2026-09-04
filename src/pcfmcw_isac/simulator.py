from __future__ import annotations

import numpy as np
from .models import QoS, State
from .physics import dbpsk_ber, effective_rate_mbps, range_rmse_m, velocity_rmse_mps
from .policies import communication_ok, sensing_ok, select_configuration

POLICIES = ("B0_fixed", "B1_comm", "B2_sensing", "B3_joint", "B4_robust", "oracle")


def run_trial(true_state: State, estimated_state: State, qos: QoS, rng: np.random.Generator,
              uncertainty_scale: float = 1.0) -> list[dict]:
    rows = []
    for policy in POLICIES:
        cfg = select_configuration(policy, estimated_state, qos, rng=rng,
                                   uncertainty_scale=uncertainty_scale, oracle_state=true_state)
        comm = communication_ok(true_state, cfg, qos)
        sensing = sensing_ok(true_state, cfg, qos)
        rows.append({
            "policy": policy,
            "ber": dbpsk_ber(true_state, cfg),
            "effective_rate_mbps": effective_rate_mbps(true_state, cfg),
            "range_rmse_m": range_rmse_m(true_state, cfg),
            "velocity_rmse_mps": velocity_rmse_mps(true_state, cfg),
            "communication_qos_met": comm,
            "sensing_qos_met": sensing,
            "joint_qos_met": comm and sensing,
            "resource_cost": cfg.resource_cost,
            "tx_power_scale": cfg.tx_power_scale,
            "code_length": cfg.code_length,
            "chirps": cfg.chirps,
            "repetitions": cfg.repetitions,
        })
    return rows
