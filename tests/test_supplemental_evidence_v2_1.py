from dataclasses import replace

from pcfmcw_isac.publication_benchmark import benchmark_states
from pcfmcw_isac.publication_protocol import EvaluationState
from pcfmcw_isac.supplemental_evidence_v2_1 import (
    _state_category,
    run_extended_ablations,
    run_physics_only_maps,
    run_runtime_benchmark,
    run_same_seed_policy_check,
)


def test_physics_map_exposes_profile_boundaries():
    out = run_physics_only_maps()
    limits = out["derived_profile_limits"]
    parking = limits["ti_77ghz_parking_profile"]
    mobile = limits["ti_77ghz_high_mobility_capability_profile"]
    assert parking["max_unambiguous_velocity_mps"] < mobile["max_unambiguous_velocity_mps"]
    assert parking["positive_if_max_range_m"] < mobile["positive_if_max_range_m"]
    assert any(not c["any_profile_feasible"] for c in out["cells"])
    assert any(c["any_profile_feasible"] for c in out["cells"])


def test_state_category_separates_abstention_from_physics_infeasibility():
    feasible = benchmark_states(10000)[0]
    assert _state_category(feasible, None) == "POLICY_ABSTENTION"
    impossible = replace(feasible, range_m=1000.0)
    assert _state_category(impossible, None) == "PHYSICALLY_INFEASIBLE"


def test_same_seed_comparison_is_paired_and_includes_all_policies():
    out = run_same_seed_policy_check(seeds=[10000], comm_bits=500, sensing_trials=1, robust_draws=16)
    assert set(out["aggregate"]) == {
        "B0_FIXED", "B1_COMM_ONLY", "B2_SENSING_ONLY",
        "B3_DETERMINISTIC_JOINT", "B4_ROBUST_JOINT", "ORACLE"
    }
    assert out["paired_B4_minus_B3"]["n_pairs"] == 12


def test_extended_ablations_have_requested_components():
    out = run_extended_ablations(seeds=[10000], comm_bits=500, sensing_trials=1, robust_draws=16)
    assert set(out["summary"]) == {
        "FULL_B4", "NO_PHYSICS_GATE", "NO_STATE_UNCERTAINTY", "NO_JOINT_CONSTRAINT"
    }


def test_runtime_reports_latency_quantiles():
    out = run_runtime_benchmark(seeds=[10000], robust_draws_values=(8,), repetitions=1)
    b4 = out["summary"]["8"]["B4_ROBUST_JOINT"]
    assert b4["n"] == 12
    assert b4["median_us"] >= 0.0
    assert b4["p99_us"] >= b4["median_us"]
