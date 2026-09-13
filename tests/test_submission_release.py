import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load_bundle_module():
    path = ROOT / "scripts/build_submission_bundle.py"
    spec = importlib.util.spec_from_file_location("build_submission_bundle", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_release_packaging_surface_is_wired_into_repository() -> None:
    required = (
        "scripts/build_submission_bundle.py",
        "docs/SUBMISSION_V2_1_RELEASE.md",
        "paper/SUBMISSION_CHECKLIST.md",
    )
    for rel in required:
        assert (ROOT / rel).is_file(), rel

    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "submission-bundle:" in makefile
    assert "scripts/build_submission_bundle.py" in makefile
    assert "adaptive-pc-fmcw-isac-submission-v2.1.zip" in makefile

    workflow = (ROOT / ".github/workflows/manuscript_latex.yml").read_text(encoding="utf-8")
    assert "Build deterministic submission bundle" in workflow
    assert "Validate submission bundle" in workflow
    assert "adaptive-pc-fmcw-isac-submission-v2.1.zip" in workflow
    assert "push:" in workflow and "main" in workflow


def test_release_material_is_covered_by_submission_manifest_builder() -> None:
    manifest_builder = (ROOT / "scripts/build_submission_manifest.py").read_text(encoding="utf-8")
    for rel in (
        "paper/SUBMISSION_CHECKLIST.md",
        "docs/SUBMISSION_V2_1_RELEASE.md",
        "scripts/build_submission_bundle.py",
    ):
        assert rel in manifest_builder


def test_bundle_collection_contains_every_manifest_file_pdf_and_frozen_tree(tmp_path: Path) -> None:
    module = _load_bundle_module()

    manifest_path = tmp_path / module.MANIFEST_REL
    manifest_path.parent.mkdir(parents=True)
    manifest_files = ("alpha.txt", "nested/beta.txt")
    for rel in manifest_files:
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(rel, encoding="utf-8")

    pdf = tmp_path / "paper/manuscript_v2_1.pdf"
    pdf.parent.mkdir(parents=True)
    pdf.write_bytes(b"%PDF-test")

    evidence = tmp_path / "artifacts/publication/v2_1/FINAL_RESULTS.json"
    evidence.parent.mkdir(parents=True)
    evidence.write_text("{}", encoding="utf-8")

    manifest = {
        "submission_commit": "a" * 40,
        "frozen_scientific_baseline": "3904c4c2a69c4af96751d64614f7228ddea24b56",
        "files": [{"path": rel} for rel in manifest_files],
    }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    loaded, commit = module._load_manifest(tmp_path)
    assert commit == "a" * 40
    collected = {p.relative_to(tmp_path).as_posix() for p in module._collect(tmp_path, loaded)}

    assert module.MANIFEST_REL in collected
    assert set(manifest_files).issubset(collected)
    assert "paper/manuscript_v2_1.pdf" in collected
    assert "artifacts/publication/v2_1/FINAL_RESULTS.json" in collected
