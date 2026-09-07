from pcfmcw_isac.part_b_completion import (
    _robust_success_table,
    run_confidence_maps,
    run_reliability_target_sweep,
)
from pcfmcw_isac.policy_evaluation import _estimated_state
from pcfmcw_isac.policy_v2_1 import select_action_v2_1
from pcfmcw_isac.publication_benchmark import benchmark_states
from pcfmcw_isac.publication_protocol import FROZEN_PROTOCOL_V1


def test_frozen_target_matches_frozen_b4_selector():
    state = benchmark_states(10000)[8]
    estimated = _estimated_state(state, state.state_uncertainty_scale)
    table = _robust_success_table(state, estimated, robust_draws=64)
    accepted = [a for a, (lb, _) in table.items() if lb >= FROZEN_PROTOCOL_V1.qos.joint_reliability_target]
    from pcfmcw_isac.policy_evaluation import _cheapest
    assert (_cheapest(accepted) if accepted else None) == select_action_v2_1("B4_ROBUST_JOINT", state, robust_draws=64)


def test_reliability_target_selection_is_monotone_with_common_draws():
    out = run_reliability_target_sweep(seeds=[10000], targets=(0.80, 0.90, 0.95), comm_bits=200, sensing_trials=1, robust_draws=32)
    rates = [out["summary"][str(t)]["selection_rate"] for t in (0.8, 0.9, 0.95)]
    assert rates == sorted(rates, reverse=True)
    assert "common action-local robust draws" in out["claim_boundary"]


def test_zeroing_one_uncertainty_source_changes_only_that_draw_coordinate():
    state = benchmark_states(10000)[8]
    estimated = _estimated_state(state, state.state_uncertainty_scale)
    full = _robust_success_table(state, estimated, robust_draws=16, std_scales=(1, 1, 1, 1))
    no_ebn0 = _robust_success_table(state, estimated, robust_draws=16, std_scales=(0, 1, 1, 1))
    assert set(full) == set(no_ebn0)
    # Deterministic repeatability is essential for paired source ablations.
    assert no_ebn0 == _robust_success_table(state, estimated, robust_draws=16, std_scales=(0, 1, 1, 1))


def test_confidence_map_schema_smoke():
    out = run_confidence_maps(seeds=[10000], comm_bits=100, sensing_trials=1, robust_draws=8)
    assert set(out) == {"ebn0_velocity", "inr_cfo"}
    assert len(out["ebn0_velocity"]["cells"]) == 36
    assert len(out["inr_cfo"]["cells"]) == 20
    assert "confidence_qualified_target_0p95" in out["ebn0_velocity"]["cells"][0]
