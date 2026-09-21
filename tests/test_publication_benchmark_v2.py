from pcfmcw_isac.publication_benchmark_v2 import (
    aggregate_policy_metrics_v2,
    feasible_region_slice,
    pareto_front,
    physical_resource_vector,
    run_paired_benchmark_v2,
    run_e11_ablations,
)
from pcfmcw_isac.publication_protocol import EvaluationState, PhyActionSpec


def _state(**kwargs):
    values = dict(
        ebn0_db=12.0,
        if_snr_db=0.0,
        range_m=20.0,
        radial_velocity_mps=10.0,
        residual_cfo_hz=500.0,
        inr_db=None,
        phase_noise_std_rad_per_sample=0.001,
        state_uncertainty_scale=0.5,
        seed=10000,
    )
    values.update(kwargs)
    return EvaluationState(**values)


def test_physical_resource_vector_is_interpretable():
    action = PhyActionSpec("ti_77ghz_high_mobility_capability_profile", 32, 3.0, 2)
    rv = physical_resource_vector(action)
    assert 0.0 < rv["tx_power_fraction"] < 1.0
    assert rv["repetition_factor"] == 2
    assert rv["chips_per_chirp"] == 32
    assert rv["profile_adc_samples_per_frame"] == 750 * 128


def test_v2_aggregate_separates_selection_and_conditional_qos():
    records = [
        {"policy": "B4_ROBUST_JOINT", "joint_qos": True, "selected_action": {"x": 1}, "normalized_resource_cost": 1.0},
        {"policy": "B4_ROBUST_JOINT", "joint_qos": False, "selected_action": None},
    ]
    out = aggregate_policy_metrics_v2(records)["B4_ROBUST_JOINT"]
    assert out["selection_rate"] == 0.5
    assert out["abstention_rate"] == 0.5
    assert out["joint_qos_probability_unconditional"] == 0.5
    assert out["joint_qos_probability_conditional_on_selection"] == 1.0


def test_pareto_front_removes_strictly_dominated_point():
    records = [
        {"policy": "B4_ROBUST_JOINT", "joint_qos": True, "normalized_resource_cost": 1.0, "resource_vector": {"tx_power_fraction": 1.0, "repetition_factor": 1, "chips_per_chirp": 16, "profile_adc_samples_per_frame": 1}},
        {"policy": "B4_ROBUST_JOINT", "joint_qos": False, "normalized_resource_cost": 2.0, "resource_vector": {"tx_power_fraction": 1.0, "repetition_factor": 2, "chips_per_chirp": 32, "profile_adc_samples_per_frame": 2}},
    ]
    front = pareto_front(records, "B4_ROBUST_JOINT")
    assert len(front) == 1
    assert front[0]["mean_normalized_resource_cost"] == 1.0


def test_feasible_region_slice_is_machine_readable():
    out = feasible_region_slice(
        axis_x="ebn0_db",
        values_x=[8.0],
        axis_y="radial_velocity_mps",
        values_y=[10.0],
        base_state=_state(),
        seeds=[10000],
        comm_bits=1000,
        sensing_trials=1,
        robust_draws=16,
    )
    assert out["axis_x"] == "ebn0_db"
    assert out["axis_y"] == "radial_velocity_mps"
    assert len(out["cells"]) == 1


def test_e11_ablations_are_explicit_and_threshold_preserving():
    rows = run_e11_ablations([_state()], comm_bits=1000, sensing_trials=1, robust_draws=16)
    assert {r["ablation"] for r in rows} == {"FULL_B4", "NO_STATE_UNCERTAINTY", "NO_CFO", "NO_INTERFERENCE"}


def test_v2_paired_smoke_runs_all_policies():
    rows = run_paired_benchmark_v2([10000], comm_bits=1000, sensing_trials=1, robust_draws=16)
    assert len(rows) == 12 * 6
    assert {r["policy"] for r in rows} == {"B0_FIXED", "B1_COMM_ONLY", "B2_SENSING_ONLY", "B3_DETERMINISTIC_JOINT", "B4_ROBUST_JOINT", "ORACLE"}
