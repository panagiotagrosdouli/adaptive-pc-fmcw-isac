#!/usr/bin/env python3
"""Build a deterministic, reviewer-facing submission/reproducibility ZIP.

The bundle intentionally contains publication-facing material and frozen evidence,
not the entire Git repository. Source-code provenance remains the Git commit named
in the generated submission manifest.
"""
from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path

FIXED_ZIP_TIME = (2026, 1, 1, 0, 0, 0)

EXPLICIT_PATHS = (
    "README.md",
    "Makefile",
    "pyproject.toml",
    "configs/paper_protocol_v2_1.json",
    "artifacts/publication/submission/action_space.csv",
    "artifacts/publication/submission/manifest.json",
    "paper/manuscript_v2_1.pdf",
    "paper/manuscript_v2_1.tex",
    "paper/references_v2_1.bib",
    "paper/references_submission.bib",
    "paper/SUBMISSION_SOURCE_MANIFEST.txt",
    "paper/SOURCE_TO_CLAIM_TRACEABILITY.md",
    "paper/FIGURE_PROVENANCE.md",
    "paper/CLAIM_AUDIT.md",
    "paper/REVIEWER_DEFENSE.md",
    "paper/EXCLUDED_UNVERIFIED_CLAIMS.md",
    "paper/SUBMISSION_CHECKLIST.md",
    "docs/EVIDENCE_MAP.md",
    "docs/EQUATION_TO_CODE_AUDIT.md",
    "docs/POLICY_DEFINITIONS.md",
    "docs/REPRODUCIBILITY.md",
    "docs/SUBMISSION_CHANGELOG.md",
    "docs/SUBMISSION_V2_1_RELEASE.md",
)

TREE_ROOTS = (
    "artifacts/publication/v2_1",
)


def _collect(root: Path) -> list[Path]:
    paths: set[Path] = set()
    missing: list[str] = []
    for rel in EXPLICIT_PATHS:
        p = root / rel
        if not p.is_file():
            missing.append(rel)
        else:
            paths.add(p)
    for rel in TREE_ROOTS:
        p = root / rel
        if not p.is_dir():
            missing.append(rel + "/")
            continue
        for child in p.rglob("*"):
            if child.is_file():
                paths.add(child)
    if missing:
        raise SystemExit("missing required submission bundle inputs: " + ", ".join(missing))
    return sorted(paths, key=lambda p: p.relative_to(root).as_posix())


def _validate_manifest(root: Path) -> str:
    manifest_path = root / "artifacts/publication/submission/manifest.json"
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    commit = str(data.get("submission_commit", "")).strip()
    if not commit or commit == "UNKNOWN":
        raise SystemExit("submission manifest has no immutable submission_commit")
    if data.get("frozen_scientific_baseline") != "3904c4c2a69c4af96751d64614f7228ddea24b56":
        raise SystemExit("submission manifest frozen baseline does not match publication-v2.1 baseline")
    return commit


def _write_member(zf: zipfile.ZipFile, root: Path, path: Path) -> None:
    rel = path.relative_to(root).as_posix()
    info = zipfile.ZipInfo(rel, FIXED_ZIP_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    zf.writestr(info, path.read_bytes())


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--root", default=".")
    p.add_argument("--output", default="artifacts/publication/submission/adaptive-pc-fmcw-isac-submission-v2.1.zip")
    args = p.parse_args()

    root = Path(args.root).resolve()
    commit = _validate_manifest(root)
    inputs = _collect(root)
    output = root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in inputs:
            _write_member(zf, root, path)
        info = zipfile.ZipInfo("SUBMISSION_COMMIT.txt", FIXED_ZIP_TIME)
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        zf.writestr(info, commit + "\n")

    print(f"wrote {output} with {len(inputs) + 1} files for commit {commit}")


if __name__ == "__main__":
    main()
