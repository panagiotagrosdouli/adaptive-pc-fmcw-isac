#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[3]
STAGE_ROOT = Path(__file__).resolve().parents[1]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_commit() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip() or None


def json_dump(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _decode_strings(values: np.ndarray) -> np.ndarray:
    flat = np.asarray(values).reshape(-1)
    decoded = []
    for value in flat:
        if isinstance(value, bytes):
            decoded.append(value.decode("utf-8"))
        else:
            decoded.append(str(value))
    return np.asarray(decoded, dtype=object)


def load_scenarios(path: Path) -> tuple[set[str], dict[str, set[str]]]:
    with np.load(path, allow_pickle=False) as data:
        keys = set(data.files)
        scenario_key = next(
            (key for key in ("scenario_id", "scenario_ids", "scenario") if key in keys),
            None,
        )
        if scenario_key is None:
            raise KeyError(
                f"{path} has no scenario id key; expected one of "
                "scenario_id/scenario_ids/scenario"
            )
        scenario_ids = _decode_strings(data[scenario_key])
        unique = set(scenario_ids.tolist())
        split_sets: dict[str, set[str]] = {}
        split_key = next(
            (key for key in ("split", "splits", "split_name", "fixed_split") if key in keys),
            None,
        )
        if split_key is not None:
            splits = _decode_strings(data[split_key])
            if len(splits) != len(scenario_ids):
                raise ValueError(f"split array length mismatch in {path}")
            for split_name in sorted(set(splits.tolist())):
                mask = splits == split_name
                split_sets[split_name] = set(scenario_ids[mask].tolist())
        return unique, split_sets


def overlap_report(train_npz: Path, official_validation_npz: Path | None) -> dict:
    train_all, internal = load_scenarios(train_npz)
    train = internal.get("train", internal.get("training", set()))
    development = internal.get("development", internal.get("dev", internal.get("validation", set())))

    # When the NPZ does not store explicit labels, we can still audit the official held-out
    # against the full official-training-derived corpus. Internal train/dev overlap then remains unknown.
    internal_overlap = train & development if train or development else set()

    official = set()
    if official_validation_npz is not None:
        official, _ = load_scenarios(official_validation_npz)

    return {
        "train_npz": str(train_npz),
        "official_validation_npz": str(official_validation_npz) if official_validation_npz else None,
        "training_corpus_scenarios": len(train_all),
        "internal_train_scenarios": len(train),
        "internal_development_scenarios": len(development),
        "official_validation_scenarios": len(official),
        "internal_train_development_overlap_count": len(internal_overlap),
        "training_corpus_official_validation_overlap_count": len(train_all & official),
        "internal_split_labels_present": bool(train or development),
        "official_validation_present": official_validation_npz is not None,
        "zero_cross_split_overlap": (
            official_validation_npz is not None
            and len(train_all & official) == 0
            and len(internal_overlap) == 0
        ),
    }


def dataset_entry(path: Path, role: str) -> dict:
    return {
        "role": role,
        "path": str(path),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Freeze Stage-00 publication provenance.")
    parser.add_argument("--train-npz", type=Path, required=True)
    parser.add_argument("--official-validation-npz", type=Path)
    parser.add_argument("--output-root", type=Path, default=REPO_ROOT / "artifacts" / "paper_final")
    parser.add_argument(
        "--protocol-template",
        type=Path,
        default=STAGE_ROOT / "experiment_protocol.template.json",
    )
    args = parser.parse_args()

    if not args.train_npz.is_file():
        parser.error(f"training NPZ not found: {args.train_npz}")
    if args.official_validation_npz and not args.official_validation_npz.is_file():
        parser.error(f"official-validation NPZ not found: {args.official_validation_npz}")

    now = datetime.now(timezone.utc).isoformat()
    commit = git_commit()
    protocol = json.loads(args.protocol_template.read_text(encoding="utf-8"))
    protocol.update({"frozen_at_utc": now, "git_commit": commit})

    audit = overlap_report(args.train_npz, args.official_validation_npz)
    dataset_files = [dataset_entry(args.train_npz, "official_womd_training_derived")]
    if args.official_validation_npz:
        dataset_files.append(dataset_entry(args.official_validation_npz, "official_womd_validation"))

    dataset_manifest = {
        "frozen_at_utc": now,
        "womd_release": "v1.3.1",
        "files": dataset_files,
        "heldout_policy": "official validation is evaluation-only and forbidden for tuning",
    }
    code_manifest = {
        "frozen_at_utc": now,
        "git_commit": commit,
        "protocol_sha256": sha256_file(args.protocol_template),
        "stage_definition_sha256": sha256_file(STAGE_ROOT / "stage.json"),
    }

    json_dump(args.output_root / "manifests" / "code_manifest.json", code_manifest)
    json_dump(args.output_root / "manifests" / "dataset_manifest.json", dataset_manifest)
    json_dump(args.output_root / "manifests" / "experiment_protocol.json", protocol)
    json_dump(args.output_root / "data_audit" / "split_overlap.json", audit)

    complete = bool(audit["zero_cross_split_overlap"] and commit)
    status = {
        "stage": "stage00",
        "status": "DONE" if complete else "BLOCKED",
        "reason": None if complete else (
            "official validation is missing, overlap is non-zero, internal split leakage exists, "
            "or git commit provenance is unavailable"
        ),
        "outputs": {
            "code_manifest": "manifests/code_manifest.json",
            "dataset_manifest": "manifests/dataset_manifest.json",
            "experiment_protocol": "manifests/experiment_protocol.json",
            "split_overlap": "data_audit/split_overlap.json",
        },
    }
    json_dump(args.output_root / "manifests" / "stage00_status.json", status)
    print(json.dumps(status, indent=2, sort_keys=True))
    return 0 if complete else 2


if __name__ == "__main__":
    raise SystemExit(main())
