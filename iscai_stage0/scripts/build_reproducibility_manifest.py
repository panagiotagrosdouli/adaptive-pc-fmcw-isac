#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from iscai_stage0.common import load_config, sha256_file, write_json  # noqa: E402


def tree_hash(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths, key=lambda item: item.as_posix()):
        relative = path.relative_to(PROJECT_ROOT).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(sha256_file(path).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def git_commit() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip() or None


def build_manifest(config_path: Path) -> dict:
    config = load_config(config_path)
    source_files = [
        *PROJECT_ROOT.joinpath("src").rglob("*.py"),
        *PROJECT_ROOT.joinpath("scripts").glob("*.py"),
        *PROJECT_ROOT.joinpath("tests").glob("*.py"),
    ]
    return {
        "stage": 0,
        "purpose": "portable_dataset_and_reproducibility_audit",
        "dataset_release": config["dataset_release"],
        "dataset_root_policy": {
            "environment_variable": config["dataset_root_env"],
            "path_committed": False,
        },
        "part_a_role": config["part_a_role"],
        "config_sha256": sha256_file(config_path),
        "stage0_source_sha256": tree_hash(source_files),
        "source_file_count": len(source_files),
        "git_commit": git_commit(),
        "completion_semantics": (
            "Manifest generation proves code/config provenance only; dataset "
            "access and schema checks have separate reports."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build portable Stage-0 provenance.")
    parser.add_argument(
        "--config",
        type=Path,
        default=PROJECT_ROOT / "configs" / "stage0.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "reports" / "stage0" / "reproducibility_manifest.json",
    )
    args = parser.parse_args()
    manifest = build_manifest(args.config)
    write_json(args.output, manifest)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    print(f"\nWrote: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
