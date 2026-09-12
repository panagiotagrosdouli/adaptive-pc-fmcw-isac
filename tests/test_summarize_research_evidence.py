import importlib.util
import json
from pathlib import Path


def _load_module():
    path = Path(__file__).resolve().parents[1] / "scripts" / "summarize_research_evidence.py"
    spec = importlib.util.spec_from_file_location("summarize_research_evidence", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


summary = _load_module()


def _write(root: Path, name: str, results: dict) -> None:
    (root / f"{name}.json").write_text(json.dumps({"results": results}))


def test_verdict_rejects_universal_superiority_and_detects_availability_tradeoff(tmp_path):
    root = tmp_path
    records = []
    for seed, b3_success, b4_success in ((1, True, True), (2, True, False), (3, True, False), (4, True, True)):
        records.extend([
            {"seed": seed, "scenario_id": 0, "policy": summary.B3, "joint_qos": b3_success},
            {"seed": seed, "scenario_id": 0, "policy": summary.B4, "joint_qos": b4_success},
        ])
    _write(root, "full-metrics", {
        "records": records,
        "summary": {
            summary.B3: {"selection_rate": 0.8, "joint_qos_probability_unconditional": 1.0, "joint_qos_probability_conditional": 1.0, "wilson_lower_95_conditional": 0.99},
            summary.B4: {"selection_rate": 0.4, "joint_qos_probability_unconditional": 0.5, "joint_qos_probability_conditional": 1.0, "wilson_lower_95_conditional": 0.98},
        },
    })
    _write(root, "reliability-calibration", {"summary": {"256": {
        "target_attainable_at_draw_count": True,
        "decision_disagreement_rate": 0.01,
        "false_feasible_rate": 0.0,
        "false_infeasible_rate": 0.01,
        "minimum_successes_to_accept": 249,
    }}})
    _write(root, "distribution-shift", {"paired_statistics": {"NOMINAL_GAUSSIAN": {
        "mean_difference_a_minus_b": -0.1, "ci_low": -0.2, "ci_high": 0.0,
    }}})
    _write(root, "pareto", {"pareto": {"n_points": 3, "n_non_dominated": 2, "n_dominated": 1}, "claim_boundary": "empirical only"})
    _write(root, "runtime", {"summary": {"256": {summary.B4: {"median_us": 1000.0}}}})
    _write(root, "uncertainty", {"summary": {"1.0": {
        summary.B3: {"selection_rate": 0.8, "joint_qos_conditional_on_selection": 0.9},
        summary.B4: {"selection_rate": 0.4, "joint_qos_conditional_on_selection": 1.0},
    }}})

    out = summary.derive_verdict(root, bootstrap_resamples=200)
    claims = out["claim_status"]
    assert claims["b4_high_conditional_reliability_when_selected"]
    assert claims["b4_pays_availability_cost_vs_b3"]
    assert claims["reliability_availability_tradeoff_supported"]
    assert not claims["b4_unconditional_superiority_vs_b3"]
    assert not claims["universal_b4_superiority_allowed"]
    assert not claims["hardware_validation_allowed"]
    assert out["paired_b4_minus_b3_unconditional_joint_qos"]["mean_difference_a_minus_b"] == -0.5
