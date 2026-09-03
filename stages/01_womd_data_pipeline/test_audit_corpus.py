import importlib.util
from pathlib import Path

import numpy as np

MODULE = Path(__file__).with_name("audit_corpus.py")
spec = importlib.util.spec_from_file_location("stage01_audit", MODULE)
audit_module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(audit_module)


def corpus(path: Path, split="official_validation", bad=False):
    n = 3
    history = np.zeros((n, 11, 2), dtype=np.float32)
    if bad:
        history[0, 0, 0] = np.nan
    np.savez_compressed(
        path,
        history_xy=history,
        history_vxy=np.zeros((n, 11, 2), dtype=np.float32),
        future_xy=np.zeros((n, 80, 2), dtype=np.float32),
        history_valid=np.ones((n, 11), dtype=bool),
        future_valid=np.ones((n, 80), dtype=bool),
        scenario_id=np.array(["a", "a", "b"]),
        track_id=np.array([1, 2, 3]),
        sdc_track_id=np.array([9, 9, 10]),
        split=np.array([split] * n),
    )


def test_valid_official_corpus_passes(tmp_path):
    path = tmp_path / "official.npz"
    corpus(path)
    report = audit_module.audit(path, "official_validation")
    assert report["passed"]
    assert report["sample_count"] == 3
    assert report["scenario_count"] == 2


def test_internal_development_cannot_pose_as_official(tmp_path):
    path = tmp_path / "dev.npz"
    corpus(path, split="development")
    report = audit_module.audit(path, "official_validation")
    assert not report["passed"]


def test_nonfinite_trajectory_fails(tmp_path):
    path = tmp_path / "bad.npz"
    corpus(path, bad=True)
    report = audit_module.audit(path)
    assert not report["passed"]
    assert not report["finite_numeric_arrays"]
