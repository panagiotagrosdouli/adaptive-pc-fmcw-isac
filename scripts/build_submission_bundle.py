#!/usr/bin/env python3
"""Build a deterministic, reviewer-facing submission/reproducibility ZIP.

Every repository file listed in the SHA-256 submission manifest is included in
the ZIP. The bundle additionally carries the compiled manuscript PDF and the
complete frozen publication-v2.1 evidence tree. This keeps the manifest and the
archive self-consistent while preserving the Git commit as source provenance.
"""
from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path

FIXED_ZIP_TIME = (2026, 1, 1, 0, 0, 0)
MANIFEST_REL = "artifacts/publication/submission/manifest.json"
ADDITIONAL_FILES = (
    "paper/manuscript_v2_1.pdf",
)
TREE_ROOTS = (
    "artifacts/publication/v2_1",
)


def _load_manifest(root: Path) -> tuple[dict, str]:
    manifest_path = root / MANIFEST_REL
    if not manifest_path.is_file():
        raise SystemExit(f"missing submission manifest: {MANIFEST_REL}")
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    commit = str(data.get("submission_commit", "")).strip()
    if not commit or commit == "UNKNOWN":
        raise SystemExit("submission manifest has no immutable submission_commit")
    if data.get("frozen_scientific_baseline") != "3904c4c2a69c4af96751d64614f7228ddea24b56":
        raise SystemExit("submission manifest frozen baseline does not match publication-v2.1 baseline")
    files = data.get("files")
    if not isinstance(files, list) or not files:
        raise SystemExit("submission manifest has no file records")
    return data, commit


def _collect(root: Path, manifest: dict) -> list[Path]:
    paths: set[Path] = {root / MANIFEST_REL}
    missing: list[str] = []

    for record in manifest["files"]:
        rel = str(record.get("path", "")).strip()
        if not rel or rel.startswith("/") or ".." in Path(rel).parts:
            raise SystemExit(f"unsafe/invalid manifest path: {rel!r}")
        p = root / rel
        if not p.is_file():
            missing.append(rel)
        else:
            paths.add(p)

    for rel in ADDITIONAL_FILES:
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
        raise SystemExit("missing required submission bundle inputs: " + ", ".join(sorted(set(missing))))
    return sorted(paths, key=lambda p: p.relative_to(root).as_posix())


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
    manifest, commit = _load_manifest(root)
    inputs = _collect(root, manifest)
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
