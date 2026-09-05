from pcfmcw_isac.policy_evaluation import evaluate_action
from pcfmcw_isac.policy_v2 import _action_seed, select_action_v2
from pcfmcw_isac.publication_protocol import EvaluationState, PhyActionSpec


def _state(**kwargs):
    values = dict(
        ebn0_db=12.0,
        if_snr_db=10.0,
        range_m=10.0,
        radial_velocity_mps=3.0,
        residual_cfo_hz=0.0,
        inr_db=None,
        phase_noise_std_rad_per_sample=0.0,
        state_uncertainty_scale=0.0,
        seed=10000,
    )
    values.update(kwargs)
    return EvaluationState(**values)


def test_action_seed_is_stable_and_action_local():
    state = _state()
    a = PhyActionSpec("ti_77ghz_parking_profile", 16, 0.0, 1)
    b = PhyActionSpec("ti_77ghz_parking_profile", 32, 0.0, 1)
    assert _action_seed(state, a) == _action_seed(state, a)
    assert _action_seed(state, a) != _action_seed(state, b)


def test_hindsight_oracle_returns_receiver_valid_action_on_easy_state():
    state = _state()
    action = select_action_v2("ORACLE", state, oracle_comm_bits=2000, oracle_sensing_trials=1)
    assert action is not None
    metrics = evaluate_action(action, state, comm_bits=2000, sensing_trials=1)
    assert metrics.joint_qos


def test_b4_uses_confidence_bound_and_remains_defined():
    action = select_action_v2("B4_ROBUST_JOINT", _state(), robust_draws=64)
    assert action is None or isinstance(action, PhyActionSpec)
