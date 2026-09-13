#!/usr/bin/env python3
"""Repository-wide scientific/submission consistency audit.

This gate is intentionally broader than unit tests.  It checks machine-readable
artifacts, frozen protocol invariants, code/config profile agreement, manuscript
source/citation integrity, and selected claim-boundary regressions.
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path

from pcfmcw_isac.profiles import high_mobility_profile, short_range_profile
from pcfmcw_isac.publication_protocol import FROZEN_PROTOCOL_V1

ROOT = Path(__file__).resolve().parents[1]


class AuditFailure(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditFailure(message)


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - message preserved for CI
        raise AuditFailure(f"invalid JSON {path.relative_to(ROOT)}: {exc}") from exc


def audit_all_json() -> None:
    for path in sorted(ROOT.rglob("*.json")):
        if any(part in {".git", ".venv", "venv", "build", "dist"} for part in path.parts):
            continue
        load_json(path)


def audit_protocol_and_results() -> None:
    cfg = load_json(ROOT / "configs/paper_protocol_v2_1.json")
    require(cfg["protocol_id"] == "pcfmcw_isac_paper_v2_1", "wrong frozen v2.1 protocol id")
    sem = cfg["v2_1_semantics"]
    require(sem["b4_internal_draws"] == 512, "frozen v2.1 B4 draw count must be 512")
    require(math.isclose(sem["b4_reliability_confidence"], 0.95), "wrong B4 confidence")
    require(sem["no_post_hoc_threshold_tuning"] is True, "post-hoc tuning guard must remain true")
    paired = cfg["paired_benchmark"]
    require(paired["n_scenarios_per_seed"] == 12, "frozen scenario count changed")
    require(paired["n_seeds_final"] == 1000, "frozen seed count changed")
    require(paired["comm_bits_final"] == 20000, "frozen comm bit budget changed")
    require(paired["sensing_trials_final"] == 3, "frozen sensing trial budget changed")
    require(paired["bootstrap_resamples"] == 10000, "frozen bootstrap budget changed")

    results = load_json(ROOT / "artifacts/publication/v2_1/FINAL_RESULTS.json")
    require(results["protocol_id"] == cfg["protocol_id"], "result/config protocol id mismatch")
    require("NOT_HARDWARE_MEASUREMENT" in results["evidence_class"], "frozen evidence class lost simulation boundary")
    require(results["n_records"] == 72000, "frozen record count changed")
    require(results["n_states_per_policy"] == 12000, "frozen states/policy changed")
    require(set(results["aggregate"]) == set(cfg["policies"]), "policy set mismatch between config and results")

    for policy, row in results["aggregate"].items():
        require(math.isclose(row["selection_rate"] + row["abstention_rate"], 1.0, abs_tol=1e-12), f"{policy}: selection+abstention != 1")
        bounds = results["reliability_bounds"][policy]
        require(bounds["unconditional_trials"] == 12000, f"{policy}: wrong unconditional trial count")
        selected = round(row["selection_rate"] * 12000)
        require(bounds["conditional_trials"] == selected, f"{policy}: conditional trials do not match selected states")
        require(bounds["conditional_successes"] <= bounds["conditional_trials"], f"{policy}: impossible conditional counts")

    b4 = results["reliability_bounds"]["B4_ROBUST_JOINT"]
    require((b4["conditional_successes"], b4["conditional_trials"]) == (1468, 1468), "frozen B4 1468/1468 result changed")
    require(results["aggregate"]["B4_ROBUST_JOINT"]["joint_qos_probability_conditional_on_selection"] == 1.0, "frozen B4 conditional QoS changed")
    delta = results["paired_B4_minus_B3_joint_qos"]
    require(delta["n_pairs"] == 12000 and delta["bootstrap_resamples"] == 10000, "paired B4-B3 protocol changed")
    require(delta["ci_high"] < 0.0, "frozen B4-B3 unconditional CI no longer matches negative result")
    require(results["sanity_gate"]["b4_superiority_over_b3_supported"] is False, "unsupported B4 superiority flag detected")


def audit_profiles_and_actions() -> None:
    mappings = (
        (ROOT / "configs/ti_77ghz_parking_profile.json", short_range_profile()),
        (ROOT / "configs/ti_77ghz_high_mobility_capability_profile.json", high_mobility_profile()),
    )
    fields = (
        "carrier_hz", "bandwidth_hz", "chirp_duration_s", "chirp_repetition_s",
        "sample_rate_hz", "samples_per_chirp", "n_chirps",
    )
    for path, profile in mappings:
        cfg = load_json(path)
        profile.validate()
        for field in fields:
            lhs = cfg[field]
            rhs = getattr(profile, field)
            if isinstance(lhs, float) or isinstance(rhs, float):
                require(math.isclose(float(lhs), float(rhs), rel_tol=0.0, abs_tol=max(1e-15, abs(float(lhs))*1e-12)), f"{path.name}: code/config drift in {field}")
            else:
                require(lhs == rhs, f"{path.name}: code/config drift in {field}")

    actions = FROZEN_PROTOCOL_V1.actions()
    require(len(actions) == 54, f"frozen action space must have 54 actions, found {len(actions)}")
    require(len(set(actions)) == 54, "frozen action space contains duplicates")


def _paper_sources() -> list[Path]:
    manifest = ROOT / "paper/SUBMISSION_SOURCE_MANIFEST.txt"
    require(manifest.is_file(), "missing paper submission source manifest")
    names = [line.strip() for line in manifest.read_text(encoding="utf-8").splitlines() if line.strip()]
    require(len(names) == len(set(names)), "duplicate entries in paper source manifest")
    require("figures_submission.tex" in names, "figure source omitted from paper source manifest")
    require("literature_positioning.tex" in names, "literature positioning omitted from paper source manifest")
    paths = []
    for name in names:
        require(not name.startswith("/") and ".." not in Path(name).parts, f"unsafe paper manifest path: {name}")
        path = ROOT / "paper" / name
        require(path.is_file(), f"paper manifest references missing file: {name}")
        paths.append(path)
    return paths


def audit_manuscript_and_bibliography() -> None:
    sources = _paper_sources()
    manuscript = ROOT / "paper/manuscript_v2_1.tex"
    text = manuscript.read_text(encoding="utf-8")
    require("\\documentclass[journal]{IEEEtran}" in text, "manuscript is not IEEEtran journal style")
    require("\\input{figures_submission}" in text, "submission figures are not included in manuscript")
    require("\\input{literature_positioning}" in text, "literature positioning table is not included")

    forbidden = {
        "frozen 256-draw": "stale frozen draw count",
        "prototype latency": "host runtime mislabeled as prototype latency",
        "hardware-validated controller": "unsupported hardware-validation claim",
        "universally outperforms": "unsupported universal superiority claim",
    }
    combined_tex = "\n".join(p.read_text(encoding="utf-8") for p in sources if p.suffix == ".tex")
    lower = combined_tex.lower()
    for phrase, reason in forbidden.items():
        require(phrase not in lower, f"{reason}: {phrase!r}")

    cite_keys: set[str] = set()
    for match in re.finditer(r"\\cite\{([^}]+)\}", combined_tex):
        cite_keys.update(k.strip() for k in match.group(1).split(",") if k.strip())

    bib_keys: list[str] = []
    for bib in (ROOT / "paper/references_v2_1.bib", ROOT / "paper/references_submission.bib"):
        content = bib.read_text(encoding="utf-8")
        bib_keys.extend(re.findall(r"@\w+\s*\{\s*([^,\s]+)", content))
    duplicates = sorted({k for k in bib_keys if bib_keys.count(k) > 1})
    require(not duplicates, "duplicate BibTeX keys across bibliography files: " + ", ".join(duplicates))
    missing = sorted(cite_keys - set(bib_keys))
    require(not missing, "undefined citation keys: " + ", ".join(missing))

    table = (ROOT / "paper/results_v2_1_tables.tex").read_text(encoding="utf-8")
    results = load_json(ROOT / "artifacts/publication/v2_1/FINAL_RESULTS.json")
    for policy, label in {
        "B0_FIXED": "B0 FIXED", "B1_COMM_ONLY": "B1 COMM ONLY", "B2_SENSING_ONLY": "B2 SENSING ONLY",
        "B3_DETERMINISTIC_JOINT": "B3 DETERMINISTIC JOINT", "B4_ROBUST_JOINT": "B4 ROBUST JOINT", "ORACLE": "ORACLE",
    }.items():
        row = results["aggregate"][policy]
        expected = f"{label} & {100*row['selection_rate']:.2f} & {100*row['joint_qos_probability_unconditional']:.2f} & {100*row['joint_qos_probability_conditional_on_selection']:.2f}"
        require(expected in table, f"paper results table drift for {policy}")


def audit_repo_text_hygiene() -> None:
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".py", ".md", ".tex", ".yml", ".yaml", ".toml"}:
            continue
        if any(part in {".git", ".venv", "venv", "build", "dist"} for part in path.parts):
            continue
        text = path.read_text(encoding="utf-8", errors="strict")
        for marker in ("TODO", "FIXME"):
            require(marker not in text, f"unfinished marker {marker} in {path.relative_to(ROOT)}")


def audit_makefile_and_workflows() -> None:
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    for target in ("test:", "paper:", "submission-artifacts:", "submission-check:", "repo-audit:"):
        require(target in makefile, f"Makefile missing target {target[:-1]}")
    require("scripts/audit_repository.py" in makefile, "repo-audit target does not invoke repository audit")
    ci = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    require("audit_repository.py" in ci, "CI does not run repository-wide audit")
    require("export_submission_action_space.py" in ci, "CI does not validate action-space export")
    require("build_submission_manifest.py" in ci, "CI does not build submission provenance manifest")
    latex = (ROOT / ".github/workflows/manuscript_latex.yml").read_text(encoding="utf-8")
    require("latexmk" in latex and "undefined citations" in latex.lower(), "manuscript workflow lacks build/citation gate")


def run_audit() -> None:
    checks = (
        audit_all_json,
        audit_protocol_and_results,
        audit_profiles_and_actions,
        audit_manuscript_and_bibliography,
        audit_repo_text_hygiene,
        audit_makefile_and_workflows,
    )
    for check in checks:
        check()
        print(f"PASS {check.__name__}")
    print(f"PASS repository audit ({len(checks)} check groups)")


if __name__ == "__main__":
    run_audit()
