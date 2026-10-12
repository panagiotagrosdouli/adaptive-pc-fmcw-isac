"""Regression tests for the frozen publication-v2.1 statistical summary.

These tests validate bookkeeping and published summary consistency; they do not
re-run the Monte Carlo experiment or establish real-world reliability.
"""

import json
import math
from pathlib import Path

RESULTS = Path(__file__).resolve().parents[1] / "artifacts/publication/v2_1/FINAL_RESULTS.json"
Z_ONE_SIDED_95 = 1.6448536269514722


def _wilson_lower(successes: int, trials: int) -> float:
    p = successes / trials
    z = Z_ONE_SIDED_95
    return (
        p + z * z / (2 * trials)
        - z * math.sqrt(p * (1 - p) / trials + z * z / (4 * trials * trials))
    ) / (1 + z * z / trials)


def test_frozen_primary_policy_bookkeeping():
    data = json.loads(RESULTS.read_text())
    assert data["protocol_id"] == "pcfmcw_isac_paper_v2_1"
    assert data["n_states_per_policy"] == 12000
    assert data["n_records"] == 72000
    assert len(data["aggregate"]) == 6

    for name, metrics in data["aggregate"].items():
        bounds = data["reliability_bounds"][name]
        total = bounds["unconditional_trials"]
        selected = bounds["conditional_trials"]
        successful = bounds["unconditional_successes"]
        assert total == 12000, name
        assert 0 <= successful <= selected <= total, name
        assert bounds["conditional_successes"] == successful, name
        assert math.isclose(metrics["selection_rate"], selected / total, abs_tol=1e-12), name
        assert math.isclose(metrics["abstention_rate"], 1 - selected / total, abs_tol=1e-12), name
        assert math.isclose(metrics["joint_qos_probability_unconditional"], successful / total, abs_tol=1e-12), name
        assert math.isclose(
            metrics["joint_qos_probability_conditional_on_selection"], successful / selected,
            abs_tol=1e-12
        ), name
        assert math.isclose(
            bounds["unconditional_wilson_lower_95"], _wilson_lower(successful, total),
            abs_tol=1e-10
        ), name
        assert math.isclose(
            bounds["conditional_wilson_lower_95"], _wilson_lower(successful, selected),
            abs_tol=1e-10
        ), name


def test_frozen_b4_b3_tradeoff_not_reversed():
    data = json.loads(RESULTS.read_text())
    metrics = data["aggregate"]
    b3 = metrics["B3_DETERMINISTIC_JOINT"]
    b4 = metrics["B4_ROBUST_JOINT"]
    bounds = data["reliability_bounds"]["B4_ROBUST_JOINT"]
    paired = data["paired_B4_minus_B3_joint_qos"]

    assert bounds["conditional_successes"] == bounds["conditional_trials"] == 1468
    assert b4["selection_rate"] < b3["selection_rate"]
    assert b4["joint_qos_probability_conditional_on_selection"] > b3["joint_qos_probability_conditional_on_selection"]
    assert b4["joint_qos_probability_unconditional"] < b3["joint_qos_probability_unconditional"]
    assert math.isclose(
        paired["mean_paired_difference"],
        b4["joint_qos_probability_unconditional"] - b3["joint_qos_probability_unconditional"],
        abs_tol=1e-12,
    )
    assert paired["ci_low"] < paired["mean_paired_difference"] < paired["ci_high"] < 0
    assert paired["n_pairs"] == 12000
    assert paired["bootstrap_resamples"] == 10000
