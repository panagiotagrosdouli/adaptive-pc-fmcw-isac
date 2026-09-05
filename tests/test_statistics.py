import pytest

from pcfmcw_isac.statistics import reliability_target_satisfied, wilson_lower_bound


def test_wilson_lower_bound_is_conservative():
    assert wilson_lower_bound(95, 100) < 0.95
    assert wilson_lower_bound(100, 100) < 1.0


def test_reliability_requires_confidence_bound_not_point_estimate():
    assert not reliability_target_satisfied(95, 100, target=0.95)
    assert reliability_target_satisfied(512, 512, target=0.95)


def test_invalid_counts_rejected():
    with pytest.raises(ValueError):
        wilson_lower_bound(2, 1)
    with pytest.raises(ValueError):
        wilson_lower_bound(0, 0)
