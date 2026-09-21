import importlib.util
from pathlib import Path
import sys

import numpy as np

P = Path(__file__).with_name("statistics.py")
SPEC = importlib.util.spec_from_file_location("stage07_statistics_test", P)
M = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = M
SPEC.loader.exec_module(M)


def records():
    return [
        {"scenario_id": "a", "policy": "new", "seed": 1, "score": 4},
        {"scenario_id": "a", "policy": "new", "seed": 2, "score": 6},
        {"scenario_id": "a", "policy": "base", "seed": 1, "score": 3},
        {"scenario_id": "a", "policy": "base", "seed": 2, "score": 3},
        {"scenario_id": "b", "policy": "new", "seed": 1, "score": 8},
        {"scenario_id": "b", "policy": "base", "seed": 1, "score": 5},
    ]


def test_repeated_seeds_collapse_within_scenario():
    clusters, delta = M.paired_deltas(records(), "policy", "score", "new", "base", True)
    assert clusters == ["a", "b"]
    np.testing.assert_allclose(delta, [2, 3])


def test_lower_is_better_is_oriented_as_improvement():
    _, delta = M.paired_deltas(records(), "policy", "score", "new", "base", False)
    np.testing.assert_allclose(delta, [-2, -3])


def test_unpaired_scenarios_fail_closed():
    bad = records()[:-1]
    try:
        M.paired_deltas(bad, "policy", "score", "new", "base", True)
    except ValueError as error:
        assert "unpaired" in str(error)
    else:
        raise AssertionError("unpaired comparison was accepted")


def test_holm_is_monotone_in_sorted_p_order():
    adjusted = M.holm_adjust([0.04, 0.01, 0.03])
    assert adjusted == [0.06, 0.03, 0.06]


def test_zero_delta_has_neutral_tests_and_reproducible_ci():
    result = M.analyze_delta(np.zeros(6), repetitions=200, seed=7)
    assert result.wilcoxon_p == result.paired_t_p == 1
    assert result.ci_low == result.ci_high == 0
    assert result.win_fraction == 0
