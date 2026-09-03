#!/usr/bin/env python3
"""Run and record the Stage-04 communication-loss lambda sweep.

The sweep is development-only and has no official-validation argument.
Selection never compares the weighted training objective across different
lambda values. Instead it uses lambda-independent development metrics recorded
by each checkpoint.
"""
from __future__ import annotations
import argparse,csv,json,math,subprocess,sys
from pathlib import Path
import torch

OBJECTIVES=("trajectory_plus_link","trajectory_plus_outage","full_communication_aware")

def grid(values): return [float(x) for x in values.split(",")]
def mean(xs): return sum(xs)/len(xs)

def selection_score(objective,row,baseline):
 if objective=="trajectory_plus_link": return row["mean_development_link_loss"]
 if objective=="trajectory_plus_outage": return row["mean_development_outage_loss"]
 # Full objective: equal-weight geometric mean of three dimensionless ratios
 # relative to the zero-lambda development baseline. This score is independent
 # of the weighted optimization objective and is declared before held-out use.
 ratios=[]
 for key in ("mean_development_ade_m","mean_development_link_loss","mean_development_outage_loss"):
  den=max(float(baseline[key]),1e-12); ratios.append(max(float(row[key])/den,1e-12))
 return math.exp(sum(math.log(x) for x in ratios)/len(ratios))

def main():
 p=argparse.ArgumentParser(); p.add_argument("npz",type=Path); p.add_argument("--objective",choices=OBJECTIVES,required=True); p.add_argument("--lambda-link",default="0,0.01,0.03,0.1"); p.add_argument("--lambda-outage",default="0,0.01,0.03,0.1"); p.add_argument("--seeds",default="11,22,33,44,55"); p.add_argument("--epochs",type=int,default=50); p.add_argument("--link-config",type=Path,default=Path(__file__).resolve().parent.parent/"predictive_stage2"/"link_model_config.json"); p.add_argument("--workdir",type=Path,required=True); p.add_argument("--output",type=Path,required=True); p.add_argument("--selection",type=Path,required=True); a=p.parse_args()
 ll=grid(a.lambda_link) if a.objective!="trajectory_plus_outage" else [0.]; lo=grid(a.lambda_outage) if a.objective!="trajectory_plus_link" else [0.]; seeds=[int(x) for x in a.seeds.split(",")]
 rows=[]; a.workdir.mkdir(parents=True,exist_ok=True)
 for x in ll:
  for y in lo:
   metrics={"objective":[],"ade":[],"link":[],"outage":[]}
   for seed in seeds:
    ck=a.workdir/f"{a.objective}__link{x:g}__out{y:g}__seed{seed}.pt"
    subprocess.run([sys.executable,str(Path(__file__).with_name("train.py")),str(a.npz),"--objective",a.objective,"--seed",str(seed),"--lambda-link",str(x),"--lambda-outage",str(y),"--epochs",str(a.epochs),"--link-config",str(a.link_config),"--output",str(ck)],check=True)
    d=torch.load(ck,map_location="cpu",weights_only=False); metrics["objective"].append(float(d["development_objective"])); metrics["ade"].append(float(d["development_ade_m"])); metrics["link"].append(float(d["development_link_loss"])); metrics["outage"].append(float(d["development_outage_loss"]))
   rows.append({"objective":a.objective,"lambda_link":x,"lambda_outage":y,"seed_count":len(seeds),"mean_development_objective":mean(metrics["objective"]),"mean_development_ade_m":mean(metrics["ade"]),"mean_development_link_loss":mean(metrics["link"]),"mean_development_outage_loss":mean(metrics["outage"]),"seed_metrics_json":json.dumps(metrics,sort_keys=True)})
 baseline=next((r for r in rows if r["lambda_link"]==0. and r["lambda_outage"]==0.),None)
 if baseline is None: raise RuntimeError("lambda grid must contain zero-lambda development baseline")
 for r in rows: r["selection_score"]=selection_score(a.objective,r,baseline)
 a.output.parent.mkdir(parents=True,exist_ok=True)
 with a.output.open("w",newline="") as f: w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
 best=min(rows,key=lambda r:(r["selection_score"],r["lambda_link"],r["lambda_outage"]))
 rule=("minimum mean development link-fidelity loss" if a.objective=="trajectory_plus_link" else "minimum mean development outage-surrogate loss" if a.objective=="trajectory_plus_outage" else "minimum equal-weight geometric mean of development ADE/link/outage ratios relative to zero-lambda baseline")
 sel={"schema":"stage04_lambda_selection_v2","selection_split":"development","official_validation_used":False,"weighted_training_objective_used_for_cross_lambda_selection":False,"rule":rule,"tie_breaker":"smaller lambda_link then smaller lambda_outage","seeds":seeds,"baseline":{k:baseline[k] for k in ("lambda_link","lambda_outage","mean_development_ade_m","mean_development_link_loss","mean_development_outage_loss")},"selected":{k:best[k] for k in ("objective","lambda_link","lambda_outage","selection_score","mean_development_ade_m","mean_development_link_loss","mean_development_outage_loss")}}
 a.selection.parent.mkdir(parents=True,exist_ok=True); a.selection.write_text(json.dumps(sel,indent=2,sort_keys=True)+"\n"); print(json.dumps(sel,indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
