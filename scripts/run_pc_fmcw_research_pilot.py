"""Versioned PC-FMCW receiver-level B3/B4 pilot (NOT publication-grade evidence).

Run: python scripts/run_pc_fmcw_research_pilot.py --cases-per-split 8 --draws 32
Independent scenario seeds are partitioned before evaluation. Calibration is
a conservative policy-level threshold on B3's estimated link-quality score;
held-out outcomes are obtained from actual comm and dechirped-IF receivers.
"""
from __future__ import annotations
import argparse
import json
import time
from pathlib import Path

import numpy as np
from pcfmcw_isac.publication_protocol import EvaluationState
from pcfmcw_isac.policy_v2_1 import select_action_v2_1
from pcfmcw_isac.policy_evaluation import evaluate_action
from pcfmcw_isac.research_gap_methods import calibrate_fixed_thresholds


def generate_states(seed: int, n: int):
    """Disjoint deterministic scenario seeds, distinct from frozen v2.1 seeds."""
    rng=np.random.default_rng(seed)
    return [
        EvaluationState(
            ebn0_db=float(rng.uniform(3, 18)),
            if_snr_db=float(rng.uniform(-5, 18)),
            range_m=float(rng.uniform(5, 45)),
            radial_velocity_mps=float(rng.uniform(-30, 30)),
            residual_cfo_hz=float(rng.uniform(0, 1000)),
            inr_db=None,
            phase_noise_std_rad_per_sample=0.001,
            state_uncertainty_scale=1.0,
            seed=seed * 100000 + i,
        ) for i in range(n)
    ]


def evaluate_split(states, *, draws=32, comm_bits=1000, sensing_trials=1):
    out=[]
    for state in states:
        record={"seed":state.seed}
        for label,policy in (("B3","B3_DETERMINISTIC_JOINT"),("B4","B4_ROBUST_JOINT")):
            start=time.perf_counter()
            action=select_action_v2_1(policy,state,robust_draws=draws)
            latency_ms=1000*(time.perf_counter()-start)
            successful=(evaluate_action(action,state,comm_bits=comm_bits,
                 sensing_trials=sensing_trials).joint_qos if action is not None else False)
            record[label]={"selected":action is not None,"joint_qos":bool(successful),
                           "selection_latency_ms":latency_ms}
        # A fixed, bounded score known before seeing the held-out outcome.
        record["score"]=float(np.clip((state.ebn0_db-3.0)/15.0,0.0,1.0))
        out.append(record)
    return out


def summarise(rows,label):
    selected=[r[label] for r in rows if r[label]["selected"]]
    return {"total_states":len(rows),"selected":len(selected),
       "selected_successes":sum(bool(r["joint_qos"]) for r in selected),
       "coverage":len(selected)/len(rows) if rows else None,
       "conditional_success":(sum(bool(r["joint_qos"]) for r in selected)/len(selected) if selected else None),
       "unconditional_success":sum(bool(r[label]["joint_qos"]) for r in rows)/len(rows) if rows else None,
       "median_selection_ms":float(np.median([r[label]["selection_latency_ms"] for r in rows])) if rows else None}


def run(seed=420, cases_per_split=8, draws=32, comm_bits=1000, sensing_trials=1):
    if cases_per_split<1 or draws<1:
        raise ValueError("cases_per_split and draws must be positive")
    cal=evaluate_split(generate_states(seed,cases_per_split),draws=draws,
       comm_bits=comm_bits,sensing_trials=sensing_trials)
    held=evaluate_split(generate_states(seed+1,cases_per_split),draws=draws,
       comm_bits=comm_bits,sensing_trials=sensing_trials)
    # Calibrate acceptance among states B3 would actually select; the threshold
    # is a post-filter; abstained states cannot be declared successful.
    scores=[r["score"] for r in cal if r["B3"]["selected"]]
    outcomes=[r["B3"]["joint_qos"] for r in cal if r["B3"]["selected"]]
    if scores:
        fit=calibrate_fixed_thresholds(scores,outcomes,
            thresholds=[0.0,0.25,0.5,0.75,1.0],risk_target=.05,
            alpha=.05,minimum_selected=1)
        threshold=fit.threshold
    else:
        threshold=None
    calibrated=[{"B3_CAL":{"selected":r["B3"]["selected"] and
       threshold is not None and r["score"]>=threshold,
       "joint_qos":r["B3"]["joint_qos"] and r["B3"]["selected"] and
       threshold is not None and r["score"]>=threshold,
       "selection_latency_ms":r["B3"]["selection_latency_ms"]}} for r in held]
    return {"evidence":"PC_FMCW_RECEIVER_PILOT_NOT_FINAL","seed":seed,
      "config":{"cases_per_split":cases_per_split,"robust_draws":draws,
                "comm_bits":comm_bits,"sensing_trials":sensing_trials},
      "calibration":{"policy":"B3","threshold":threshold,
                      "n_candidate_states":len(scores)},
      "held_out":{"B3":summarise(held,"B3"),"B4":summarise(held,"B4"),
                  "B3_CAL":summarise(calibrated,"B3_CAL")},
      "limitations":["Tiny split; not an independent research conclusion",
         "Score is a fixed illustrative link-quality proxy",
         "Hoeffding guarantee requires independent calibration units",
         "Runtime measured on unspecified host; not ECU",
         "B4 draws reduced for pilot; not frozen 512-draw benchmark"]}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--cases-per-split",type=int,default=8)
    p.add_argument("--draws",type=int,default=32)
    p.add_argument("--comm-bits",type=int,default=1000)
    p.add_argument("--output",default="artifacts/research_gaps/pc_fmcw_pilot.json")
    a=p.parse_args()
    data=run(cases_per_split=a.cases_per_split,draws=a.draws,comm_bits=a.comm_bits)
    dest=Path(a.output)
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(data,indent=2)+"\n")
    print(json.dumps(data,indent=2))

if __name__=="__main__":
    main()
