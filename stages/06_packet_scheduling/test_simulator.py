import importlib.util
from pathlib import Path
import sys

import numpy as np

P = Path(__file__).with_name("simulator.py")
SPEC = importlib.util.spec_from_file_location("stage06_simulator", P)
SIM = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = SIM
SPEC.loader.exec_module(SIM)


def test_arrivals_are_paired_and_reproducible():
    cfg = SIM.TrafficConfig()
    a = SIM.generate_arrivals(100, 3, 0.5, 1e9, cfg, seed=17)
    b = SIM.generate_arrivals(100, 3, 0.5, 1e9, cfg, seed=17)
    np.testing.assert_array_equal(a, b)


def test_predictions_never_replace_ground_truth_capacity():
    cfg = SIM.TrafficConfig(packet_bits=100, deadline_s=1, slot_s=0.1)
    arrivals = np.array([[1], [0], [0]])
    truth = np.zeros((3, 1))
    predicted = np.full((3, 1, 2), 1e9)
    result = SIM.simulate(
        SIM.SCHEDULERS.PredictiveUtility(), truth, np.ones_like(truth, bool), arrivals, cfg,
        predicted_goodput_bps=predicted,
    )
    assert result["delivered_packets"] == 0
    assert result["timely_goodput_bps"] == 0


def test_fifo_delivery_metrics_and_fairness_are_bounded():
    cfg = SIM.TrafficConfig(packet_bits=100, deadline_s=1, slot_s=0.1)
    truth = np.full((4, 2), 1000.0)
    arrivals = np.array([[1, 1], [0, 0], [0, 0], [0, 0]])
    result = SIM.simulate(
        SIM.SCHEDULERS.RoundRobin(), truth, np.zeros_like(truth, bool), arrivals, cfg
    )
    assert result["delivered_packets"] == 2
    assert result["pdr"] == 1
    assert 0 <= result["jain_fairness"] <= 1


def test_empty_trace_is_well_defined():
    cfg = SIM.TrafficConfig()
    truth = np.ones((5, 2))
    result = SIM.simulate(
        SIM.SCHEDULERS.ReactiveGreedy(), truth, np.zeros_like(truth, bool),
        np.zeros_like(truth, dtype=int), cfg,
    )
    assert result["pdr"] == 1
    assert result["deadline_miss_rate"] == 0
    assert result["idle_slots"] == 5


def test_partial_expired_packet_is_not_counted_as_timely_goodput():
    cfg = SIM.TrafficConfig(packet_bits=100, deadline_s=0.1, slot_s=0.1)
    truth = np.full((2, 1), 500.0)  # only 50 bits can be sent before the deadline
    result = SIM.simulate(
        SIM.SCHEDULERS.ReactiveGreedy(), truth, np.zeros_like(truth, bool),
        np.array([[1], [0]]), cfg,
    )
    assert result["delivered_packets"] == 0
    assert result["timely_goodput_bps"] == 0
    assert result["deadline_missed_packets"] == 1
