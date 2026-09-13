from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_submission_manifest.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("build_submission_manifest", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_submission_manifest_required_paths_exist_after_action_space_export(tmp_path, monkeypatch):
    module = _load_module()
    required = set(module.DEFAULT_PATHS)
    assert "artifacts/publication/submission/action_space.csv" in required
    assert "paper/figures_submission.tex" in required
    assert "paper/literature_positioning.tex" in required
    assert ".github/workflows/ci.yml" in required
    assert ".github/workflows/manuscript_latex.yml" in required


def test_detect_commit_prefers_github_sha(monkeypatch):
    module = _load_module()
    monkeypatch.setenv("GITHUB_SHA", "a" * 40)
    assert module.detect_commit(ROOT) == "a" * 40


def test_manifest_schema_and_frozen_baseline_are_stable():
    module = _load_module()
    assert module.DEFAULT_PATHS
    source = SCRIPT.read_text(encoding="utf-8")
    assert "pcfmcw-isac-submission-manifest-v2" in source
    assert "3904c4c2a69c4af96751d64614f7228ddea24b56" in source
