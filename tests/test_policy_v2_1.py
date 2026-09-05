from pcfmcw_isac.policy_v2_1 import _predict_metrics_v2_1, select_action_v2_1
from pcfmcw_isac.publication_protocol import EvaluationState, PhyActionSpec


def _state(**kwargs):
    values = dict(
        ebn0_db=16.0,
        if_snr_db=-20.0,
        range_m=10.0,
        radial_velocity_mps=0.0,
        residual_cfo_hz=0.0,
        inr_db=None,
        phase_noise_std_rad_per_sample=0.0,
        state_uncertainty_scale=0.0,
        seed=10000,
    )
    values.update(kwargs)
    return EvaluationState(**values)


def test_v2_1_sensing_guard_degrades_at_low_if_snr():
    action = PhyActionSpec("ti_77ghz_parking_profile", 32, 0.0, 1)
    feasible, comm_ok, sensing_ok, _ = _predict_metrics_v2_1(action, _state())
    assert feasible
    assert comm_ok
    assert not sensing_ok


def test_v2_1_sensing_guard_recovers_at_high_if_snr():
    action = PhyActionSpec("ti_77ghz_parking_profile", 32, 0.0, 1)
    feasible, _, sensing_ok, _ = _predict_metrics_v2_1(action, _state(if_snr_db=10.0))
    assert feasible
    assert sensing_ok


def test_comm_only_and_joint_no_longer_collapse_when_sensing_is_limiting():
    state = _state()
    b1 = select_action_v2_1("B1_COMM_ONLY", state, robust_draws=64)
    b3 = select_action_v2_1("B3_DETERMINISTIC_JOINT", state, robust_draws=64)
    assert b1 is not None
    assert b3 is None


def test_oracle_remains_receiver_valid_on_easy_state():
    state = _state(if_snr_db=10.0)
    oracle = select_action_v2_1(
        "ORACLE", state, robust_draws=64, oracle_comm_bits=2000, oracle_sensing_trials=1
    )
    assert oracle is not None
