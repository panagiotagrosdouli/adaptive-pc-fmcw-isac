from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load_repository_audit():
    spec = importlib.util.spec_from_file_location(
        "repository_audit", ROOT / "scripts" / "audit_repository.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_all_paper_tex_files_are_free_of_known_stale_submission_claims():
    forbidden = {
        "frozen 256-draw": "stale frozen draw count",
        "prototype latency": "host runtime mislabeled as prototype latency",
        "138.89~ms": "obsolete 256-draw runtime",
        "272.81~ms": "obsolete 512-draw runtime",
        "279.71~ms": "obsolete p95 runtime",
        "hardware-validated controller": "unsupported controller hardware claim",
    }
    for path in sorted((ROOT / "paper").rglob("*.tex")):
        text = path.read_text(encoding="utf-8").lower()
        for phrase, reason in forbidden.items():
            assert phrase.lower() not in text, f"{reason} in {path.relative_to(ROOT)}: {phrase}"


def test_submission_manifest_does_not_duplicate_sources():
    manifest = ROOT / "paper" / "SUBMISSION_SOURCE_MANIFEST.txt"
    entries = [line.strip() for line in manifest.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(entries) == len(set(entries))
    for entry in entries:
        assert not entry.startswith("/")
        assert ".." not in Path(entry).parts
        assert (ROOT / "paper" / entry).is_file(), entry


def test_repository_audit_ignores_ephemeral_tool_directories():
    audit = _load_repository_audit()
    assert audit._is_ignored(ROOT / "pip-build-env-abc" / "dependency.py")
    assert audit._is_ignored(ROOT / "pytest-of-root" / "test.json")
    assert not audit._is_ignored(ROOT / "src" / "pcfmcw_isac" / "models.py")
