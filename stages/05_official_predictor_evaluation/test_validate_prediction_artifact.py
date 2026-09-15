from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np


MODULE_PATH = Path(__file__).with_name("validate_prediction_artifact.py")
_SPEC = importlib.util.spec_from_file_location("stage05_validator", MODULE_PATH)
assert _SPEC and _SPEC.loader
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)
validate = _MODULE.validate


def _artifact(path, include_provenance=True):
    n = 2
    payload = {
        "scenario_id": np.array(["s1", "s2"]),
        "track_id": np.array(["t1", "t2"]),
        "sdc_track_id": np.array(["sdc1", "sdc2"]),
        "predicted_xy": np.zeros((n, 80, 2), dtype=np.float32),
        "prediction_valid": np.ones((n, 80), dtype=np.uint8),
    }
    if include_provenance:
        payload.update({
            "checkpoint_sha256": np.array("a" * 64),
            "preprocessing_sha256": np.array("b" * 64),
            "input_corpus_sha256": np.array("c" * 64),
        })
    np.savez(path, **payload)


def test_valid_prediction_artifact(tmp_path):
    path = tmp_path / "predictions.npz"
    _artifact(path)
    report = validate(path)
    assert report["passed"]
    assert report["sample_count"] == 2


def test_missing_provenance_is_rejected(tmp_path):
    path = tmp_path / "predictions.npz"
    _artifact(path, include_provenance=False)
    report = validate(path)
    assert not report["passed"]
    assert any("provenance" in error for error in report["errors"])


def test_wrong_horizon_is_rejected(tmp_path):
    path = tmp_path / "predictions.npz"
    _artifact(path)
    with np.load(path, allow_pickle=False) as data:
        payload = {key: data[key] for key in data.files}
    payload["predicted_xy"] = np.zeros((2, 79, 2), dtype=np.float32)
    np.savez(path, **payload)
    report = validate(path)
    assert not report["passed"]
    assert any("predicted_xy" in error for error in report["errors"])
