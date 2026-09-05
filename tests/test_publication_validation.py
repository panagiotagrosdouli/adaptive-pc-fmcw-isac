import math

from pcfmcw_isac.profiles import high_mobility_profile, short_range_profile
from pcfmcw_isac.publication_validation import (
    _comm_cfg,
    e1_waveform_sanity,
    simulate_dbpsk_impaired,
)


def test_e1_derived_physics_matches_expected_scales():
    rows = e1_waveform_sanity()
    sr = rows["ti_77ghz_parking_profile"]
    hm = rows["ti_77ghz_high_mobility_capability_profile"]

    assert math.isclose(sr["range_resolution_m"], 0.174704, rel_tol=2e-3)
    assert math.isclose(sr["max_unambiguous_velocity_mps"], 8.405, rel_tol=2e-3)
    assert math.isclose(hm["range_resolution_m"], 0.149896, rel_tol=2e-3)
    assert math.isclose(hm["max_unambiguous_velocity_mps"], 48.668, rel_tol=2e-3)


def test_profiles_have_consistent_sampling():
    for p in (short_range_profile(), high_mobility_profile()):
        p.validate()
        assert abs(p.sample_rate_hz * p.chirp_duration_s - p.samples_per_chirp) <= 0.5


def test_inr_is_defined_relative_to_noise_and_degrades_dbpsk():
    cfg = _comm_cfg("ti_77ghz_parking_profile", 32)
    clean = simulate_dbpsk_impaired(8.0, 50_000, cfg=cfg, inr_db=None, seed=1234)
    interfered = simulate_dbpsk_impaired(8.0, 50_000, cfg=cfg, inr_db=10.0, seed=1234)
    assert interfered > clean


def test_residual_cfo_degrades_reference_modem_at_khz_scale():
    cfg = _comm_cfg("ti_77ghz_parking_profile", 32)
    clean = simulate_dbpsk_impaired(8.0, 50_000, cfg=cfg, residual_frequency_hz=0.0, seed=4321)
    offset = simulate_dbpsk_impaired(8.0, 50_000, cfg=cfg, residual_frequency_hz=5000.0, seed=4321)
    assert offset > clean


def test_controlled_phase_noise_parameter_is_nonnegative():
    cfg = _comm_cfg("ti_77ghz_parking_profile", 32)
    try:
        simulate_dbpsk_impaired(
            8.0,
            100,
            cfg=cfg,
            phase_noise_std_rad_per_chip=-1e-3,
            seed=1,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("negative phase-noise innovation must be rejected")
