from pcfmcw_isac.research_extensions import (
    run_action_space_sensitivity,
    run_reliability_calibration,
)


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
            "false_feasible_rate",
            "false_infeasible_rate",
            "decision_disagreement_rate",
            "selected_action_disagreement_rate",
            "finite_selection_rate",
            "reference_selection_rate",
        ):
            assert 0.0 <= summary[key] <= 1.0


def test_action_space_sensitivity_contains_full_and_restricted_variants():
    out = run_action_space_sensitivity(
        seeds=range(10000, 10001),
        comm_bits=500,
        sensing_trials=1,
        robust_draws=16,
    )
    expected = {
        "FULL",
        "HIGH_MOBILITY_PROFILE_ONLY",
        "PARKING_PROFILE_ONLY",
        "NO_REPETITION",
        "FIXED_32_CHIPS",
        "NO_POWER_BACKOFF",
    }
    assert set(out["summary"]) == expected
    assert set(out["action_frequency"]) == expected
    for summary in out["summary"].values():
        assert summary["n"] > 0
        assert 0.0 <= summary["selection_rate"] <= 1.0
