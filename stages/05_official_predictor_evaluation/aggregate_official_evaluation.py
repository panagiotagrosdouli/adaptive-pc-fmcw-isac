#!/usr/bin/env python3
"""Validate and aggregate immutable Stage-05 official-validation outputs."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

OBJECTIVES = (
    "trajectory",
    "trajectory_plus_link",
    "trajectory_plus_outage",
    "full_communication_aware",
)
METRICS = (
    "ade_m", "fde_m", "range_mae_m", "bearing_mae_rad", "snr_mae_db",
    "goodput_mae_bps", "outage_f1", "outage_auroc",
    "link_lifetime_abs_error_s", "nll", "coverage_50", "coverage_90",
    "coverage_95",
)
LOWER_IS_BETTER = set(METRICS) - {"outage_f1", "outage_auroc", "coverage_50", "coverage_90", "coverage_95"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _number(value: str):
    if value is None or not str(value).strip():
        return None
    result = float(value)
    return result if math.isfinite(result) else None


def read_rows(paths: list[Path]) -> list[dict]:
    rows = []
    for path in paths:
        with path.open(newline="") as handle:
            for raw in csv.DictReader(handle):
                row = dict(raw)
                row["source_file"] = path.name
                rows.append(row)
    return rows


def validate(rows: list[dict], expected_seeds: list[int], require_complete_archive: bool) -> list[str]:
    errors, keys = [], set()
    learned = defaultdict(set)
    if not rows:
        return ["no scenario rows supplied"]
    for line, row in enumerate(rows, 2):
        label = f"{row.get('source_file', '?')}:{line}"
        if row.get("split") != "official_validation":
            errors.append(f"{label}: split must be official_validation")
        if not row.get("scenario_id") or not row.get("predictor"):
            errors.append(f"{label}: scenario_id and predictor are required")
        key = (row.get("scenario_id"), row.get("predictor"), row.get("seed", ""))
        if key in keys:
            errors.append(f"{label}: duplicate scenario/predictor/seed {key}")
        keys.add(key)
        objective, seed = row.get("objective", ""), row.get("seed", "")
        if objective:
            try:
                learned[objective].add(int(seed))
            except ValueError:
                errors.append(f"{label}: learned row requires an integer seed")
        for metric in METRICS:
            value = row.get(metric, "")
            support = row.get(f"{metric}_support", row.get("actor_samples", ""))
            if str(value).strip() and _number(value) is None:
                errors.append(f"{label}: {metric} is non-finite")
            if not str(value).strip() and not str(support).strip():
                errors.append(f"{label}: undefined {metric} requires an explicit support count")
    if require_complete_archive:
        wanted = set(expected_seeds)
        for objective in OBJECTIVES:
            if learned[objective] != wanted:
                errors.append(f"{objective}: seeds {sorted(learned[objective])}, expected {sorted(wanted)}")
        extras = sorted(set(learned) - set(OBJECTIVES))
        if extras:
            errors.append(f"unexpected learned objectives: {extras}")
    return errors


def aggregate(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    groups = defaultdict(list)
    for row in rows:
        groups[row["predictor"]].append(row)
    summaries = []
    for predictor, items in sorted(groups.items()):
        out = {"predictor": predictor, "scenario_rows": len(items),
               "unique_scenarios": len({x["scenario_id"] for x in items})}
        for metric in METRICS:
            values = [v for v in (_number(x.get(metric, "")) for x in items) if v is not None]
            out[metric] = sum(values) / len(values) if values else ""
            out[f"{metric}_support"] = len(values)
        summaries.append(out)
    rankings = []
    for metric in METRICS:
        eligible = [x for x in summaries if x[metric] != ""]
        eligible.sort(key=lambda x: x[metric], reverse=metric not in LOWER_IS_BETTER)
        for rank, row in enumerate(eligible, 1):
            rankings.append({"metric": metric, "rank": rank, "predictor": row["predictor"],
                             "value": row[metric], "scenario_support": row[f"{metric}_support"]})
    return summaries, rankings


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted(set().union(*(row.keys() for row in rows))) if rows else []
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--official-dataset", type=Path, required=True)
    parser.add_argument("--checkpoint-archive-manifest", type=Path, required=True)
    parser.add_argument("--calibration-manifest", type=Path, required=True)
    parser.add_argument("--link-config", type=Path, required=True)
    parser.add_argument("--ber-lut", type=Path, required=True)
    parser.add_argument("--seeds", default="11,22,33,44,55")
    parser.add_argument("--allow-incomplete-archive", action="store_true", help="development/testing only")
    args = parser.parse_args()
    seeds = [int(x) for x in args.seeds.split(",")]
    archive = json.loads(args.checkpoint_archive_manifest.read_text())
    calibration = json.loads(args.calibration_manifest.read_text())
    pre_errors = []
    if archive.get("passed") is not True or archive.get("checkpoint_count") != 20:
        pre_errors.append("Stage-04 checkpoint archive is not a passed 20-checkpoint archive")
    if calibration.get("fit_split") != "development" or calibration.get("official_validation_used_for_fit") is not False:
        pre_errors.append("calibration provenance is not development-only")
    rows = read_rows(args.inputs)
    errors = pre_errors + validate(rows, seeds, not args.allow_incomplete_archive)
    if errors:
        raise SystemExit("Stage-05 acceptance gate failed:\n- " + "\n- ".join(errors))
    summaries, rankings = aggregate(rows)
    write_csv(args.output_dir / "scenario_metrics.csv", rows)
    write_csv(args.output_dir / "aggregate_metrics.csv", summaries)
    (args.output_dir / "aggregate_metrics.json").write_text(
        json.dumps(summaries, indent=2, sort_keys=True) + "\n"
    )
    calibration_rows = [
        {key: value for key, value in row.items() if key in {
            "predictor", "scenario_rows", "unique_scenarios", "nll", "nll_support",
            "coverage_50", "coverage_50_support", "coverage_90", "coverage_90_support",
            "coverage_95", "coverage_95_support",
        }}
        for row in summaries
        if row["nll_support"] or row["coverage_50_support"]
    ]
    write_csv(args.output_dir / "calibration_metrics.csv", calibration_rows)
    write_csv(args.output_dir / "model_ranking.csv", rankings)
    manifest = {
        "schema": "stage05_official_predictor_evaluation_v1",
        "passed": True,
        "selection_frozen_before_official_evaluation": True,
        "official_validation_used_for_selection": False,
        "aggregation_unit": "scenario",
        "scenario_count": len({r["scenario_id"] for r in rows}),
        "row_count": len(rows),
        "predictors": sorted({r["predictor"] for r in rows}),
        "inputs_sha256": {p.name: sha256(p) for p in args.inputs},
        "provenance_sha256": {
            "official_dataset": sha256(args.official_dataset),
            "checkpoint_archive_manifest": sha256(args.checkpoint_archive_manifest),
            "calibration_manifest": sha256(args.calibration_manifest),
            "link_config": sha256(args.link_config),
            "ber_lut": sha256(args.ber_lut),
        },
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
