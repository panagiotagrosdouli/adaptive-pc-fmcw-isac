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


def _write_pair(out: Path, stem: str, rows: list[dict], fields: list[str], caption: str, label: str) -> None:
    write_csv(out / f"{stem}.csv", rows, fields)
    write_latex(out / f"{stem}.tex", rows, fields, caption, label)


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
    _write_pair(out, "policy_comparison", rows, fields, "Policy comparison from machine-readable simulation artifacts.", "tab:policy-comparison")


def calibration_table(root: Path, out: Path) -> None:
    summary = load(root, "reliability-calibration")["summary"]
    rows = [{"robust_draws": draws, **metrics} for draws, metrics in sorted(summary.items(), key=lambda x: int(x[0]))]
    fields = [
        "robust_draws", "n", "max_possible_wilson_lower_95", "target_attainable_at_draw_count",
        "minimum_successes_to_accept", "minimum_empirical_success_fraction_to_accept",
        "false_feasible_rate", "false_infeasible_rate", "decision_disagreement_rate",
        "selected_action_disagreement_rate", "finite_selection_rate", "reference_selection_rate",
    ]
    _write_pair(
        out,
        "reliability_calibration",
        rows,
        fields,
        "Finite-draw reliability decision calibration with explicit Wilson-target attainability.",
        "tab:reliability-calibration",
    )


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
    _write_pair(out, "action_space_sensitivity", rows, fields, "PC-FMCW action-space sensitivity.", "tab:action-space")


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
    _write_pair(out, "distribution_shift", rows, fields, "Paired distribution-shift robustness study.", "tab:distribution-shift")


def runtime_table(root: Path, out: Path) -> None:
    summary = load(root, "runtime")["summary"]
    rows = [
        {"robust_draws": draws, "policy": policy, "median_us": m.get("median_us"), "p95_us": m.get("p95_us"), "p99_us": m.get("p99_us")}
        for draws, policies in sorted(summary.items(), key=lambda x: int(x[0]))
        for policy, m in policies.items()
    ]
    fields = list(rows[0]) if rows else ["robust_draws"]
    _write_pair(out, "runtime", rows, fields, "Controller decision runtime; microseconds.", "tab:runtime")


def reliability_target_table(root: Path, out: Path) -> None:
    summary = load(root, "reliability-targets")["summary"]
    rows = [{
        "target": target,
        "selection_rate": m.get("selection_rate"),
        "joint_qos_unconditional": m.get("joint_qos_probability_unconditional"),
        "joint_qos_conditional": m.get("joint_qos_probability_conditional"),
        "wilson_lower_95_conditional": m.get("wilson_lower_95_conditional"),
        "mean_resource_cost_selected": m.get("mean_normalized_resource_cost_selected"),
    } for target, m in sorted(summary.items(), key=lambda x: float(x[0]))]
    fields = list(rows[0]) if rows else ["target"]
    _write_pair(out, "reliability_target_sensitivity", rows, fields, "Reliability-target sensitivity with common robust draws.", "tab:reliability-targets")


def qos_sensitivity_table(root: Path, out: Path) -> None:
    summary = load(root, "qos-sensitivity")["summary"]
    rows = []
    for variant, policies in summary.items():
        for policy, m in policies.items():
            rows.append({
                "qos_variant": variant,
                "policy": policy,
                "selection_rate": m.get("selection_rate"),
                "counterfactual_joint_qos_unconditional": m.get("counterfactual_joint_qos_unconditional"),
                "counterfactual_joint_qos_conditional": m.get("counterfactual_joint_qos_conditional"),
                "wilson_lower_95_conditional": m.get("wilson_lower_95_conditional"),
            })
    fields = list(rows[0]) if rows else ["qos_variant"]
    _write_pair(out, "qos_threshold_sensitivity", rows, fields, "Post-selection counterfactual QoS-threshold sensitivity.", "tab:qos-sensitivity")


def uncertainty_sources_table(root: Path, out: Path) -> None:
    summary = load(root, "uncertainty-sources")["summary"]
    rows = [{
        "variant": variant,
        "selection_rate": m.get("selection_rate"),
        "joint_qos_unconditional": m.get("joint_qos_probability_unconditional"),
        "joint_qos_conditional": m.get("joint_qos_probability_conditional"),
        "wilson_lower_95_conditional": m.get("wilson_lower_95_conditional"),
    } for variant, m in summary.items()]
    fields = list(rows[0]) if rows else ["variant"]
    _write_pair(out, "uncertainty_source_ablation", rows, fields, "Selector-side uncertainty-source ablation.", "tab:uncertainty-sources")


def confidence_maps_table(root: Path, out: Path) -> None:
    maps = load(root, "confidence-maps")
    rows = []
    for map_name, data in maps.items():
        for cell in data.get("cells", []):
            rows.append({
                "map": map_name,
                "x": cell.get("x"),
                "y": cell.get("y"),
                "selection_rate": cell.get("selection_rate"),
                "joint_qos_unconditional": cell.get("joint_qos_probability_unconditional"),
                "joint_qos_conditional": cell.get("joint_qos_probability_conditional"),
                "wilson_lower_95_conditional": cell.get("wilson_lower_95_conditional"),
                "confidence_qualified_target_0p95": cell.get("confidence_qualified_target_0p95"),
            })
    fields = list(rows[0]) if rows else ["map"]
    _write_pair(out, "confidence_qualified_maps", rows, fields, "Confidence-qualified B4 operating-region cells.", "tab:confidence-maps")


def pareto_table(root: Path, out: Path) -> None:
    data = load(root, "pareto")
    points = data.get("physical_points", [])
    partition = data.get("pareto", {})
    dominated = {int(p["point_index"]): p.get("dominated_by_indices", []) for p in partition.get("dominated_points", [])}
    frontier = {int(p["point_index"]) for p in partition.get("non_dominated_points", [])}
    rows = []
    for i, point in enumerate(points):
        rows.append({
            "point_index": i,
            "non_dominated": i in frontier,
            "dominated_by_indices": ";".join(str(v) for v in dominated.get(i, [])),
            "joint_qos_probability": point.get("joint_qos_probability"),
            "mean_effective_rate_bps": point.get("mean_effective_rate_bps"),
            "tx_power_fraction": point.get("tx_power_fraction"),
            "repetition_factor": point.get("repetition_factor"),
            "chips_per_chirp": point.get("chips_per_chirp"),
            "profile_adc_samples_per_frame": point.get("profile_adc_samples_per_frame"),
            "mean_range_rmse_m": point.get("mean_range_rmse_m"),
            "mean_velocity_rmse_mps": point.get("mean_velocity_rmse_mps"),
            "n": point.get("n"),
        })
    fields = list(rows[0]) if rows else ["point_index"]
    _write_pair(out, "empirical_pareto", rows, fields, "Empirical non-dominance partition over realized B4-selected operating points.", "tab:pareto")


def main() -> None:
    args = parse_args(); root = Path(args.input_dir); out = Path(args.output_dir)
    policy_table(root, out)
    calibration_table(root, out)
    action_space_table(root, out)
    distribution_shift_table(root, out)
    runtime_table(root, out)
    reliability_target_table(root, out)
    qos_sensitivity_table(root, out)
    uncertainty_sources_table(root, out)
    confidence_maps_table(root, out)
    pareto_table(root, out)


if __name__ == "__main__":
    main()
