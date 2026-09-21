#!/usr/bin/env python3
"""Build a SHA-256 provenance manifest for submission-facing repository artifacts."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path

DEFAULT_PATHS = (
    "README.md",
    "Makefile",
    "pyproject.toml",
    "configs/paper_protocol_v2_1.json",
    "artifacts/publication/v2_1/FINAL_RESULTS.json",
    "artifacts/publication/v2_1/PROVENANCE.json",
    "artifacts/publication/submission/action_space.csv",
    "paper/manuscript_v2_1.tex",
    "paper/final_abstract_conclusion_abstract_only.tex",
    "paper/final_abstract_conclusion_conclusion_only.tex",
    "paper/final_results_discussion.tex",
    "paper/results_v2_1_tables.tex",
    "paper/supplemental_v2_1_tables.tex",
    "paper/figures_submission.tex",
    "paper/literature_positioning.tex",
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
    "scripts/build_submission_bundle.py",
    ".github/workflows/ci.yml",
    ".github/workflows/manuscript_latex.yml",
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def detect_commit(root: Path) -> str:
    """Return the checked-out commit, preferring CI-provided immutable SHAs."""
    for name in ("GITHUB_SHA", "CI_COMMIT_SHA"):
        value = os.environ.get(name, "").strip()
        if value:
            return value
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--root", default=".")
    p.add_argument("--output", default="artifacts/publication/submission/manifest.json")
    p.add_argument("--commit", default=None)
    args = p.parse_args()

    root = Path(args.root).resolve()
    records = []
    missing = []
    for rel in DEFAULT_PATHS:
        path = root / rel
        if not path.is_file():
            missing.append(rel)
            continue
        records.append(
            {
                "path": rel,
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    if missing:
        raise SystemExit("missing required submission files: " + ", ".join(missing))

    commit = (args.commit or detect_commit(root)).strip()
    if not commit or commit == "UNKNOWN":
        raise SystemExit("submission commit could not be determined; pass --commit or run inside a git checkout")

    payload = {
        "schema": "pcfmcw-isac-submission-manifest-v2",
        "frozen_scientific_baseline": "3904c4c2a69c4af96751d64614f7228ddea24b56",
        "submission_commit": commit,
        "evidence_scope": "SIMULATION_ANALYTICAL_STATISTICAL_AND_HOST_RUNTIME_NOT_CONTROLLER_HARDWARE_MEASUREMENT",
        "files": records,
    }
    output = root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote manifest with {len(records)} files to {output} for commit {commit}")


if __name__ == "__main__":
    main()
