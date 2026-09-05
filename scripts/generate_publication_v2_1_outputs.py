#!/usr/bin/env python3
"""Generate publication-ready tables from frozen v2.1 summary JSON files.

This script does not modify simulation outputs, thresholds, or policy logic. It
only reformats already-frozen summary evidence into CSV and LaTeX tables.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "artifacts" / "publication" / "v2_1"
OUT = EVIDENCE / "tables"
PAPER = ROOT / "paper"


def _load(name: str) -> dict:
    with (EVIDENCE / name).open("r", encoding="utf-8") as f:
        return json.load(f)


def _pct(x: float) -> str:
    return f"{100.0 * x:.2f}"


def write_policy_csv(final: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    fields = [
        "policy",
        "selection_rate",
        "abstention_rate",
        "joint_qos_unconditional",
        "joint_qos_conditional",
        "wilson_lower_95_unconditional",
        "wilson_lower_95_conditional",
        "mean_normalized_resource_cost_when_selected",
    ]
    with (OUT / "policy_summary.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for policy, metrics in final["aggregate"].items():
            rb = final["reliability_bounds"][policy]
            w.writerow({
                "policy": policy,
                "selection_rate": metrics["selection_rate"],
                "abstention_rate": metrics["abstention_rate"],
                "joint_qos_unconditional": metrics["joint_qos_probability_unconditional"],
                "joint_qos_conditional": metrics["joint_qos_probability_conditional_on_selection"],
                "wilson_lower_95_unconditional": rb["unconditional_wilson_lower_95"],
                "wilson_lower_95_conditional": rb["conditional_wilson_lower_95"],
                "mean_normalized_resource_cost_when_selected": metrics["mean_normalized_resource_cost_when_selected"],
            })


def write_paired_csv(final: dict) -> None:
    rows = []
    for label, key in [
        ("B4 minus B3", "paired_B4_minus_B3_joint_qos"),
        ("B4 minus B0", "paired_B4_minus_B0_joint_qos"),
    ]:
        x = final[key]
        rows.append({
            "comparison": label,
            "mean_paired_difference": x["mean_paired_difference"],
            "ci_low": x["ci_low"],
            "ci_high": x["ci_high"],
            "confidence": x["confidence"],
            "n_pairs": x["n_pairs"],
            "bootstrap_resamples": x["bootstrap_resamples"],
        })
    with (OUT / "paired_differences.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)


def write_e11_csv(e9e11: dict) -> None:
    rows = []
    for key in ["FULL_B4", "NO_STATE_UNCERTAINTY", "NO_CFO", "NO_INTERFERENCE"]:
        x = e9e11["e11"][key]
        rows.append({"ablation": key, **x})
    with (OUT / "e11_ablation.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)


def write_latex(final: dict, e9e11: dict) -> None:
    PAPER.mkdir(parents=True, exist_ok=True)
    lines = []
    lines += [
        "% Auto-generated from frozen v2.1 summary JSON. Do not edit numerical values manually.",
        "\\begin{table}[t]",
        "\\centering",
        "\\caption{Frozen v2.1 policy-level reliability and availability results.}",
        "\\label{tab:v21_policy}",
        "\\begin{tabular}{lrrrr}",
        "\\hline",
        "Policy & Selection (\\%) & Joint QoS (\\%) & Conditional QoS (\\%) & 95\\% Wilson LCB (cond.) \\\\",
        "\\hline",
    ]
    for policy, m in final["aggregate"].items():
        rb = final["reliability_bounds"][policy]
        lines.append(
            f"{policy.replace('_', ' ')} & {_pct(m['selection_rate'])} & {_pct(m['joint_qos_probability_unconditional'])} & "
            f"{_pct(m['joint_qos_probability_conditional_on_selection'])} & {_pct(rb['conditional_wilson_lower_95'])} \\\\" 
        )
    lines += ["\\hline", "\\end{tabular}", "\\end{table}", ""]

    lines += [
        "\\begin{table}[t]",
        "\\centering",
        "\\caption{Frozen v2.1 E11 ablation results.}",
        "\\label{tab:v21_e11}",
        "\\begin{tabular}{lrrr}",
        "\\hline",
        "Variant & Selection (\\%) & Joint QoS (\\%) & Conditional QoS (\\%) \\\\",
        "\\hline",
    ]
    for key in ["FULL_B4", "NO_STATE_UNCERTAINTY", "NO_CFO", "NO_INTERFERENCE"]:
        x = e9e11["e11"][key]
        lines.append(f"{key.replace('_', ' ')} & {_pct(x['selection_rate'])} & {_pct(x['joint_qos_rate_unconditional'])} & {_pct(x['conditional_joint_qos'])} \\\\")
    lines += ["\\hline", "\\end{tabular}", "\\end{table}", ""]

    p = final["paired_B4_minus_B3_joint_qos"]
    lines += [
        "% Frozen paired-bootstrap result for manuscript text:",
        f"% B4-B3 mean difference = {100*p['mean_paired_difference']:.3f} percentage points; "
        f"95% CI [{100*p['ci_low']:.3f}, {100*p['ci_high']:.3f}] pp.",
        "% Claim boundary: this does NOT support unconditional superiority of B4 over B3.",
        "% Hindsight ORACLE is a non-deployable reference and must be labeled as such.",
    ]
    (PAPER / "results_v2_1_tables.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    final = _load("FINAL_RESULTS.json")
    e9e11 = _load("E9_E11_RESULTS.json")
    assert final["protocol_id"] == e9e11["protocol_id"] == "pcfmcw_isac_paper_v2_1"
    assert final["workflow_run_id"] == e9e11["workflow_run_id"] == 33967030983
    write_policy_csv(final)
    write_paired_csv(final)
    write_e11_csv(e9e11)
    write_latex(final, e9e11)
    print(f"Wrote deterministic publication outputs under {OUT} and {PAPER}")


if __name__ == "__main__":
    main()
