#!/usr/bin/env python3
"""Generate publication tables from machine-readable research artifacts only."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Iterable


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--input-dir", default="artifacts/research")
    p.add_argument("--output-dir", default="artifacts/research/tables")
    return p.parse_args()


def load(root: Path, name: str) -> dict:
    path = root / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(path)
    payload = json.loads(path.read_text())
    if "results" not in payload:
        raise ValueError(f"missing results envelope in {path}")
    return payload["results"]


def write_csv(path: Path, rows: Iterable[dict], fields: list[str]) -> None:
    rows = list(rows)
    if not rows:
        raise ValueError(f"refusing to write empty table {path.name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _latex_escape(value: object) -> str:
    text = "" if value is None else str(value)
    for old, new in (("\\", r"\textbackslash{}"), ("_", r"\_"), ("%", r"\%"), ("&", r"\&"), ("#", r"\#")):
        text = text.replace(old, new)
    return text


def write_latex(path: Path, rows: list[dict], fields: list[str], caption: str, label: str) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty table {path.name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    row_end = " \\\\"
    lines = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\small",
        r"\begin{tabular}{" + "l" * len(fields) + "}",
        r"\hline",
        " & ".join(_latex_escape(f) for f in fields) + row_end,
        r"\hline",
    ]
    for row in rows:
        lines.append(" & ".join(_latex_escape(row.get(f)) for f in fields) + row_end)
    lines += [
        r"\hline",
        r"\end{tabular}",
        f"\\caption{{{_latex_escape(caption)}}}",
        f"\\label{{{_latex_escape(label)}}}",
        r"\end{table*}",
    ]
    path.write_text("\n".join(lines) + "\n")


def policy_table(root: Path, out: Path) -> None:
    summary = load(root, "full-metrics")["summary"]
    rows = [{
        "policy": policy,
        "n": m.get("n"),
        "selection_rate": m.get("selection_rate"),
        "joint_qos_unconditional": m.get("joint_qos_probability_unconditional"),
        "joint_qos_conditional": m.get("joint_qos_probability_conditional"),
        "wilson_lower_95_conditional": m.get("wilson_lower_95_conditional"),
        "mean_resource_cost_selected": m.get("mean_normalized_resource_cost_selected"),
    } for policy, m in summary.items()]
    fields = list(rows[0]) if rows else ["policy"]
    write_csv(out / "policy_comparison.csv", rows, fields)
    write_latex(out / "policy_comparison.tex", rows, fields, "Policy comparison from machine-readable simulation artifacts.", "tab:policy-comparison")


def calibration_table(root: Path, out: Path) -> None:
    summary = load(root, "reliability-calibration")["summary"]
    rows = [{"robust_draws": draws, **metrics} for draws, metrics in sorted(summary.items(), key=lambda x: int(x[0]))]
    fields = ["robust_draws", "n", "false_feasible_rate", "false_infeasible_rate", "decision_disagreement_rate", "selected_action_disagreement_rate", "finite_selection_rate", "reference_selection_rate"]
    write_csv(out / "reliability_calibration.csv", rows, fields)
    write_latex(out / "reliability_calibration.tex", rows, fields, "Finite-draw reliability decision calibration.", "tab:reliability-calibration")


def action_space_table(root: Path, out: Path) -> None:
    summary = load(root, "action-space")["summary"]
    rows = [{
        "variant": variant,
        "selection_rate": m.get("selection_rate"),
        "joint_qos_unconditional": m.get("joint_qos_probability_unconditional"),
        "joint_qos_conditional": m.get("joint_qos_probability_conditional"),
        "wilson_lower_95_conditional": m.get("wilson_lower_95_conditional"),
        "mean_resource_cost_selected": m.get("mean_normalized_resource_cost_selected"),
    } for variant, m in summary.items()]
    fields = list(rows[0]) if rows else ["variant"]
    write_csv(out / "action_space_sensitivity.csv", rows, fields)
    write_latex(out / "action_space_sensitivity.tex", rows, fields, "PC-FMCW action-space sensitivity.", "tab:action-space")


def distribution_shift_table(root: Path, out: Path) -> None:
    data = load(root, "distribution-shift")
    rows = []
    stats = data.get("paired_statistics", {})
    for family, policies in data["summary"].items():
        stat = stats.get(family, {})
        for policy, m in policies.items():
            rows.append({
                "family": family,
                "policy": policy,
                "selection_rate": m.get("selection_rate"),
                "joint_qos_unconditional": m.get("joint_qos_probability_unconditional"),
                "joint_qos_conditional": m.get("joint_qos_probability_conditional"),
                "wilson_lower_95_conditional": m.get("wilson_lower_95_conditional"),
                "paired_b4_minus_b3": stat.get("mean_difference_a_minus_b"),
                "paired_ci_low": stat.get("ci_low"),
                "paired_ci_high": stat.get("ci_high"),
            })
    fields = list(rows[0]) if rows else ["family"]
    write_csv(out / "distribution_shift.csv", rows, fields)
    write_latex(out / "distribution_shift.tex", rows, fields, "Paired distribution-shift robustness study.", "tab:distribution-shift")


def runtime_table(root: Path, out: Path) -> None:
    summary = load(root, "runtime")["summary"]
    rows = [
        {"robust_draws": draws, "policy": policy, "median_us": m.get("median_us"), "p95_us": m.get("p95_us"), "p99_us": m.get("p99_us")}
        for draws, policies in sorted(summary.items(), key=lambda x: int(x[0]))
        for policy, m in policies.items()
    ]
    fields = list(rows[0]) if rows else ["robust_draws"]
    write_csv(out / "runtime.csv", rows, fields)
    write_latex(out / "runtime.tex", rows, fields, "Controller decision runtime; microseconds.", "tab:runtime")


def main() -> None:
    args = parse_args(); root = Path(args.input_dir); out = Path(args.output_dir)
    policy_table(root, out)
    calibration_table(root, out)
    action_space_table(root, out)
    distribution_shift_table(root, out)
    runtime_table(root, out)


if __name__ == "__main__":
    main()
