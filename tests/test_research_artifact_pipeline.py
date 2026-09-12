import json
from pathlib import Path
import importlib.util


def _load_script(name: str, filename: str):
    path = Path(__file__).resolve().parents[1] / "scripts" / filename
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


figures = _load_script("generate_supplemental_v2_1_figures", "generate_supplemental_v2_1_figures.py")
gate = _load_script("check_research_submission_gate", "check_research_submission_gate.py")


def test_runtime_series_converts_microseconds_to_milliseconds():
    data = {
        "summary": {
            "64": {
                "B3_DETERMINISTIC_JOINT": {"median_us": 500.0},
                "B4_ROBUST_JOINT": {"median_us": 25_000.0},
            },
            "128": {
                "B3_DETERMINISTIC_JOINT": {"median_us": 600.0},
                "B4_ROBUST_JOINT": {"median_us": 50_000.0},
            },
        }
    }
    draws, b3, b4 = figures._runtime_series(data)
    assert draws == [64, 128]
    assert b3 == [0.5, 0.6]
    assert b4 == [25.0, 50.0]


def test_mismatch_series_flattens_family_and_pair_keys():
    data = {
        "summary": {
            "SNR_BIAS": {
                "assumed=12|actual=8": {
                    "B3_DETERMINISTIC_JOINT": {"joint_qos_unconditional": 0.1},
                    "B4_ROBUST_JOINT": {"joint_qos_unconditional": 0.8},
                }
            }
        }
    }
    labels, b3, b4 = figures._mismatch_series(data)
    assert labels == ["SNR_BIAS: assumed=12|actual=8"]
    assert b3 == [0.1]
    assert b4 == [0.8]


def _envelope(name: str, results: dict) -> dict:
    return {
        "evidence_class": gate.EXPECTED_EVIDENCE_CLASS,
        "frozen_parent_protocol": "pcfmcw_isac_paper_v2_1",
        "experiment": name,
        "results": results,
    }


def test_submission_gate_fails_closed_when_artifacts_are_missing(tmp_path):
    report = gate.run_gate(tmp_path)
    assert not report["passed"]
    assert len(report["errors"]) == len(gate.REQUIRED)


def test_submission_gate_rejects_nonfinite_numbers():
    payload = _envelope("uncertainty", {"summary": {"x": float("nan")}})
    errors = gate.validate_artifact("uncertainty", payload)
    assert any("non-finite" in error for error in errors)


def test_submission_gate_accepts_calibration_shape():
    payload = _envelope(
        "reliability-calibration",
        {
            "summary": {
                "256": {
                    "false_feasible_rate": 0.01,
                    "false_infeasible_rate": 0.02,
                    "decision_disagreement_rate": 0.03,
                    "selected_action_disagreement_rate": 0.04,
                    "max_possible_wilson_lower_95": 0.9895,
                    "target_attainable_at_draw_count": True,
                    "minimum_successes_to_accept": 251,
                    "minimum_empirical_success_fraction_to_accept": 251 / 256,
                }
            },
            "finite_draw_attainability_note": "sample-size geometry is explicit",
        },
    )
    assert gate.validate_artifact("reliability-calibration", payload) == []


def test_submission_gate_rejects_inconsistent_unattainable_calibration_row():
    payload = _envelope(
        "reliability-calibration",
        {
            "summary": {
                "32": {
                    "false_feasible_rate": 0.0,
                    "false_infeasible_rate": 1.0,
                    "decision_disagreement_rate": 1.0,
                    "selected_action_disagreement_rate": 1.0,
                    "max_possible_wilson_lower_95": 0.922,
                    "target_attainable_at_draw_count": False,
                    "minimum_successes_to_accept": 32,
                    "minimum_empirical_success_fraction_to_accept": 1.0,
                }
            },
            "finite_draw_attainability_note": "sample-size geometry is explicit",
        },
    )
    errors = gate.validate_artifact("reliability-calibration", payload)
    assert any("must not report an acceptance success count" in error for error in errors)
