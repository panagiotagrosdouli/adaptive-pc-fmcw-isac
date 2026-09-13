from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


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
