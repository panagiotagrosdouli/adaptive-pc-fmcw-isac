#!/usr/bin/env python3
"""Create a provenance-complete frozen predictor release manifest."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def freeze(training_manifest: Path, checkpoint: Path, preprocessing: Path) -> dict:
    training = json.loads(training_manifest.read_text(encoding="utf-8"))
    if training.get("schema") != "predictor_training_contract_v1":
        raise ValueError("wrong training-manifest schema")
    if training.get("status") != "READY_FOR_TRAINING":
        raise ValueError("training manifest is not ready")
    if training.get("official_validation_used") is not False:
        raise ValueError("official validation contamination detected")
    json.loads(preprocessing.read_text(encoding="utf-8"))
    if checkpoint.stat().st_size <= 0:
        raise ValueError("checkpoint is empty")
    return {
        "schema": "frozen_predictor_release_v1",
        "status": "FROZEN",
        "training_manifest": {"path": str(training_manifest), "sha256": sha256_file(training_manifest)},
        "checkpoint": {"path": str(checkpoint), "sha256": sha256_file(checkpoint), "bytes": checkpoint.stat().st_size},
        "preprocessing": {"path": str(preprocessing), "sha256": sha256_file(preprocessing)},
        "official_validation_used_for_selection": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--training-manifest", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--preprocessing", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    release = freeze(args.training_manifest, args.checkpoint, args.preprocessing)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(release, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
