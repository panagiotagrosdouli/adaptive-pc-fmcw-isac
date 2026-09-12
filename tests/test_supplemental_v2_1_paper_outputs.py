import importlib.util
import json
from pathlib import Path

import pytest


def _load_module():
    path = Path(__file__).resolve().parents[1] / "scripts" / "generate_supplemental_v2_1_figures.py"
    spec = importlib.util.spec_from_file_location("supplemental_v2_1_figures", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_artifact_loader_reads_results_envelope(tmp_path):
    m = _load_module()
    payload = {"results": {"summary": {"case": {"selection_rate": 0.5}}}}
    (tmp_path / "uncertainty.json").write_text(json.dumps(payload))

    assert m._load(tmp_path, "uncertainty") == payload["results"]


def test_artifact_loader_rejects_missing_results_envelope(tmp_path):
    m = _load_module()
    (tmp_path / "uncertainty.json").write_text(json.dumps({"summary": {}}))

    with pytest.raises(ValueError, match="artifact has no results envelope"):
        m._load(tmp_path, "uncertainty")


def test_runtime_series_uses_machine_readable_medians_and_ms_units():
    m = _load_module()
    data = {
        "summary": {
            "512": {
                "B3_DETERMINISTIC_JOINT": {"median_us": 750.0},
                "B4_ROBUST_JOINT": {"median_us": 250000.0},
            },
            "64": {
                "B3_DETERMINISTIC_JOINT": {"median_us": 500.0},
                "B4_ROBUST_JOINT": {"median_us": 32000.0},
            },
        }
    }

    draws, b3_ms, b4_ms = m._runtime_series(data)

    assert draws == [64, 512]
    assert b3_ms == [0.5, 0.75]
    assert b4_ms == [32.0, 250.0]


def test_runtime_series_rejects_artifacts_without_draw_counts():
    m = _load_module()

    with pytest.raises(ValueError, match="runtime artifact contains no draw-count summary"):
        m._runtime_series({"summary": {"metadata": {}}})


def test_mismatch_series_preserves_case_labels_and_policy_values():
    m = _load_module()
    data = {
        "summary": {
            "family_a": {
                "nominal_to_shifted": {
                    "B3_DETERMINISTIC_JOINT": {"joint_qos_unconditional": 0.25},
                    "B4_ROBUST_JOINT": {"joint_qos_unconditional": 0.75},
                }
            }
        }
    }

    labels, b3, b4 = m._mismatch_series(data)

    assert labels == ["family_a: nominal_to_shifted"]
    assert b3 == [0.25]
    assert b4 == [0.75]
