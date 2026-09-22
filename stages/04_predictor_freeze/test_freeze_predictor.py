from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

PATH = Path(__file__).with_name("freeze_predictor.py")
SPEC = importlib.util.spec_from_file_location("stage04", PATH); assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(MODULE)


def files(tmp_path: Path, contaminated: bool = False):
    manifest, checkpoint, preprocessing = tmp_path/"training.json", tmp_path/"model.bin", tmp_path/"preprocess.json"
    manifest.write_text(json.dumps({"schema":"predictor_training_contract_v1", "status":"READY_FOR_TRAINING", "official_validation_used": contaminated}))
    checkpoint.write_bytes(b"frozen-checkpoint"); preprocessing.write_text("{}")
    return manifest, checkpoint, preprocessing


def test_freeze_records_all_hashes(tmp_path):
    result = MODULE.freeze(*files(tmp_path))
    assert result["status"] == "FROZEN"
    assert all(result[key]["sha256"] for key in ("training_manifest", "checkpoint", "preprocessing"))


def test_official_validation_contamination_fails_closed(tmp_path):
    with pytest.raises(ValueError, match="contamination"):
        MODULE.freeze(*files(tmp_path, contaminated=True))
