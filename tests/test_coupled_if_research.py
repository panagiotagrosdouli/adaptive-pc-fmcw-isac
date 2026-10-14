from pcfmcw_isac.coupled_if_research import (
    IFPassband,coupled_physics,nominal_complex_if,nominal_positive_if
)
from pcfmcw_isac.profiles import high_mobility_profile
import pytest

def test_coupled_bound_exposes_positive_doppler_boundary():
    p=high_mobility_profile()
    result=coupled_physics(p,p.positive_if_max_range_m,10.0,
        passband=nominal_complex_if(p))
    assert not result.valid
    assert "BEAT_OUTSIDE_IF_PASSBAND" in result.reasons

def test_complex_and_positive_if_conventions_differ_for_negative_beat():
    p=high_mobility_profile()
    v=-15.0
    r=0.0
    assert coupled_physics(p,r,v,passband=nominal_complex_if(p)).valid
    assert not coupled_physics(p,r,v,passband=nominal_positive_if(p)).valid

def test_guard_band_can_reject_boundary():
    p=high_mobility_profile()
    f=p.sample_rate_hz
    assert coupled_physics(p,30,10,passband=IFPassband(-f/2,f/2,0)).valid
    assert not coupled_physics(p,30,10,passband=IFPassband(-f/2,f/2,f/4)).valid

def test_invalid_passband_guard():
    with pytest.raises(ValueError):
        IFPassband(-10,10,11).validate()
