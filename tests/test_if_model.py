import numpy as np

from pcfmcw_isac.if_model import RadarProfile, Target, synthesize_if, estimate_single_target
from pcfmcw_isac.profiles import high_mobility_profile, short_range_profile


def test_ti_profile_derived_limits():
    p = short_range_profile()
    assert np.isclose(p.slope_hz_per_s, 40e12, rtol=1e-12)
    assert np.isclose(p.range_resolution_m, 0.1747042296, rtol=1e-6)
    assert np.isclose(p.positive_if_max_range_m, 18.737028625, rtol=1e-9)
    assert np.isclose(p.velocity_resolution_mps, 0.2626705895, rtol=1e-6)
    assert np.isclose(p.max_unambiguous_velocity_mps, 8.4054588632, rtol=1e-6)


def test_composite_profile_can_derive_slope_from_bandwidth_and_duration():
    p = high_mobility_profile()
    assert p.explicit_slope_hz_per_s is None
    assert np.isclose(p.slope_hz_per_s, 50e12, rtol=1e-12)


def test_noise_free_single_target_recovery_is_within_fft_resolution():
    p = RadarProfile()
    y = synthesize_if(p, [Target(range_m=10.0, radial_velocity_mps=3.0)])
    r_hat, v_hat = estimate_single_target(p, y)
    assert abs(r_hat - 10.0) < p.range_resolution_m
    assert abs(v_hat - 3.0) < p.velocity_resolution_mps


def test_seeded_20db_single_target_recovery():
    p = RadarProfile()
    rng = np.random.default_rng(20260905)
    y = synthesize_if(p, [Target(range_m=15.0, radial_velocity_mps=-3.0)], snr_db=20.0, rng=rng)
    r_hat, v_hat = estimate_single_target(p, y)
    assert abs(r_hat - 15.0) < p.range_resolution_m
    assert abs(v_hat + 3.0) < p.velocity_resolution_mps
