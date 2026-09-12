from pcfmcw_isac.research_analysis import (
    distribution_shift_statistics,
    enrich_pareto,
    enrich_physics_map,
    failure_taxonomy,
    paired_bootstrap_binary_difference,
    pareto_partition,
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


def test_physics_map_enrichment_reports_range_and_velocity_rejections():
    raw = {
        "derived_profile_limits": {
            "p": {"positive_if_max_range_m": 20.0, "max_unambiguous_velocity_mps": 10.0}
        },
        "cells": [
            {"range_m": 30.0, "radial_velocity_mps": 15.0, "profiles": {"p": False}, "any_profile_feasible": False},
            {"range_m": 10.0, "radial_velocity_mps": 5.0, "profiles": {"p": True}, "any_profile_feasible": True},
        ],
    }
    out = enrich_physics_map(raw)
    failed = out["cells"][0]["profile_feasibility"]["p"]
    passed = out["cells"][1]["profile_feasibility"]["p"]
    assert failed["reasons"] == ["RANGE_UNSUPPORTED", "VELOCITY_AMBIGUOUS"]
    assert not failed["feasible"]
    assert passed == {"feasible": True, "reasons": []}


def _pareto_point(name, qos, rate, tx, rep, chips, adc, rr, vr):
    return {
        "name": name,
        "joint_qos_probability": qos,
        "mean_effective_rate_bps": rate,
        "tx_power_fraction": tx,
        "repetition_factor": rep,
        "chips_per_chirp": chips,
        "profile_adc_samples_per_frame": adc,
        "mean_range_rmse_m": rr,
        "mean_velocity_rmse_mps": vr,
    }


def test_pareto_partition_marks_strictly_worse_point_dominated():
    strong = _pareto_point("strong", 1.0, 2e5, 0.5, 1, 16, 1000, 0.2, 0.2)
    weak = _pareto_point("weak", 0.8, 1e5, 1.0, 2, 64, 2000, 0.5, 0.5)
    tradeoff = _pareto_point("tradeoff", 1.0, 3e5, 0.8, 1, 16, 1000, 0.2, 0.2)
    out = pareto_partition([strong, weak, tradeoff])
    assert out["n_points"] == 3
    assert out["n_dominated"] == 1
    assert out["dominated_points"][0]["name"] == "weak"
    assert {p["name"] for p in out["non_dominated_points"]} == {"strong", "tradeoff"}


def test_pareto_partition_prefers_lower_chip_occupancy_when_else_equal():
    low_chips = _pareto_point("low_chips", 1.0, 2e5, 0.5, 1, 16, 1000, 0.2, 0.2)
    high_chips = _pareto_point("high_chips", 1.0, 2e5, 0.5, 1, 64, 1000, 0.2, 0.2)
    out = pareto_partition([low_chips, high_chips])
    assert [p["name"] for p in out["non_dominated_points"]] == ["low_chips"]
    assert out["dominated_points"][0]["name"] == "high_chips"


def test_enrich_pareto_declares_empirical_claim_boundary():
    point = _pareto_point("only", 1.0, 2e5, 0.5, 1, 16, 1000, 0.2, 0.2)
    out = enrich_pareto({"physical_points": [point]})
    assert out["pareto"]["n_non_dominated"] == 1
    assert out["pareto"]["n_dominated"] == 0
    assert "realized B4-selected" in out["claim_boundary"]
