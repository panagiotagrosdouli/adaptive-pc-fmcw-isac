import pytest

from pcfmcw_isac.statistics import reliability_target_satisfied, wilson_lower_bound


def test_wilson_lower_bound_is_conservative():
    assert wilson_lower_bound(95, 100) < 0.95
    assert wilson_lower_bound(100, 100) < 1.0


def test_reliability_requires_confidence_bound_not_point_estimate():
    assert not reliability_target_satisfied(95, 100, target=0.95)
    assert reliability_target_satisfied(512, 512, target=0.95)


def test_frozen_95pct_target_is_structurally_unattainable_at_32_draws():
    lower = wilson_lower_bound(32, 32, confidence=0.95)
    assert lower == pytest.approx(0.9220429, abs=1e-6)
    assert not reliability_target_satisfied(32, 32, target=0.95, confidence=0.95)


def test_frozen_finite_draw_minimum_success_counts():
    expected = {
        64: 64,
        128: 126,
        256: 249,
        512: 495,
    }
    for trials, minimum_successes in expected.items():
        assert reliability_target_satisfied(
            minimum_successes,
            trials,
            target=0.95,
            confidence=0.95,
        )
        assert not reliability_target_satisfied(
            minimum_successes - 1,
            trials,
            target=0.95,
            confidence=0.95,
        )


def test_all_success_maximum_bounds_match_frozen_calibration():
    expected = {
        32: 0.9220429,
        64: 0.9594405,
        128: 0.9793005,
        256: 0.9895420,
        512: 0.9947435,
    }
    for trials, lower_expected in expected.items():
        assert wilson_lower_bound(trials, trials, confidence=0.95) == pytest.approx(
            lower_expected, abs=1e-6
        )


def test_invalid_counts_rejected():
    with pytest.raises(ValueError):
        wilson_lower_bound(2, 1)
    with pytest.raises(ValueError):
        wilson_lower_bound(0, 0)
