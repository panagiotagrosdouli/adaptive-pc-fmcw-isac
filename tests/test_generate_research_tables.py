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
    _write(root, "full-metrics", {"summary": {"B4_ROBUST_JOINT": {
        "n": 10, "selection_rate": 0.2, "joint_qos_probability_unconditional": 0.2,
        "joint_qos_probability_conditional": 1.0, "wilson_lower_95_conditional": 0.7,
        "mean_normalized_resource_cost_selected": 1.2,
    }}})
    _write(root, "reliability-calibration", {"summary": {"32": {
        "n": 10, "false_feasible_rate": 0.0, "false_infeasible_rate": 0.1,
        "decision_disagreement_rate": 0.1, "selected_action_disagreement_rate": 0.2,
        "finite_selection_rate": 0.2, "reference_selection_rate": 0.3,
    }}})
    _write(root, "action-space", {"summary": {"FULL": {
        "selection_rate": 0.2, "joint_qos_probability_unconditional": 0.2,
        "joint_qos_probability_conditional": 1.0, "wilson_lower_95_conditional": 0.7,
        "mean_normalized_resource_cost_selected": 1.2,
    }}})
    _write(root, "distribution-shift", {"summary": {"HEAVY_TAILED_T3": {
        "B4_ROBUST_JOINT": {"selection_rate": 0.2, "joint_qos_probability_unconditional": 0.2,
        "joint_qos_probability_conditional": 1.0, "wilson_lower_95_conditional": 0.7},
    }}, "paired_statistics": {"HEAVY_TAILED_T3": {
        "mean_difference_a_minus_b": 0.1, "ci_low": 0.0, "ci_high": 0.2,
    }}})
    _write(root, "runtime", {"summary": {"32": {
        "B4_ROBUST_JOINT": {"median_us": 100.0, "p95_us": 150.0, "p99_us": 200.0},
    }}})

    tables.policy_table(root, out)
    tables.calibration_table(root, out)
    tables.action_space_table(root, out)
    tables.distribution_shift_table(root, out)
    tables.runtime_table(root, out)

    expected = {
        "policy_comparison.csv", "policy_comparison.tex",
        "reliability_calibration.csv", "reliability_calibration.tex",
        "action_space_sensitivity.csv", "action_space_sensitivity.tex",
        "distribution_shift.csv", "distribution_shift.tex",
        "runtime.csv", "runtime.tex",
    }
    assert {p.name for p in out.iterdir()} == expected
    tex = (out / "policy_comparison.tex").read_text()
    assert "\\begin{table*}" in tex
    assert "B4\\_ROBUST\\_JOINT" in tex
