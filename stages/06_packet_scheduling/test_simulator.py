import importlib.util
from pathlib import Path

import numpy as np

P = Path(__file__).with_name("simulator.py")
SPEC = importlib.util.spec_from_file_location("stage06_simulator", P)
SIM = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(SIM)


def test_arrivals_are_reproducible():
    cfg = SIM.TrafficConfig()
    a = SIM.generate_arrivals(100, 3, 0.5, 1e9, cfg, seed=17)
    b = SIM.generate_arrivals(100, 3, 0.5, 1e9, cfg, seed=17)
    np.testing.assert_array_equal(a, b)


def test_predictions_cannot_create_physical_delivery():
    cfg = SIM.TrafficConfig(packet_bits=100, deadline_s=1.0, slot_s=0.1)
    arrivals = np.array([[1], [0], [0]])
    truth = np.zeros((3, 1))
    outage = np.ones((3, 1), dtype=bool)
    prediction = np.full((3, 1), 1e9)
    result = SIM.simulate(
        SIM.PredictiveGoodput(), truth, outage, arrivals, cfg,
        predicted_goodput_bps=prediction,
    )
    assert result["delivered_packets"] == 0
    assert result["timely_goodput_bps"] == 0


def test_paired_policies_share_the_same_exogenous_trace():
    cfg = SIM.TrafficConfig(packet_bits=100, deadline_s=1.0, slot_s=0.1)
    arrivals = SIM.generate_arrivals(20, 2, 0.5, 1e4, cfg, seed=42)
    truth = np.full((20, 2), 2_000.0)
    outage = np.zeros((20, 2), dtype=bool)
    a = SIM.simulate(SIM.GreedyGoodput(), truth, outage, arrivals, cfg)
    b = SIM.simulate(SIM.GreedyGoodput(), truth, outage, arrivals, cfg)
    assert a == b


def test_metrics_are_bounded_and_partial_packets_do_not_count():
    cfg = SIM.TrafficConfig(packet_bits=100, deadline_s=0.1, slot_s=0.1)
    truth = np.full((2, 1), 500.0)
    result = SIM.simulate(
        SIM.GreedyGoodput(), truth, np.zeros_like(truth, dtype=bool),
        np.array([[1], [0]]), cfg,
    )
    assert result["delivered_packets"] == 0
    assert result["timely_goodput_bps"] == 0
    assert result["deadline_missed_packets"] == 1
    assert 0 <= result["pdr"] <= 1
    assert 0 <= result["jain_fairness"] <= 1
