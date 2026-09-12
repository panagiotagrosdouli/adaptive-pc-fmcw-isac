#!/usr/bin/env python3
"""Fail closed when required research evidence is missing or structurally invalid."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

REQUIRED = (
    "uncertainty", "stress", "physics", "pareto", "ablations", "mismatch",
    "distribution-shift", "runtime", "full-metrics", "reliability-targets",
    "confidence-maps", "uncertainty-sources", "reliability-calibration", "action-space",
)
EXPECTED_EVIDENCE_CLASS = "SUPPLEMENTAL_PUBLICATION_V2_1_SIMULATION_NOT_HARDWARE_MEASUREMENT"


def parse_args() -> argparse.Namespace:
    p=argparse.ArgumentParser(); p.add_argument("--input-dir",default="artifacts/research"); p.add_argument("--output",default=None); return p.parse_args()


def _finite_tree(value: Any, path: str = "results") -> list[str]:
    errors=[]
    if isinstance(value,float) and not math.isfinite(value): errors.append(f"{path}: non-finite float")
    elif isinstance(value,dict):
        for key,item in value.items(): errors.extend(_finite_tree(item,f"{path}.{key}"))
    elif isinstance(value,list):
        for index,item in enumerate(value): errors.extend(_finite_tree(item,f"{path}[{index}]"))
    return errors


def _require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition: errors.append(message)


def validate_artifact(name: str, payload: dict) -> list[str]:
    errors=[]
    _require(payload.get("evidence_class")==EXPECTED_EVIDENCE_CLASS,f"{name}: wrong/missing evidence_class",errors)
    _require(payload.get("frozen_parent_protocol")=="pcfmcw_isac_paper_v2_1",f"{name}: wrong/missing frozen parent protocol",errors)
    _require(payload.get("experiment")==name,f"{name}: experiment label mismatch",errors)
    _require("results" in payload,f"{name}: missing results",errors)
    if "results" not in payload: return errors
    results=payload["results"]; errors.extend(f"{name}: {x}" for x in _finite_tree(results))

    if name=="full-metrics":
        summary=results.get("summary",{})
        for policy in ("B0_FIXED","B1_COMM_ONLY","B2_SENSING_ONLY","B3_DETERMINISTIC_JOINT","B4_ROBUST_JOINT","ORACLE"):
            _require(policy in summary,f"{name}: missing policy {policy}",errors)
        if "B4_ROBUST_JOINT" in summary:
            b4=summary["B4_ROBUST_JOINT"]
            _require(b4.get("selected",0)>0,f"{name}: B4 selected zero states",errors)
            _require(b4.get("wilson_lower_95_conditional") is not None,f"{name}: B4 conditional Wilson bound missing",errors)
    elif name=="reliability-calibration":
        summary=results.get("summary",{}); _require(bool(summary),f"{name}: empty calibration summary",errors)
        for draws,row in summary.items():
            for key in ("false_feasible_rate","false_infeasible_rate","decision_disagreement_rate","selected_action_disagreement_rate"):
                val=row.get(key); _require(isinstance(val,(int,float)) and 0.0<=val<=1.0,f"{name}: invalid {key} at draws={draws}",errors)
    elif name=="action-space":
        summary=results.get("summary",{})
        for variant in ("FULL","HIGH_MOBILITY_PROFILE_ONLY","PARKING_PROFILE_ONLY","NO_REPETITION","FIXED_32_CHIPS","NO_POWER_BACKOFF"):
            _require(variant in summary,f"{name}: missing variant {variant}",errors)
    elif name=="physics":
        _require(bool(results.get("cells",[])),f"{name}: empty physical map",errors)
        _require("derived_profile_limits" in results,f"{name}: missing derived profile limits",errors)
    elif name in ("mismatch","distribution-shift"):
        summary=results.get("summary",{}); _require(bool(summary),f"{name}: empty mismatch summary",errors)
        if name=="distribution-shift":
            for family in ("NOMINAL_GAUSSIAN","HEAVY_TAILED_T3","CORRELATED_SNR_INTERFERENCE","BIASED_STATE_ESTIMATE"):
                _require(family in summary,f"{name}: missing family {family}",errors)
                if family in summary:
                    for policy in ("B3_DETERMINISTIC_JOINT","B4_ROBUST_JOINT"):
                        _require(policy in summary[family],f"{name}: missing {policy} in {family}",errors)
    elif name=="runtime":
        summary=results.get("summary",{}); _require(bool(summary),f"{name}: empty runtime summary",errors)
        for draws,policies in summary.items():
            if "B4_ROBUST_JOINT" in policies:
                b4=policies["B4_ROBUST_JOINT"]
                for key in ("median_us","p95_us","p99_us"): _require(b4.get(key,0)>0,f"{name}: invalid B4 {key} at draws={draws}",errors)
    elif name=="confidence-maps": _require(bool(results),f"{name}: empty confidence maps",errors)
    elif name in ("uncertainty","stress","ablations","reliability-targets","uncertainty-sources"): _require(bool(results),f"{name}: empty results",errors)
    elif name=="pareto": _require("physical_points" in results,f"{name}: missing physical_points",errors)
    return errors


def run_gate(root: Path) -> dict:
    report={"input_dir":str(root),"artifacts":{},"errors":[]}
    for name in REQUIRED:
        path=root/f"{name}.json"
        if not path.exists():
            report["errors"].append(f"{name}: missing artifact {path}"); report["artifacts"][name]={"status":"MISSING"}; continue
        try: payload=json.loads(path.read_text())
        except Exception as exc:
            report["errors"].append(f"{name}: unreadable JSON: {exc}"); report["artifacts"][name]={"status":"INVALID_JSON"}; continue
        errors=validate_artifact(name,payload); report["artifacts"][name]={"status":"PASS" if not errors else "FAIL","errors":errors}; report["errors"].extend(errors)
    report["passed"]=not report["errors"]; return report


def main() -> None:
    args=parse_args(); report=run_gate(Path(args.input_dir)); text=json.dumps(report,indent=2,allow_nan=False)
    if args.output:
        out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(text)
    print(text); raise SystemExit(0 if report["passed"] else 2)


if __name__=="__main__": main()
