import importlib.util
import json
from pathlib import Path


def _load_module():
    path = Path(__file__).resolve().parents[1] / "scripts" / "generate_research_tables.py"
    spec = importlib.util.spec_from_file_location("generate_research_tables", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


tables = _load_module()


def _write(root, name, results):
    (root / f"{name}.json").write_text(json.dumps({"results": results}))


def test_table_generator_emits_csv_and_latex_from_artifacts(tmp_path):
    root = tmp_path / "in"; out = tmp_path / "out"; root.mkdir()
    metric = {
        "n": 10, "selection_rate": 0.2, "joint_qos_probability_unconditional": 0.2,
        "joint_qos_probability_conditional": 1.0, "wilson_lower_95_conditional": 0.7,
        "mean_normalized_resource_cost_selected": 1.2,
    }
    _write(root, "full-metrics", {"summary": {"B4_ROBUST_JOINT": metric}})
    _write(root, "reliability-calibration", {"summary": {"32": {
        "n": 10,
        "max_possible_wilson_lower_95": 0.922,
        "target_attainable_at_draw_count": False,
        "minimum_successes_to_accept": None,
        "minimum_empirical_success_fraction_to_accept": None,
        "false_feasible_rate": 0.0, "false_infeasible_rate": 0.1,
        "decision_disagreement_rate": 0.1, "selected_action_disagreement_rate": 0.2,
        "finite_selection_rate": 0.2, "reference_selection_rate": 0.3,
    }}})
    _write(root, "action-space", {"summary": {"FULL": metric}})
    _write(root, "distribution-shift", {"summary": {"HEAVY_TAILED_T3": {
        "B4_ROBUST_JOINT": metric,
    }}, "paired_statistics": {"HEAVY_TAILED_T3": {
        "mean_difference_a_minus_b": 0.1, "ci_low": 0.0, "ci_high": 0.2,
    }}})
    _write(root, "runtime", {"summary": {"32": {
        "B4_ROBUST_JOINT": {"median_us": 100.0, "p95_us": 150.0, "p99_us": 200.0},
    }}})
    _write(root, "reliability-targets", {"summary": {"0.95": metric}})
    _write(root, "qos-sensitivity", {"summary": {"BASELINE": {
        "B4_ROBUST_JOINT": {
            "selection_rate": 0.2,
            "counterfactual_joint_qos_unconditional": 0.2,
            "counterfactual_joint_qos_conditional": 1.0,
            "wilson_lower_95_conditional": 0.7,
        }
    }}})
    _write(root, "uncertainty-sources", {"summary": {"FULL_B4": metric}})
    _write(root, "confidence-maps", {"ebn0_velocity": {"cells": [{
        "x": 12.0, "y": 20.0, "selection_rate": 0.2,
        "joint_qos_probability_unconditional": 0.2,
        "joint_qos_probability_conditional": 1.0,
        "wilson_lower_95_conditional": 0.7,
        "confidence_qualified_target_0p95": False,
    }]}})
    point = {
        "joint_qos_probability": 1.0, "mean_effective_rate_bps": 2e5,
        "tx_power_fraction": 0.5, "repetition_factor": 1, "chips_per_chirp": 16,
        "profile_adc_samples_per_frame": 1000, "mean_range_rmse_m": 0.2,
        "mean_velocity_rmse_mps": 0.2, "n": 8,
    }
    _write(root, "pareto", {"physical_points": [point], "pareto": {
        "non_dominated_points": [{**point, "point_index": 0, "dominated_by_indices": []}],
        "dominated_points": [],
    }})

    tables.policy_table(root, out)
    tables.calibration_table(root, out)
    tables.action_space_table(root, out)
    tables.distribution_shift_table(root, out)
    tables.runtime_table(root, out)
    tables.reliability_target_table(root, out)
    tables.qos_sensitivity_table(root, out)
    tables.uncertainty_sources_table(root, out)
    tables.confidence_maps_table(root, out)
    tables.pareto_table(root, out)

    stems = {
        "policy_comparison", "reliability_calibration", "action_space_sensitivity",
        "distribution_shift", "runtime", "reliability_target_sensitivity",
        "qos_threshold_sensitivity", "uncertainty_source_ablation",
        "confidence_qualified_maps", "empirical_pareto",
    }
    expected = {f"{stem}.{suffix}" for stem in stems for suffix in ("csv", "tex")}
    assert {p.name for p in out.iterdir()} == expected
    tex = (out / "policy_comparison.tex").read_text()
    assert "\\begin{table*}" in tex
    assert "B4\\_ROBUST\\_JOINT" in tex
    calibration_csv = (out / "reliability_calibration.csv").read_text()
    assert "max_possible_wilson_lower_95" in calibration_csv
    assert "target_attainable_at_draw_count" in calibration_csv
    assert "False" in calibration_csv
    calibration_tex = (out / "reliability_calibration.tex").read_text()
    assert "target\\_attainable\\_at\\_draw\\_count" in calibration_tex
    pareto_csv = (out / "empirical_pareto.csv").read_text()
    assert "non_dominated" in pareto_csv
    assert "True" in pareto_csv
