"""Versioned diagnostic benchmark for B/C building blocks.

This experiment uses synthetic independent Bernoulli outcomes as a methodological
smoke test. It does NOT demonstrate PC-FMCW performance.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
from pcfmcw_isac.research_gap_methods import calibrate_fixed_thresholds, anytime_bernoulli_decision

def run(seed: int = 20261014, n_cal: int = 10000, n_test: int = 10000, n_cases: int = 400):
    rng = np.random.default_rng(seed)
    # Score is fixed prior to calibration. The synthetic data-generating law is
    # intentionally simple so this checks wiring, NOT domain validity.
    cal_score = rng.uniform(size=n_cal)
    cal_success = rng.random(n_cal) < (0.85 + 0.149 * cal_score)
    test_score = rng.uniform(size=n_test)
    test_success = rng.random(n_test) < (0.85 + 0.149 * test_score)
    grid = [round(i / 20, 2) for i in range(21)]
    fit = calibrate_fixed_thresholds(cal_score.tolist(), cal_success.tolist(),
        thresholds=grid, alpha=0.05, risk_target=0.05, minimum_selected=100)
    chosen = fit.threshold
    held = [bool(y) for s,y in zip(test_score,test_success) if chosen is not None and s >= chosen]
    test_summary = {"selected":len(held),"failures":len(held)-sum(held),
                    "empirical_risk":((len(held)-sum(held))/len(held) if held else None)}
    sequential = []
    for _ in range(n_cases):
        true_p = rng.uniform(.60,.999)
        outcomes = rng.random(512) < true_p
        result = anytime_bernoulli_decision(outcomes.tolist(), target=.95, alpha=.05)
        sequential.append({"draws":result.draws,"accepted":result.accepted,
            "rejected":result.rejected,"true_p":float(true_p)})
    return {"evidence":"SYNTHETIC_SMOKE_NOT_PC_FMCW","seed":seed,
       "calibration":{"n":n_cal,"threshold":chosen,"selected":fit.selected,
           "failures":fit.failures,"upper_bound":fit.upper_failure_bound},
       "held_out":{"n":n_test,**test_summary},
       "sequential":{"cases":n_cases,
           "mean_draws":float(np.mean([x["draws"] for x in sequential])),
           "early_rejections":sum(x["rejected"] for x in sequential),
           "early_acceptances":sum(x["accepted"] for x in sequential),
           "max_draws":512}}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output",default="artifacts/research_gaps/synthetic_smoke.json")
    args = parser.parse_args()
    result = run()
    output=Path(args.output)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))

if __name__=="__main__":
    main()
