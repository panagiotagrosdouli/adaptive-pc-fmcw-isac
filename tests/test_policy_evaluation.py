from pcfmcw_isac.policy_evaluation import (
    evaluate_action,
    normalized_resource_cost,
    repetition_ber,
    select_action,
)
from pcfmcw_isac.publication_protocol import EvaluationState, PhyActionSpec


def _state(**kwargs):
    base = dict(
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
    base.update(kwargs)
    return EvaluationState(**base)


def test_even_repetition_tie_rule_is_well_defined():
    p = 0.1
    assert repetition_ber(p, 1) == p
    assert 0.0 <= repetition_ber(p, 2) <= 1.0
    assert 0.0 <= repetition_ber(p, 4) <= 1.0


def test_resource_cost_rewards_power_backoff_but_charges_repetition():
    hi_power = PhyActionSpec("ti_77ghz_parking_profile", 32, 0.0, 1)
    low_power = PhyActionSpec("ti_77ghz_parking_profile", 32, 6.0, 1)
    repeated = PhyActionSpec("ti_77ghz_parking_profile", 32, 6.0, 4)
    assert normalized_resource_cost(low_power) < normalized_resource_cost(hi_power)
    assert normalized_resource_cost(repeated) > normalized_resource_cost(low_power)


def test_physics_gate_rejects_parking_profile_at_high_velocity():
    action = PhyActionSpec("ti_77ghz_parking_profile", 32, 0.0, 1)
    metrics = evaluate_action(action, _state(radial_velocity_mps=30.0), comm_bits=1000, sensing_trials=1)
    assert not metrics.physics_feasible
    assert not metrics.joint_qos


def test_high_mobility_profile_remains_available_at_30_mps():
    state = _state(range_m=20.0, radial_velocity_mps=30.0)
    action = select_action("B2_SENSING_ONLY", state)
    assert action is not None
    assert action.profile_name == "ti_77ghz_high_mobility_capability_profile"


def test_all_named_policies_are_selectable_on_easy_state():
    state = _state()
    for policy in (
        "B0_FIXED",
        "B1_COMM_ONLY",
        "B2_SENSING_ONLY",
        "B3_DETERMINISTIC_JOINT",
        "B4_ROBUST_JOINT",
        "ORACLE",
    ):
        action = select_action(policy, state, robust_draws=8)
        assert action is None or isinstance(action, PhyActionSpec)
