#!/usr/bin/env python3
"""Aggregate per-checkpoint Stage-04 summaries into the learned-objective ablation table."""
from __future__ import annotations
import argparse,csv,json
from collections import defaultdict
from pathlib import Path
import numpy as np

OBJECTIVES=("trajectory","trajectory_plus_link","trajectory_plus_outage","full_communication_aware")
METRICS=("ade_m","fde_m","range_mae_m","bearing_mae_rad","snr_mae_db","goodput_mae_bps","outage_f1","link_lifetime_abs_error_s","nll","coverage_50","coverage_90","coverage_95")

def main():
 p=argparse.ArgumentParser(); p.add_argument("summaries",type=Path,nargs="+"); p.add_argument("--split",choices=["development","official_validation"],required=True); p.add_argument("--seeds",default="11,22,33,44,55"); p.add_argument("--output",type=Path,required=True); p.add_argument("--manifest",type=Path,required=True); a=p.parse_args(); seeds=[int(x) for x in a.seeds.split(",")]
 records=[]; errors=[]
 for path in a.summaries:
  d=json.loads(path.read_text())
  if d.get("split")!=a.split: errors.append(f"split mismatch: {path}"); continue
  if d.get("objective") not in OBJECTIVES: errors.append(f"unknown objective: {path}"); continue
  if int(d.get("seed")) not in seeds: errors.append(f"unexpected seed: {path}"); continue
  records.append((path,d))
 seen={(d["objective"],int(d["seed"])) for _,d in records}; expected={(o,s) for o in OBJECTIVES for s in seeds}
 missing=sorted(expected-seen); duplicate=len(seen)!=len(records)
 if missing: errors.append(f"missing objective/seed summaries: {missing}")
 if duplicate: errors.append("duplicate objective/seed summaries")
 dataset_hashes={d.get("dataset_sha256") for _,d in records}; link_hashes={d.get("link_model_sha256") for _,d in records}; lut_hashes={d.get("ber_lut_sha256") for _,d in records}
 if len(dataset_hashes)!=1: errors.append("dataset SHA differs across summaries")
 if len(link_hashes-{None})>1: errors.append("link-model SHA differs across summaries")
 if len(lut_hashes-{None})>1: errors.append("BER-LUT SHA differs across summaries")
 rows=[]
 for obj in OBJECTIVES:
  group=[d for _,d in records if d["objective"]==obj]; row={"objective":obj,"seed_count":len(group)}
  for m in METRICS:
   vals=[float(d[m]) for d in group if d.get(m) is not None]
   if vals:
    row[m+"__mean"]=float(np.mean(vals)); row[m+"__std"]=float(np.std(vals,ddof=1)) if len(vals)>1 else 0.0
  rows.append(row)
 a.output.parent.mkdir(parents=True,exist_ok=True); fields=sorted(set().union(*(r.keys() for r in rows)))
 with a.output.open("w",newline="") as f: w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
 manifest={"schema":"stage04_ablation_aggregate_v1","passed":not errors,"split":a.split,"paired_seeds":seeds,"expected_runs":20,"observed_runs":len(records),"dataset_sha256":next(iter(dataset_hashes)) if len(dataset_hashes)==1 else None,"link_model_sha256":next(iter(link_hashes)) if len(link_hashes)==1 else None,"ber_lut_sha256":next(iter(lut_hashes)) if len(lut_hashes)==1 else None,"aggregation":"mean/std across paired seeds of scenario-aggregated checkpoint summaries","errors":errors}
 a.manifest.parent.mkdir(parents=True,exist_ok=True); a.manifest.write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n"); print(json.dumps(manifest,indent=2)); return 0 if manifest["passed"] else 2
if __name__=="__main__": raise SystemExit(main())
