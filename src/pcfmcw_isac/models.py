from dataclasses import dataclass


@dataclass(frozen=True)
class State:
    snr_db: float
    doppler_hz: float
    interference_db: float = -100.0
    cfo_hz: float = 0.0
    phase_noise_std_rad: float = 0.0


@dataclass(frozen=True)
class PhyConfig:
    tx_power_scale: float
    code_length: int
    chirps: int
    repetitions: int

    @property
    def resource_cost(self) -> float:
        return self.tx_power_scale * self.chirps * self.repetitions


@dataclass(frozen=True)
class QoS:
    ber_max: float = 1e-3
    min_effective_rate_mbps: float = 1.0
    range_rmse_max_m: float = 0.5
    velocity_rmse_max_mps: float = 0.5
    joint_success_probability: float = 0.95
