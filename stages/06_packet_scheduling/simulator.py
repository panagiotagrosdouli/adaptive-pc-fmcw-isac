"""Paired packet-level scheduling simulator for the current research tree.

The simulator is deliberately independent of historical Stage-03 imports.
Predictions are decision inputs only; realized delivery is always scored from
shared ground-truth link traces. This makes the experiment suitable for a
future Stage-05 predictor without coupling Stage-06 to a legacy branch.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Protocol

import numpy as np


@dataclass(frozen=True)
class TrafficConfig:
    packet_bits: int = 12_000
    deadline_s: float = 0.1
    slot_s: float = 0.001
    average_rate_alpha: float = 0.01

    def validate(self) -> None:
        if self.packet_bits <= 0 or self.deadline_s <= 0 or self.slot_s <= 0:
            raise ValueError("packet_bits, deadline_s and slot_s must be positive")
        if not 0 < self.average_rate_alpha <= 1:
            raise ValueError("average_rate_alpha must be in (0, 1]")


@dataclass(frozen=True)
class SchedulerState:
    queue_bits: np.ndarray
    true_goodput_bps: np.ndarray
    average_rate_bps: np.ndarray
    predicted_goodput_bps: np.ndarray | None = None
    predicted_outage: np.ndarray | None = None


class Scheduler(Protocol):
    name: str

    def select(self, state: SchedulerState) -> int | None:
        """Return the vehicle to serve, or None for an idle slot."""


class GreedyGoodput:
    name = "greedy_goodput"

    def select(self, state: SchedulerState) -> int | None:
        available = state.queue_bits > 0
        if not np.any(available):
            return None
        score = np.where(available, state.true_goodput_bps, -np.inf)
        return int(np.argmax(score))


class PredictiveGoodput:
    """Prediction-driven policy; never used for physical delivery scoring."""

    name = "predictive_goodput"

    def select(self, state: SchedulerState) -> int | None:
        available = state.queue_bits > 0
        if not np.any(available):
            return None
        if state.predicted_goodput_bps is None:
            raise ValueError("predictive_goodput requires predictions")
        prediction = np.asarray(state.predicted_goodput_bps, float)
        if prediction.shape != state.queue_bits.shape:
            raise ValueError("predicted_goodput_bps shape must match vehicle count")
        score = np.where(available, prediction, -np.inf)
        return int(np.argmax(score))


def generate_arrivals(
    steps: int,
    vehicles: int,
    offered_load: float,
    reference_goodput_bps: float,
    config: TrafficConfig,
    seed: int,
) -> np.ndarray:
    """Create the immutable arrival trace shared by every policy."""
    config.validate()
    if steps <= 0 or vehicles <= 0 or not 0 <= offered_load <= 1:
        raise ValueError("invalid steps, vehicles or offered_load")
    mean_packets = offered_load * reference_goodput_bps * config.slot_s / config.packet_bits
    return np.random.default_rng(seed).poisson(
        mean_packets / vehicles, size=(steps, vehicles)
    ).astype(np.int64)


def _jain(values: np.ndarray) -> float:
    values = np.asarray(values, float)
    denominator = len(values) * float(np.sum(values * values))
    return 1.0 if denominator == 0 else float(np.sum(values) ** 2 / denominator)


def simulate(
    scheduler: Scheduler,
    true_goodput_bps: np.ndarray,
    true_outage: np.ndarray,
    arrivals: np.ndarray,
    config: TrafficConfig,
    predicted_goodput_bps: np.ndarray | None = None,
    predicted_outage: np.ndarray | None = None,
) -> dict:
    """Run one policy using shared exogenous traces and return raw metrics."""
    config.validate()
    truth = np.asarray(true_goodput_bps, float)
    outage = np.asarray(true_outage, bool)
    arrivals = np.asarray(arrivals, np.int64)
    if truth.ndim != 2 or outage.shape != truth.shape or arrivals.shape != truth.shape:
        raise ValueError("truth, outage and arrivals must share [steps, vehicles] shape")
    if np.any(~np.isfinite(truth)) or np.any(truth < 0) or np.any(arrivals < 0):
        raise ValueError("invalid ground-truth or arrival trace")
    steps, vehicles = truth.shape

    for name, values in (("predicted_goodput", predicted_goodput_bps), ("predicted_outage", predicted_outage)):
        if values is not None and np.asarray(values).shape != (steps, vehicles):
            raise ValueError(f"{name} must have shape [steps, vehicles]")

    queues = [deque() for _ in range(vehicles)]
    deadline_steps = max(1, int(round(config.deadline_s / config.slot_s)))
    offered_packets = int(arrivals.sum())
    delivered = np.zeros(vehicles, dtype=int)
    delivered_bits = np.zeros(vehicles, dtype=float)
    missed = 0
    latencies: list[float] = []
    average_rate = np.ones(vehicles, dtype=float)
    selected_slots = outage_slots = idle_slots = 0

    for step in range(steps):
        for vehicle in range(vehicles):
            for _ in range(int(arrivals[step, vehicle])):
                queues[vehicle].append([float(config.packet_bits), step, step + deadline_steps])

        for queue in queues:
            while queue and queue[0][2] <= step:
                queue.popleft()
                missed += 1

        queue_bits = np.array([sum(packet[0] for packet in q) for q in queues], float)
        state = SchedulerState(
            queue_bits=queue_bits,
            true_goodput_bps=truth[step],
            average_rate_bps=average_rate,
            predicted_goodput_bps=None if predicted_goodput_bps is None else np.asarray(predicted_goodput_bps)[step],
            predicted_outage=None if predicted_outage is None else np.asarray(predicted_outage)[step],
        )
        chosen = scheduler.select(state)
        served = np.zeros(vehicles, dtype=float)

        if chosen is None:
            idle_slots += 1
        else:
            if not 0 <= chosen < vehicles or not queues[chosen]:
                raise RuntimeError("scheduler selected an invalid or empty queue")
            selected_slots += 1
            outage_slots += int(outage[step, chosen])
            capacity = 0.0 if outage[step, chosen] else truth[step, chosen] * config.slot_s
            while capacity > 0 and queues[chosen]:
                packet = queues[chosen][0]
                sent = min(capacity, packet[0])
                packet[0] -= sent
                capacity -= sent
                served[chosen] += sent
                if packet[0] <= 1e-9:
                    queues[chosen].popleft()
                    delivered[chosen] += 1
                    delivered_bits[chosen] += config.packet_bits
                    latencies.append((step - packet[1] + 1) * config.slot_s)

        average_rate = (
            (1 - config.average_rate_alpha) * average_rate
            + config.average_rate_alpha * served / config.slot_s
        )

    missed += sum(len(q) for q in queues)
    elapsed = steps * config.slot_s
    return {
        "scheduler": scheduler.name,
        "offered_packets": offered_packets,
        "delivered_packets": int(delivered.sum()),
        "deadline_missed_packets": int(missed),
        "pdr": float(delivered.sum() / offered_packets) if offered_packets else 1.0,
        "deadline_miss_rate": float(missed / offered_packets) if offered_packets else 0.0,
        "timely_goodput_bps": float(delivered_bits.sum() / elapsed),
        "mean_latency_s": float(np.mean(latencies)) if latencies else None,
        "p95_latency_s": float(np.quantile(latencies, 0.95)) if latencies else None,
        "jain_fairness": _jain(delivered_bits),
        "scheduled_outage_fraction": float(outage_slots / selected_slots) if selected_slots else 0.0,
        "selected_slots": selected_slots,
        "idle_slots": idle_slots,
    }
