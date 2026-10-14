"""Regression diagnostics without modifying frozen policy semantics."""
from pcfmcw_isac.if_model import C0
from pcfmcw_isac.profiles import high_mobility_profile, short_range_profile
from pcfmcw_isac.if_feasibility_diagnostic import diagnose_if


def test_near_positive_if_limit_with_positive_doppler_exposes_joint_boundary():
    p = high_mobility_profile()
    r = p.positive_if_max_range_m
    v = p.max_unambiguous_velocity_mps * 0.9
    result = diagnose_if(p, r, v)
    assert result.canonical_gate_supported
    assert result.beat_hz > result.nyquist_hz
    assert not result.sampled_if_supported
    assert result.gate_mismatch


def test_typical_short_range_state_remains_supported():
    result = diagnose_if(short_range_profile(), 10.0, 3.0)
    assert result.canonical_gate_supported
    assert result.sampled_if_supported
    assert not result.gate_mismatch


def test_negative_doppler_shifts_positive_if_limit_inward_or_outward():
    p = high_mobility_profile()
    r = p.positive_if_max_range_m
    result = diagnose_if(p, r, -0.5 * p.max_unambiguous_velocity_mps)
    assert result.canonical_gate_supported
    assert result.sampled_if_supported
