#!/usr/bin/env python3
"""Run and record the Stage-04 communication-loss lambda sweep.

The sweep is development-only. It deliberately has no official-validation
argument. Selection is deterministic: minimum mean development objective,
then smaller lambdas as tie-breakers.
"""
from __future__ import annotations
import argparse,csv,json,subprocess,sys
from pathlib import Path
import torch

OBJECTIVES=("trajectory_plus_link","trajectory_plus_outage","full_communication_aware")

def grid(values): return [float(x) for x in values.split(",")]
def main():
 p=argparse.ArgumentParser(); p.add_argument("npz",type=Path); p.add_argument("--objective",choices=OBJECTIVES,required=True); p.add_argument("--lambda-link",default="0,0.01,0.03,0.1"); p.add_argument("--lambda-outage",default="0,0.01,0.03,0.1"); p.add_argument("--seeds",default="11,22,33,44,55"); p.add_argument("--epochs",type=int,default=50); p.add_argument("--workdir",type=Path,required=True); p.add_argument("--output",type=Path,required=True); p.add_argument("--selection",type=Path,required=True); a=p.parse_args()
 ll=grid(a.lambda_link) if a.objective!="trajectory_plus_outage" else [0.]; lo=grid(a.lambda_outage) if a.objective!="trajectory_plus_link" else [0.]; seeds=[int(x) for x in a.seeds.split(",")]
 rows=[]; a.workdir.mkdir(parents=True,exist_ok=True)
 for x in ll:
  for y in lo:
   vals=[]
   for seed in seeds:
    ck=a.workdir/f"{a.objective}__link{x:g}__out{y:g}__seed{seed}.pt"
    subprocess.run([sys.executable,str(Path(__file__).with_name("train.py")),str(a.npz),"--objective",a.objective,"--seed",str(seed),"--lambda-link",str(x),"--lambda-outage",str(y),"--epochs",str(a.epochs),"--output",str(ck)],check=True)
    vals.append(float(torch.load(ck,map_location="cpu",weights_only=False)["development_objective"]))
   rows.append({"objective":a.objective,"lambda_link":x,"lambda_outage":y,"seed_count":len(seeds),"mean_development_objective":sum(vals)/len(vals),"seed_values_json":json.dumps(vals)})
 a.output.parent.mkdir(parents=True,exist_ok=True)
 with a.output.open("w",newline="") as f: w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
 best=min(rows,key=lambda r:(r["mean_development_objective"],r["lambda_link"],r["lambda_outage"]))
 sel={"schema":"stage04_lambda_selection_v1","selection_split":"development","official_validation_used":False,"rule":"minimum mean development objective across paired seeds; smaller lambdas break exact ties","seeds":seeds,"selected":{k:best[k] for k in ("objective","lambda_link","lambda_outage","mean_development_objective")}}
 a.selection.parent.mkdir(parents=True,exist_ok=True); a.selection.write_text(json.dumps(sel,indent=2,sort_keys=True)+"\n"); print(json.dumps(sel,indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
