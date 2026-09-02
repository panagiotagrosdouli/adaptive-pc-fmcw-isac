from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from build_reproducibility_manifest import build_manifest  # noqa: E402


def test_manifest_is_portable_and_deterministic() -> None:
    config = PROJECT_ROOT / "configs" / "stage0.json"
    first = build_manifest(config)
    second = build_manifest(config)

    assert first["config_sha256"] == second["config_sha256"]
    assert first["stage0_source_sha256"] == second["stage0_source_sha256"]
    assert first["dataset_root_policy"]["path_committed"] is False
    assert first["part_a_role"] == "not_applicable_to_primary_methodology"
    assert first["source_file_count"] > 0
