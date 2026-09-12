from pcfmcw_isac.research_sensitivity import (
    CounterfactualQoS,
    _score,
    default_qos_variants,
    run_qos_threshold_sensitivity,
)


def test_counterfactual_qos_scoring_respects_thresholds():
    row = {
        "selected_action": {"profile_name": "p"},
        "physics_feasible": True,
        "ber": 5e-4,
        "effective_rate_bps": 150_000.0,
        "range_rmse_m": 0.75,
        "velocity_rmse_mps": 0.75,
    }
    baseline = CounterfactualQoS("B", 1e-3, 1e5, 1.0, 1.0)
    strict = CounterfactualQoS("S", 1e-4, 2e5, 0.5, 0.5)
    assert _score(row, baseline)
    assert not _score(row, strict)


def test_default_qos_variants_include_strict_and_relaxed_joint_cases():
    names = {q.name for q in default_qos_variants()}
    assert {"BASELINE", "STRICT_JOINT", "RELAXED_JOINT"} <= names


def test_qos_sensitivity_preserves_selection_rate_across_counterfactual_thresholds():
    out = run_qos_threshold_sensitivity(
        seeds=range(10000, 10001),
        comm_bits=500,
        sensing_trials=1,
        robust_draws=16,
        variants=(
            CounterfactualQoS("BASE", 1e-3, 1e5, 1.0, 1.0),
            CounterfactualQoS("RELAX", 1e-2, 5e4, 2.0, 2.0),
        ),
    )
    for policy in ("B3_DETERMINISTIC_JOINT", "B4_ROBUST_JOINT"):
        assert out["summary"]["BASE"][policy]["selection_rate"] == out["summary"]["RELAX"][policy]["selection_rate"]
        assert out["summary"]["RELAX"][policy]["counterfactual_joint_qos_unconditional"] >= out["summary"]["BASE"][policy]["counterfactual_joint_qos_unconditional"]
