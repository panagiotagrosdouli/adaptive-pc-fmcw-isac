#!/usr/bin/env python3
"""Run frozen Stage-07 comparison families from scenario-level CSV evidence."""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("stage07_statistics", HERE / "statistics.py")
STATS = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = STATS
SPEC.loader.exec_module(STATS)


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def filtered(records: list[dict], filters: dict) -> list[dict]:
    return [row for row in records if all(str(row.get(k)) == str(v) for k, v in filters.items())]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence", type=Path)
    parser.add_argument("comparisons", type=Path, help="predeclared JSON list")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--bootstrap-repetitions", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=20260904)
    args = parser.parse_args()
    evidence = read_csv(args.evidence)
    definitions = json.loads(args.comparisons.read_text())
    if not isinstance(definitions, list) or not definitions:
        raise SystemExit("comparison manifest must be a non-empty JSON list")
    results = []
    for index, definition in enumerate(definitions):
        rows = filtered(evidence, definition.get("filters", {}))
        _, delta = STATS.paired_deltas(
            rows, definition["group_column"], definition["metric"],
            definition["treatment"], definition["control"],
            bool(definition["higher_is_better"]), definition.get("cluster_column", "scenario_id"),
        )
        result = STATS.analyze_delta(delta, args.bootstrap_repetitions, args.seed + index)
        results.append({"comparison_id": definition["comparison_id"],
                        "family": definition["family"], **result.__dict__})
    by_family = {}
    for i, result in enumerate(results):
        by_family.setdefault(result["family"], []).append(i)
    for indices in by_family.values():
        adjusted = STATS.holm_adjust([results[i]["wilcoxon_p"] for i in indices])
        for i, value in zip(indices, adjusted):
            results[i]["holm_wilcoxon_p"] = value
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(results[0]))
        writer.writeheader(); writer.writerows(results)
    print(json.dumps({"comparisons": len(results), "families": sorted(by_family),
                      "bootstrap_repetitions": args.bootstrap_repetitions,
                      "aggregation_unit": "scenario"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
