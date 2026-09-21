import numpy as np

from pcfmcw_isac.comm_reference import CommConfig, dbpsk_awgn_theory, simulate_ber


def test_phase_code_rates_are_physically_derived_from_chirp_timing():
    assert np.isclose(CommConfig(chips_per_chirp=16).raw_bit_rate_bps, 138169.2573402418)
    assert np.isclose(CommConfig(chips_per_chirp=32).raw_bit_rate_bps, 276338.5146804836)
    assert np.isclose(CommConfig(chips_per_chirp=64).raw_bit_rate_bps, 552677.0293609672)


def test_dbpsk_awgn_matches_theory_at_zero_db():
    measured = simulate_ber(0.0, 100_000, seed=20260905)
    theory = float(dbpsk_awgn_theory(0.0))
    assert abs(measured - theory) < 0.012


def test_dbpsk_awgn_matches_theory_at_four_db():
    measured = simulate_ber(4.0, 150_000, seed=20260906)
    theory = float(dbpsk_awgn_theory(4.0))
    assert abs(measured - theory) < 0.006
