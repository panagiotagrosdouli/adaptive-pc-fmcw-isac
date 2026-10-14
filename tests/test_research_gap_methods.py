import pytest
from pcfmcw_isac.research_gap_methods import (
    hoeffding_upper_failures, calibrate_fixed_thresholds, anytime_bernoulli_decision
)

def test_bounds():
    assert hoeffding_upper_failures(0, 10000, .05) < .05
    assert hoeffding_upper_failures(10, 10, .05) == 1.0

def test_all_failure_calibration_abstains():
    result = calibrate_fixed_thresholds([.3,.7,.9], [False]*3, thresholds=[.2,.5,.8])
    assert result.threshold is None

def test_independent_large_success_calibration():
    r = calibrate_fixed_thresholds([.95]*10000, [True]*10000,
        thresholds=[.9], risk_target=.05)
    assert r.threshold == .9 and r.selected == 10000

def test_sequential_reject_bad_action():
    r = anytime_bernoulli_decision([False]*200, min_draws=32)
    assert r.rejected and r.draws >= 32

def test_sequential_conservative_near_one():
    r = anytime_bernoulli_decision([True]*512)
    assert not r.accepted

def test_invalid_data():
    with pytest.raises(ValueError):
        calibrate_fixed_thresholds([], [], thresholds=[.5])
