#!/usr/bin/env python3
"""Validate Stage-01 train/development corpora and record a training contract."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def scenario_ids(path: Path, expected_split: str) -> set[str]:
    with np.load(path, allow_pickle=False) as data:
        required = {"scenario_id", "split", "history_xy", "future_xy"}
        missing = sorted(required - set(data.files))
        if missing:
            raise ValueError(f"{path}: missing arrays {missing}")
        splits = {str(value) for value in data["split"].tolist()}
        if splits != {expected_split}:
            raise ValueError(f"{path}: expected split {expected_split!r}, observed {sorted(splits)}")
        ids = {str(value) for value in data["scenario_id"].tolist()}
        if not ids or any(not value for value in ids):
            raise ValueError(f"{path}: empty scenario identity")
        return ids


def build_manifest(training: Path, development: Path, model_config: Path) -> dict:
    train_ids = scenario_ids(training, "training")
    dev_ids = scenario_ids(development, "development")
    overlap = sorted(train_ids & dev_ids)
    if overlap:
        raise ValueError(f"scenario leakage between training and development: {overlap[:5]}")
    json.loads(model_config.read_text(encoding="utf-8"))
    return {
        "schema": "predictor_training_contract_v1",
        "status": "READY_FOR_TRAINING",
        "training_corpus": {"path": str(training), "sha256": sha256_file(training), "scenario_count": len(train_ids)},
        "development_corpus": {"path": str(development), "sha256": sha256_file(development), "scenario_count": len(dev_ids)},
        "model_config": {"path": str(model_config), "sha256": sha256_file(model_config)},
        "official_validation_used": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--training", type=Path, required=True)
    parser.add_argument("--development", type=Path, required=True)
    parser.add_argument("--model-config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = build_manifest(args.training, args.development, args.model_config)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
