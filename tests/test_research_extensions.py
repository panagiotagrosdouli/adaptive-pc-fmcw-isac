from pcfmcw_isac.part_b_completion import _robust_success_table
from pcfmcw_isac.policy_evaluation import _estimated_state
from pcfmcw_isac.publication_benchmark import benchmark_states
from pcfmcw_isac.research_extensions import (
    _cumulative_robust_tables,
    run_action_space_sensitivity,
    run_distribution_shift,
    run_reliability_calibration,
)


def test_cumulative_calibration_exactly_matches_direct_prefix_sampler():
    state = benchmark_states(10000)[0]
    estimated = _estimated_state(state, state.state_uncertainty_scale)
    cumulative = _cumulative_robust_tables(state, estimated, (8, 16, 32))
    for draws in (8, 16, 32):
        direct = _robust_success_table(state, estimated, robust_draws=draws)
        assert cumulative[draws] == direct


def test_reliability_calibration_smoke_and_rates_are_bounded():
    out = run_reliability_calibration(
        seeds=range(10000, 10001),
        robust_draws_values=(8, 16),
        reference_draws=32,
        target=0.95,
    )
    assert set(out["summary"]) == {"8", "16"}
    for summary in out["summary"].values():
        assert summary["n"] > 0
        for key in (
            "false_feasible_rate", "false_infeasible_rate", "decision_disagreement_rate",
            "selected_action_disagreement_rate", "finite_selection_rate", "reference_selection_rate",
        ):
            assert 0.0 <= summary[key] <= 1.0


def test_action_space_sensitivity_contains_full_and_restricted_variants():
    out = run_action_space_sensitivity(
        seeds=range(10000, 10001), comm_bits=500, sensing_trials=1, robust_draws=16,
    )
    expected = {"FULL", "HIGH_MOBILITY_PROFILE_ONLY", "PARKING_PROFILE_ONLY", "NO_REPETITION", "FIXED_32_CHIPS", "NO_POWER_BACKOFF"}
    assert set(out["summary"]) == expected
    assert set(out["action_frequency"]) == expected
    for summary in out["summary"].values():
        assert summary["n"] > 0
        assert 0.0 <= summary["selection_rate"] <= 1.0


def test_distribution_shift_uses_equal_policy_sample_counts_and_expected_families():
    out = run_distribution_shift(
        seeds=range(10000, 10001), comm_bits=500, sensing_trials=1,
        robust_draws=16, truth_draws_per_state=1,
    )
    expected = {"NOMINAL_GAUSSIAN", "HEAVY_TAILED_T3", "CORRELATED_SNR_INTERFERENCE", "BIASED_STATE_ESTIMATE"}
    assert set(out["summary"]) == expected
    for family in expected:
        b3 = out["summary"][family]["B3_DETERMINISTIC_JOINT"]
        b4 = out["summary"][family]["B4_ROBUST_JOINT"]
        assert b3["n"] == b4["n"] > 0
        assert 0.0 <= b3["joint_qos_probability_unconditional"] <= 1.0
        assert 0.0 <= b4["joint_qos_probability_unconditional"] <= 1.0
