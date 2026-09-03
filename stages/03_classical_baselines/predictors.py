"""Causal classical trajectory predictors for the paper baseline matrix."""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np

DT = 0.1
FUTURE_STEPS = 80


@dataclass(frozen=True)
class Forecast:
    mean_xy: np.ndarray
    covariance_xy: np.ndarray | None = None


class LastPosition:
    name = "Last-Position"
    def predict(self, history_xy: np.ndarray, steps: int = FUTURE_STEPS) -> Forecast:
        p = np.asarray(history_xy, float)[-1]
        return Forecast(np.repeat(p[None], steps, axis=0))


class ConstantVelocity:
    name = "CV"
    def predict(self, history_xy: np.ndarray, steps: int = FUTURE_STEPS) -> Forecast:
        h = np.asarray(history_xy, float)
        v = (h[-1] - h[-2]) / DT
        t = DT * np.arange(1, steps + 1)[:, None]
        return Forecast(h[-1] + t * v)


class ConstantAcceleration:
    name = "CA"
    def predict(self, history_xy: np.ndarray, steps: int = FUTURE_STEPS) -> Forecast:
        h = np.asarray(history_xy, float)
        v1 = (h[-1] - h[-2]) / DT
        v0 = (h[-2] - h[-3]) / DT
        a = (v1 - v0) / DT
        t = DT * np.arange(1, steps + 1)[:, None]
        return Forecast(h[-1] + t * v1 + 0.5 * t**2 * a)


class LinearKalmanCV:
    """Small deterministic CV Kalman baseline; observations are history positions only."""
    name = "Kalman-CV"
    def __init__(self, process_var: float = 1.0, measurement_var: float = 1.0):
        self.q, self.r = process_var, measurement_var

    def predict(self, history_xy: np.ndarray, steps: int = FUTURE_STEPS) -> Forecast:
        h = np.asarray(history_xy, float)
        F = np.array([[1,0,DT,0],[0,1,0,DT],[0,0,1,0],[0,0,0,1]], float)
        H = np.array([[1,0,0,0],[0,1,0,0]], float)
        Q = self.q * np.diag([DT**4/4, DT**4/4, DT**2, DT**2])
        R = self.r * np.eye(2)
        x = np.r_[h[0], [0.,0.]]; P = np.eye(4) * 10
        for z in h:
            x = F @ x; P = F @ P @ F.T + Q
            y = z - H @ x; S = H @ P @ H.T + R
            K = P @ H.T @ np.linalg.inv(S)
            x = x + K @ y; P = (np.eye(4) - K @ H) @ P
        means=[]; cov=[]
        for _ in range(steps):
            x = F @ x; P = F @ P @ F.T + Q
            means.append(x[:2].copy()); cov.append(P[:2,:2].copy())
        return Forecast(np.asarray(means), np.asarray(cov))


class InformationOracle:
    """Diagnostic upper-information forecast. Not deployable and not a global optimum."""
    name = "Information-Oracle"
    def predict(self, history_xy: np.ndarray, steps: int = FUTURE_STEPS, *, future_xy=None) -> Forecast:
        if future_xy is None:
            raise ValueError("InformationOracle explicitly requires future ground truth")
        f = np.asarray(future_xy, float)
        if len(f) < steps:
            raise ValueError("insufficient future labels")
        return Forecast(f[:steps].copy())
