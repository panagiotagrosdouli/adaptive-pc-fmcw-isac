"""Compute versioned Paper-1 coupled-IF support census; not a replacement for frozen evidence."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from pcfmcw_isac.coupled_if_research import (
    coupled_physics, nominal_complex_if, nominal_positive_if
)
from pcfmcw_isac.paper1_physics_gate_ablation import RANGE_GRID_M, VELOCITY_GRID_MPS
from pcfmcw_isac.policy_evaluation import profile_registry
from pcfmcw_isac.publication_protocol import EvaluationState, is_physics_feasible

def census(convention="complex",guard_fraction=0.0):
    if convention not in ("complex","positive"):
        raise ValueError("convention must be complex or positive")
    if not 0 <= guard_fraction < .5:
        raise ValueError("guard_fraction must lie in [0,0.5)")
    profiles=profile_registry()
    records=[]
    for r in RANGE_GRID_M:
        for v in VELOCITY_GRID_MPS:
            state=EvaluationState(12.,10.,r,v,0.,None,0.,0.,0)
            independent=any(is_physics_feasible(p,state) for p in profiles.values())
            supported={}
            for name,p in profiles.items():
                band=nominal_complex_if(p) if convention=="complex" else nominal_positive_if(p)
                band=type(band)(band.lower_hz,band.upper_hz,
                                 guard_fraction*p.sample_rate_hz)
                supported[name]=coupled_physics(p,r,v,passband=band).valid
            coupled=any(supported.values())
            records.append({"range_m":r,"radial_velocity_mps":v,
                 "old_supported":independent,"coupled_supported":coupled,
                 "coupled_profiles":supported})
    return {"evidence":"POST_FREEZE_ANALYTICAL_CENSUS_NOT_RECEIVER_VALIDATED",
      "convention":convention,"guard_fraction":guard_fraction,
      "n":len(records),
      "independent_supported":sum(x["old_supported"] for x in records),
      "coupled_supported":sum(x["coupled_supported"] for x in records),
      "old_accepts_coupled_rejects":[x for x in records if
                  x["old_supported"] and not x["coupled_supported"]],
      "old_rejects_coupled_accepts":[x for x in records if
                  not x["old_supported"] and x["coupled_supported"]]}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--convention",choices=["complex","positive"],default="complex")
    p.add_argument("--guard-fraction",type=float,default=0.)
    p.add_argument("--output",default="artifacts/research_gaps/coupled_if_census.json")
    a=p.parse_args()
    data=census(a.convention,a.guard_fraction)
    path=Path(a.output)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2)+"\n")
    print(json.dumps(data,indent=2))

if __name__=="__main__":
    main()
