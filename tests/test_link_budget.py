import numpy as np

from pcfmcw_isac.link_budget import (
    free_space_path_loss_db,
    communication_received_power_dbm,
    thermal_noise_dbm,
    monostatic_radar_received_power_dbm,
)


def test_published_20p28m_77ghz_free_space_loss_cross_check():
    # Published JCRS example reports 96.31 dB one-way attenuation without antenna gains.
    fspl = free_space_path_loss_db(20.28, 77e9)
    assert np.isclose(fspl, 96.3189567386, atol=1e-9)
    assert abs(fspl - 96.31) < 0.02


def test_zero_gain_received_power_is_tx_minus_fspl():
    pr = communication_received_power_dbm(12.0, 20.28, 77e9)
    assert np.isclose(pr, 12.0 - 96.3189567386, atol=1e-9)


def test_thermal_noise_reference_at_1mhz_and_14db_nf():
    n = thermal_noise_dbm(1e6, 14.0)
    assert np.isclose(n, -99.9751871942, atol=1e-9)


def test_radar_received_power_decreases_12db_when_range_doubles():
    p1 = monostatic_radar_received_power_dbm(12.0, 10.0, 77e9, 15.0)
    p2 = monostatic_radar_received_power_dbm(12.0, 20.0, 77e9, 15.0)
    assert np.isclose(p1 - p2, 12.0411998266, atol=1e-9)
