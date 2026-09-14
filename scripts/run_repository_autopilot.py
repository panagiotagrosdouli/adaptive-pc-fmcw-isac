#!/usr/bin/env python3
"""Fail-closed repository autopilot for scientific and submission readiness.

This script intentionally orchestrates existing repository-native checks rather than
re-implementing scientific logic. Frozen publication evidence is read/validated but
never rewritten. A run is considered successful only when every mandatory stage exits
with code 0.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS_DIR = ROOT / "artifacts" / "autopilot"


def run_stage(name: str, command: list[str], cwd: Path | None = None) -> dict:
    started = time.time()
    proc = subprocess.run(command, cwd=cwd or ROOT, text=True)
    return {
        "name": name,
        "command": command,
        "returncode": proc.returncode,
        "duration_s": round(time.time() - started, 3),
        "ok": proc.returncode == 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("smoke", "submission"), default="submission")
    parser.add_argument("--status", default=str(STATUS_DIR / "status.json"))
    args = parser.parse_args()

    py = sys.executable
    stages: list[tuple[str, list[str], Path | None]] = [
        ("tests", [py, "-m", "pytest", "-q"], None),
        ("submission_action_space", [py, "scripts/export_submission_action_space.py", "--output", "artifacts/publication/submission/action_space.csv"], None),
        ("submission_manifest", [py, "scripts/build_submission_manifest.py", "--output", "artifacts/publication/submission/manifest.json"], None),
        ("repository_audit", [py, "scripts/audit_repository.py"], None),
        ("stage7_smoke", [py, "scripts/run_stage7_validation.py", "--sensing-trials", "1", "--high-mobility-trials", "1", "--comm-bits", "2000", "--output", "artifacts/autopilot/stage7.json"], None),
        ("e1_e5_smoke", [py, "scripts/run_e1_e5_validation.py", "--output", "artifacts/autopilot/e1_e5.json"], None),
        ("e6_e12_smoke", [py, "scripts/run_e6_e12_benchmark.py", "--n-seeds", "2", "--comm-bits", "2000", "--sensing-trials", "1", "--output", "artifacts/autopilot/e6_e12.json"], None),
        ("supplemental_smoke", [py, "scripts/run_supplemental_v2_1.py", "--experiment", "all-smoke", "--seed-start", "10000", "--n-seeds", "1", "--comm-bits", "500", "--sensing-trials", "1", "--robust-draws", "16", "--reference-draws", "32", "--truth-draws", "1", "--bootstrap-resamples", "100", "--output", "artifacts/autopilot/supplemental.json"], None),
    ]

    if args.mode == "submission":
        stages.extend([
            ("paper1_build", ["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", "paper1_ieee.tex"], ROOT / "paper"),
            ("paper2_build", ["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", "paper2_ieee.tex"], ROOT / "paper"),
            ("submission_bundle", [py, "scripts/build_submission_bundle.py", "--output", "artifacts/publication/submission/adaptive-pc-fmcw-isac-submission-v2.1.zip"], None),
        ])

    STATUS_DIR.mkdir(parents=True, exist_ok=True)
    status_path = ROOT / args.status if not Path(args.status).is_absolute() else Path(args.status)
    status_path.parent.mkdir(parents=True, exist_ok=True)

    results = []
    for name, command, cwd in stages:
        result = run_stage(name, command, cwd)
        results.append(result)
        status_path.write_text(json.dumps({
            "mode": args.mode,
            "complete": False,
            "passed": False,
            "stages": results,
        }, indent=2) + "\n")
        if not result["ok"]:
            status_path.write_text(json.dumps({
                "mode": args.mode,
                "complete": True,
                "passed": False,
                "failed_stage": name,
                "stages": results,
            }, indent=2) + "\n")
            return result["returncode"] or 1

    status_path.write_text(json.dumps({
        "mode": args.mode,
        "complete": True,
        "passed": True,
        "stages": results,
    }, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
