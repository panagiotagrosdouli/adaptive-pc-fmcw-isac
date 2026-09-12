from pcfmcw_isac.research_analysis import (
    distribution_shift_statistics,
    failure_taxonomy,
    paired_bootstrap_binary_difference,
)


def _row(policy, seed, scenario, draw, success, family="TEST"):
    return {
        "policy": policy,
        "seed": seed,
        "scenario_id": scenario,
        "truth_draw": draw,
        "family": family,
        "selected_action": {"profile_name": "p"},
        "physics_feasible": True,
        "joint_qos": success,
        "ber": 0.0 if success else 0.1,
        "effective_rate_bps": 1e6,
        "range_rmse_m": 0.1,
        "velocity_rmse_mps": 0.1,
        "state_category": "SELECTED",
    }


def test_paired_bootstrap_difference_uses_declared_episode_units():
    records = [
        _row("A", 1, 0, 0, True), _row("B", 1, 0, 0, False),
        _row("A", 2, 0, 0, True), _row("B", 2, 0, 0, True),
    ]
    out = paired_bootstrap_binary_difference(
        records,
        policy_a="A",
        policy_b="B",
        key_fields=("seed", "scenario_id", "truth_draw"),
        n_resamples=200,
        seed=7,
    )
    assert out["paired_units"] == 2
    assert out["mean_difference_a_minus_b"] == 0.5
    assert out["wins_a"] == 1
    assert out["ties"] == 1
    assert out["wins_b"] == 0


def test_paired_bootstrap_rejects_unpaired_data():
    records = [_row("A", 1, 0, 0, True), _row("B", 2, 0, 0, False)]
    try:
        paired_bootstrap_binary_difference(records, policy_a="A", policy_b="B", n_resamples=10)
    except ValueError as exc:
        assert "no paired observations" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_distribution_shift_statistics_reports_b4_minus_b3():
    records = [
        _row("B4_ROBUST_JOINT", 1, 0, 0, True, "HEAVY_TAILED_T3"),
        _row("B3_DETERMINISTIC_JOINT", 1, 0, 0, False, "HEAVY_TAILED_T3"),
    ]
    stats = distribution_shift_statistics({"records": records}, n_resamples=20)
    assert stats["HEAVY_TAILED_T3"]["mean_difference_a_minus_b"] == 1.0


def test_failure_taxonomy_distinguishes_abstention_and_receiver_failure():
    rows = [
        {"policy": "B4", "selected_action": None, "state_category": "POLICY_ABSTENTION", "joint_qos": False},
        _row("B4", 1, 0, 0, False),
        _row("B4", 2, 0, 0, True),
    ]
    out = failure_taxonomy(rows)
    assert out["global"]["POLICY_ABSTENTION"] == 1
    assert out["global"]["COMM_BER"] == 1
    assert out["global"]["SUCCESS"] == 1
