from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest

PATH = Path(__file__).with_name("build_training_manifest.py")
SPEC = importlib.util.spec_from_file_location("stage03", PATH); assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(MODULE)


def corpus(path: Path, split: str, ids: list[str]) -> None:
    n = len(ids)
    np.savez(path, scenario_id=np.asarray(ids), split=np.asarray([split] * n),
             history_xy=np.zeros((n, 11, 2)), future_xy=np.zeros((n, 80, 2)))


def test_disjoint_training_contract(tmp_path):
    train, dev, cfg = tmp_path/"train.npz", tmp_path/"dev.npz", tmp_path/"model.json"
    corpus(train, "training", ["a", "b"]); corpus(dev, "development", ["c"]); cfg.write_text(json.dumps({"model":"cv"}))
    result = MODULE.build_manifest(train, dev, cfg)
    assert result["status"] == "READY_FOR_TRAINING"
    assert result["official_validation_used"] is False


def test_scenario_leakage_fails_closed(tmp_path):
    train, dev, cfg = tmp_path/"train.npz", tmp_path/"dev.npz", tmp_path/"model.json"
    corpus(train, "training", ["same"]); corpus(dev, "development", ["same"]); cfg.write_text("{}")
    with pytest.raises(ValueError, match="leakage"):
        MODULE.build_manifest(train, dev, cfg)
