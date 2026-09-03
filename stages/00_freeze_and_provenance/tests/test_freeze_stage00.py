from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "freeze_stage00.py"
spec = importlib.util.spec_from_file_location("freeze_stage00", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


def _write_npz(path: Path, scenario_ids: list[str], splits: list[str] | None = None) -> None:
    payload = {"scenario_id": np.asarray(scenario_ids, dtype="U32")}
    if splits is not None:
        payload["split"] = np.asarray(splits, dtype="U32")
    np.savez(path, **payload)


def test_overlap_report_accepts_disjoint_official_validation(tmp_path: Path) -> None:
    train_path = tmp_path / "train.npz"
    heldout_path = tmp_path / "heldout.npz"
    _write_npz(train_path, ["a", "b", "c"], ["train", "development", "train"])
    _write_npz(heldout_path, ["x", "y"])

    report = module.overlap_report(train_path, heldout_path)

    assert report["internal_train_development_overlap_count"] == 0
    assert report["training_corpus_official_validation_overlap_count"] == 0
    assert report["zero_cross_split_overlap"] is True


def test_overlap_report_rejects_cross_split_leakage(tmp_path: Path) -> None:
    train_path = tmp_path / "train.npz"
    heldout_path = tmp_path / "heldout.npz"
    _write_npz(train_path, ["a", "b"], ["train", "development"])
    _write_npz(heldout_path, ["b", "z"])

    report = module.overlap_report(train_path, heldout_path)

    assert report["training_corpus_official_validation_overlap_count"] == 1
    assert report["zero_cross_split_overlap"] is False


def test_missing_official_validation_never_passes_gate(tmp_path: Path) -> None:
    train_path = tmp_path / "train.npz"
    _write_npz(train_path, ["a", "b"], ["train", "development"])

    report = module.overlap_report(train_path, None)

    assert report["official_validation_present"] is False
    assert report["zero_cross_split_overlap"] is False
