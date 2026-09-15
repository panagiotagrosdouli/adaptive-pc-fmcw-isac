from pcfmcw_isac.paper1_physics_gate_ablation import (
    action_is_physically_valid,
    classify_state,
    nominal_state,
    run_paper1_physics_gate_ablation,
    select_nominal,
)


def test_gated_selector_never_returns_invalid_action_on_grid():
    result = run_paper1_physics_gate_ablation()
    for row in result["records"]:
        if row["gated_action"] is not None:
            assert row["gated_physics_valid"]


def test_ungated_selector_can_choose_physically_invalid_parking_action():
    state = nominal_state(30.0, 20.0)
    action = select_nominal(state, use_physics_gate=False)
    assert action is not None
    assert not action_is_physically_valid(action, state)
    assert classify_state(state, action) == "INVALID_SELECTED_ACTION"


def test_gate_recovers_high_mobility_alternative():
    state = nominal_state(30.0, 20.0)
    action = select_nominal(state, use_physics_gate=True)
    assert action is not None
    assert action.profile_name == "ti_77ghz_high_mobility_capability_profile"
    assert action_is_physically_valid(action, state)


def test_physical_infeasibility_is_not_policy_abstention():
    state = nominal_state(60.0, 60.0)
    assert select_nominal(state, use_physics_gate=True) is None
    assert classify_state(state, None) == "PHYSICALLY_INFEASIBLE_STATE"


def test_boundary_aware_summary_is_deterministic_and_consistent():
    a = run_paper1_physics_gate_ablation()
    b = run_paper1_physics_gate_ablation()
    assert a == b
    s = a["summary"]
    assert s["total_states"] == 238
    assert s["physically_feasible_states"] == 132
    assert s["physically_infeasible_states"] == 106
    assert s["gated_selected"] == 132
    assert s["gated_invalid_selections"] == 0
    assert s["ungated_selected"] == 238
    assert s["ungated_invalid_selections"] == 220
    assert s["selection_changed_cases"] == 220
    assert s["ungated_invalid_gated_valid_alternative_cases"] == 114
    assert abs(s["ungated_invalid_selection_rate_conditional"] - 220 / 238) < 1e-12
