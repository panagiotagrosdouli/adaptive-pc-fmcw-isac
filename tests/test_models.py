from pcfmcw_isac.models import PhyConfig, QoS, State
from pcfmcw_isac.physics import dbpsk_ber, range_rmse_m


def test_higher_snr_improves_surrogate_metrics():
    c = PhyConfig(1.0, 32, 32, 1)
    low = State(0.0, 0.0)
    high = State(10.0, 0.0)
    assert dbpsk_ber(high, c) < dbpsk_ber(low, c)
    assert range_rmse_m(high, c) < range_rmse_m(low, c)


def test_more_chirps_improve_range_proxy():
    s = State(5.0, 0.0)
    a = PhyConfig(1.0, 32, 16, 1)
    b = PhyConfig(1.0, 32, 64, 1)
    assert range_rmse_m(s, b) < range_rmse_m(s, a)


def test_qos_defaults_are_valid():
    q = QoS()
    assert 0 < q.joint_success_probability <= 1
    assert q.ber_max > 0
