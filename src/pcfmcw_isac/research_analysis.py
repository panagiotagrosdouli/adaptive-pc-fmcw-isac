"""Machine-readable statistical, failure, physics and Pareto analysis."""
from __future__ import annotations

from collections import Counter
from typing import Iterable

import numpy as np


def paired_bootstrap_binary_difference(
    records: list[dict], *, policy_a: str, policy_b: str,
    group_field: str | None = None, group_value: object | None = None,
    metric: str = "joint_qos", key_fields: tuple[str, ...] = ("seed", "scenario_id", "truth_draw"),
    confidence: float = 0.95, n_resamples: int = 10_000, seed: int = 20260912,
) -> dict:
    """Paired bootstrap of A-B over declared independent episode units."""
    if not 0.0 < confidence < 1.0: raise ValueError("confidence must be in (0,1)")
    if n_resamples <= 0: raise ValueError("n_resamples must be positive")
    rows = records if group_field is None else [r for r in records if r.get(group_field) == group_value]
    def key(row: dict) -> tuple:
        try: return tuple(row[field] for field in key_fields)
        except KeyError as exc: raise ValueError(f"missing paired key field {exc.args[0]!r}") from exc
    a = {key(r): float(bool(r.get(metric, False))) for r in rows if r.get("policy") == policy_a}
    b = {key(r): float(bool(r.get(metric, False))) for r in rows if r.get("policy") == policy_b}
    common = sorted(set(a) & set(b))
    if not common: raise ValueError("no paired observations")
    if len(common) != len(a) or len(common) != len(b): raise ValueError("unpaired observations detected")
    diffs = np.asarray([a[k] - b[k] for k in common], dtype=float)
    rng = np.random.default_rng(seed); boot_means=[]; remaining=n_resamples; chunk=max(1,min(1000,n_resamples))
    while remaining:
        take=min(chunk,remaining); idx=rng.integers(0,diffs.size,size=(take,diffs.size)); boot_means.append(np.mean(diffs[idx],axis=1)); remaining-=take
    boots=np.concatenate(boot_means); alpha=1.0-confidence; lo,hi=np.quantile(boots,[alpha/2.0,1.0-alpha/2.0])
    return {"policy_a":policy_a,"policy_b":policy_b,"metric":metric,"paired_units":len(common),
            "mean_difference_a_minus_b":float(np.mean(diffs)),"confidence":confidence,"bootstrap_resamples":n_resamples,
            "ci_low":float(lo),"ci_high":float(hi),"wins_a":int(np.sum(diffs>0)),"ties":int(np.sum(diffs==0)),"wins_b":int(np.sum(diffs<0))}


def distribution_shift_statistics(result: dict, *, n_resamples: int = 10_000, confidence: float = 0.95) -> dict:
    records=result.get("records",[]); families=sorted({r.get("family") for r in records if r.get("family") is not None})
    return {family: paired_bootstrap_binary_difference(records,policy_a="B4_ROBUST_JOINT",policy_b="B3_DETERMINISTIC_JOINT",
            group_field="family",group_value=family,n_resamples=n_resamples,confidence=confidence,seed=20260912+i)
            for i,family in enumerate(families)}


def _failure_reason(row: dict) -> str:
    if row.get("state_category") == "PHYSICALLY_INFEASIBLE": return "PHYSICAL_INFEASIBILITY"
    if row.get("selected_action") is None: return "POLICY_ABSTENTION"
    if not row.get("physics_feasible", True): return "SELECTED_ACTION_PHYSICS_FAILURE"
    if row.get("joint_qos", False): return "SUCCESS"
    failures=[]; ber=row.get("ber"); rate=row.get("effective_rate_bps"); rr=row.get("range_rmse_m"); vr=row.get("velocity_rmse_mps")
    if ber is not None and ber > 1e-3: failures.append("COMM_BER")
    if rate is not None and rate < 1e5: failures.append("COMM_RATE")
    if rr is not None and rr > 1.0: failures.append("RANGE_RMSE")
    if vr is not None and vr > 1.0: failures.append("VELOCITY_RMSE")
    return "+".join(failures) if failures else "UNCLASSIFIED_QOS_FAILURE"


def failure_taxonomy(records: Iterable[dict], *, group_fields: tuple[str, ...] = ("policy",)) -> dict:
    rows=list(records); global_counts=Counter(_failure_reason(r) for r in rows); groups:dict[str,Counter]={}
    for row in rows:
        key="|".join(f"{field}={row.get(field)}" for field in group_fields); groups.setdefault(key,Counter())[_failure_reason(row)]+=1
    return {"n":len(rows),"global":dict(sorted(global_counts.items())),"groups":{k:dict(sorted(v.items())) for k,v in sorted(groups.items())}}


def enrich_distribution_shift(result: dict, *, n_resamples: int = 10_000) -> dict:
    enriched=dict(result); enriched["paired_statistics"]=distribution_shift_statistics(result,n_resamples=n_resamples); enriched["failure_taxonomy"]=failure_taxonomy(result.get("records",[]),group_fields=("family","policy")); return enriched


def enrich_physics_map(result: dict) -> dict:
    """Attach per-profile machine-readable rejection reasons to existing map cells."""
    limits=result.get("derived_profile_limits",{}); enriched=dict(result); cells=[]
    for cell in result.get("cells",[]):
        new_cell=dict(cell); reasons={}
        r=float(cell["range_m"]); v=float(cell["radial_velocity_mps"])
        for profile,supported in cell.get("profiles",{}).items():
            profile_limits=limits.get(profile,{})
            codes=[]
            if r < 0.0: codes.append("NEGATIVE_RANGE")
            elif "positive_if_max_range_m" in profile_limits and r > float(profile_limits["positive_if_max_range_m"]): codes.append("RANGE_UNSUPPORTED")
            if "max_unambiguous_velocity_mps" in profile_limits and abs(v) > float(profile_limits["max_unambiguous_velocity_mps"]): codes.append("VELOCITY_AMBIGUOUS")
            if bool(supported) != (not codes): codes.append("MAP_CONSISTENCY_ERROR")
            reasons[profile]={"feasible":bool(supported),"reasons":codes}
        new_cell["profile_feasibility"] = reasons; cells.append(new_cell)
    enriched["cells"]=cells
    return enriched


PARETO_OBJECTIVES = {
    "joint_qos_probability": "maximize",
    "mean_effective_rate_bps": "maximize",
    "tx_power_fraction": "minimize",
    "repetition_factor": "minimize",
    "chips_per_chirp": "minimize",
    "profile_adc_samples_per_frame": "minimize",
    "mean_range_rmse_m": "minimize",
    "mean_velocity_rmse_mps": "minimize",
}


def _finite_objective(point: dict, key: str) -> float:
    value = point.get(key)
    if value is None or not np.isfinite(float(value)):
        raise ValueError(f"Pareto point has missing/non-finite objective {key!r}")
    return float(value)


def _dominates(a: dict, b: dict) -> bool:
    """True iff a is no worse in every declared objective and better in >=1."""
    no_worse = True
    strictly_better = False
    for key, direction in PARETO_OBJECTIVES.items():
        av = _finite_objective(a, key); bv = _finite_objective(b, key)
        if direction == "maximize":
            if av < bv: no_worse = False; break
            if av > bv: strictly_better = True
        else:
            if av > bv: no_worse = False; break
            if av < bv: strictly_better = True
    return no_worse and strictly_better


def pareto_partition(points: Iterable[dict]) -> dict:
    """Partition empirical operating points into non-dominated and dominated sets."""
    rows=[dict(p) for p in points]
    dominated=[]; frontier=[]
    for i, point in enumerate(rows):
        dominators=[j for j, other in enumerate(rows) if j != i and _dominates(other, point)]
        annotated={**point,"point_index":i,"dominated_by_indices":dominators}
        (dominated if dominators else frontier).append(annotated)
    return {
        "objective_directions": dict(PARETO_OBJECTIVES),
        "n_points": len(rows),
        "n_non_dominated": len(frontier),
        "n_dominated": len(dominated),
        "non_dominated_points": frontier,
        "dominated_points": dominated,
    }


def enrich_pareto(result: dict) -> dict:
    """Attach an explicit empirical non-dominance partition to Pareto evidence."""
    enriched=dict(result)
    partition=pareto_partition(result.get("physical_points",[]))
    enriched["pareto"] = partition
    enriched["claim_boundary"] = (
        "Empirical Pareto partition over realized B4-selected receiver-level operating points only; "
        "it is not a proof that unselected action configurations are globally dominated."
    )
    return enriched
