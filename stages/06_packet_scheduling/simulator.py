"""Paired packet-level scheduling simulation for Stage 06.

Predictions affect only scheduling decisions. Delivered bits are always
computed from the shared ground-truth link trace.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import importlib.util
from pathlib import Path
from typing import Protocol

import numpy as np

HERE = Path(__file__).resolve().parent
SCHEDULERS_PATH = HERE.parent / "03_classical_baselines" / "schedulers.py"
SPEC = importlib.util.spec_from_file_location("stage03_schedulers", SCHEDULERS_PATH)
SCHEDULERS = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
import sys
sys.modules[SPEC.name] = SCHEDULERS
SPEC.loader.exec_module(SCHEDULERS)


class Scheduler(Protocol):
    name: str
    def select(self, state: SCHEDULERS.SchedulerState) -> int | None: ...


@dataclass
class Packet:
    bits_remaining: float
    arrival_step: int
    deadline_step: int


@dataclass(frozen=True)
class TrafficConfig:
    packet_bits: int = 12_000
    deadline_s: float = 0.1
    slot_s: float = 0.001
    average_rate_alpha: float = 0.01

    def validate(self) -> None:
        if self.packet_bits <= 0 or self.deadline_s <= 0 or self.slot_s <= 0:
            raise ValueError("packet bits, deadline and slot duration must be positive")
        if not 0 < self.average_rate_alpha <= 1:
            raise ValueError("average_rate_alpha must be in (0, 1]")


def generate_arrivals(
    steps: int,
    vehicles: int,
    offered_load: float,
    reference_goodput_bps: float,
    config: TrafficConfig,
    seed: int,
) -> np.ndarray:
    """Generate the one immutable Poisson arrival trace used by every policy."""
    config.validate()
    if steps <= 0 or vehicles <= 0 or not 0 <= offered_load <= 1:
        raise ValueError("invalid trace dimensions or offered load")
    total_packets_per_slot = offered_load * reference_goodput_bps * config.slot_s / config.packet_bits
    return np.random.default_rng(seed).poisson(
        total_packets_per_slot / vehicles, size=(steps, vehicles)
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
    """Run one policy on shared exogenous traces and return episode metrics."""
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
        if values is not None and (np.asarray(values).ndim != 3 or np.asarray(values).shape[:2] != (steps, vehicles)):
            raise ValueError(f"{name} must have [steps, vehicles, horizon] shape")

    queues = [deque() for _ in range(vehicles)]
    deadline_steps = max(1, int(round(config.deadline_s / config.slot_s)))
    offered_packets = int(arrivals.sum())
    completed = np.zeros(vehicles, int)
    delivered_bits = np.zeros(vehicles, float)
    missed = 0
    latencies = []
    average_served = np.ones(vehicles, float)
    selected_slots = outage_slots = idle_slots = 0

    for step in range(steps):
        for vehicle in range(vehicles):
            for _ in range(int(arrivals[step, vehicle])):
                queues[vehicle].append(Packet(config.packet_bits, step, step + deadline_steps))
        for queue in queues:
            while queue and queue[0].deadline_step <= step:
                queue.popleft()
                missed += 1

        queue_bits = np.array([sum(packet.bits_remaining for packet in queue) for queue in queues])
        pg = None if predicted_goodput_bps is None else np.asarray(predicted_goodput_bps)[step]
        po = None if predicted_outage is None else np.asarray(predicted_outage)[step]
        state = SCHEDULERS.SchedulerState(queue_bits, truth[step], average_served, pg, po)
        chosen = scheduler.select(state)
        served_this_slot = np.zeros(vehicles, float)
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
                served = min(capacity, packet.bits_remaining)
                packet.bits_remaining -= served
                capacity -= served
                served_this_slot[chosen] += served
                if packet.bits_remaining <= 1e-9:
                    queues[chosen].popleft()
                    completed[chosen] += 1
                    delivered_bits[chosen] += config.packet_bits
                    latencies.append((step - packet.arrival_step + 1) * config.slot_s)
        average_served = (
            (1 - config.average_rate_alpha) * average_served
            + config.average_rate_alpha * served_this_slot / config.slot_s
        )

    missed += sum(len(queue) for queue in queues)
    elapsed = steps * config.slot_s
    p95 = float(np.quantile(latencies, 0.95)) if latencies else None
    return {
        "scheduler": scheduler.name,
        "offered_packets": offered_packets,
        "delivered_packets": int(completed.sum()),
        "deadline_missed_packets": int(missed),
        "pdr": float(completed.sum() / offered_packets) if offered_packets else 1.0,
        "deadline_miss_rate": float(missed / offered_packets) if offered_packets else 0.0,
        "timely_goodput_bps": float(delivered_bits.sum() / elapsed),
        "mean_latency_s": float(np.mean(latencies)) if latencies else None,
        "p95_latency_s": p95,
        "jain_fairness": _jain(delivered_bits),
        "scheduled_outage_fraction": float(outage_slots / selected_slots) if selected_slots else 0.0,
        "selected_slots": selected_slots,
        "idle_slots": idle_slots,
    }
