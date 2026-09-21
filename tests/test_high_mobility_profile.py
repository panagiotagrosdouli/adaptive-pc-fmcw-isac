import numpy as np

from pcfmcw_isac.if_model import RadarProfile, Target, synthesize_if, estimate_single_target


def high_mobility_profile() -> RadarProfile:
    return RadarProfile(
        carrier_hz=77e9,
        bandwidth_hz=1e9,
        chirp_duration_s=20e-6,
        chirp_repetition_s=20e-6,
        sample_rate_hz=37.5e6,
        samples_per_chirp=750,
        n_chirps=128,
    )


def test_high_mobility_capability_limits():
    p = high_mobility_profile()
    assert np.isclose(p.range_resolution_m, 0.149896229, rtol=1e-6)
    assert np.isclose(p.positive_if_max_range_m, 56.211085875, rtol=1e-6)
    assert np.isclose(p.max_unambiguous_velocity_mps, 48.6676068182, rtol=1e-6)


def test_published_5100hz_one_way_doppler_speed_is_inside_high_mobility_profile():
    c0 = 299_792_458.0
    speed = 5100.0 * c0 / 77e9
    p = high_mobility_profile()
    assert speed < p.max_unambiguous_velocity_mps


def test_high_mobility_target_recovery():
    p = high_mobility_profile()
    target = Target(range_m=20.28, radial_velocity_mps=19.8563835818)
    y = synthesize_if(p, [target], snr_db=10.0, rng=np.random.default_rng(20260905))
    r_hat, v_hat = estimate_single_target(p, y, range_fft=4096, doppler_fft=512)
    assert abs(r_hat - target.range_m) < p.range_resolution_m
    assert abs(v_hat - target.radial_velocity_mps) < p.velocity_resolution_mps
