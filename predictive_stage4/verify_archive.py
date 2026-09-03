#!/usr/bin/env python3
"""Verify the publication checkpoint archive: exactly four objectives x five seeds."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import torch
OBJECTIVES=("trajectory","trajectory_plus_link","trajectory_plus_outage","full_communication_aware")
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(); p.add_argument("archive",type=Path); p.add_argument("--seeds",default="11,22,33,44,55"); p.add_argument("--output",type=Path,required=True); a=p.parse_args(); seeds=[int(x) for x in a.seeds.split(",")]; errors=[]; found={}; dataset_hashes=set(); architectures=set()
 for ck in sorted(a.archive.glob("*.pt")):
  d=torch.load(ck,map_location="cpu",weights_only=False); key=(d.get("objective"),d.get("seed"));
  if key in found: errors.append(f"duplicate objective/seed: {key}")
  found[key]=ck.name; dataset_hashes.add(d.get("dataset_sha256")); architectures.add(json.dumps(d.get("architecture"),sort_keys=True))
  if d.get("selection_split")!="development" or d.get("official_validation_used_for_selection") is not False: errors.append(f"selection leakage metadata: {ck.name}")
 expected={(o,s) for o in OBJECTIVES for s in seeds}; missing=sorted(expected-set(found)); extra=sorted(set(found)-expected)
 if missing: errors.append(f"missing checkpoints: {missing}")
 if extra: errors.append(f"unexpected checkpoints: {extra}")
 if len(found)!=20: errors.append(f"expected exactly 20 objective/seed checkpoints, got {len(found)}")
 if len(dataset_hashes)!=1: errors.append(f"dataset hashes differ: {sorted(map(str,dataset_hashes))}")
 if len(architectures)!=1: errors.append("architectures differ across objective ablations")
 files=[{"objective":o,"seed":s,"file":found[(o,s)]} for o,s in sorted(found,key=lambda x:(str(x[0]),str(x[1])))]
 report={"schema":"stage04_checkpoint_archive_v1","passed":not errors,"expected_objectives":list(OBJECTIVES),"expected_seeds":seeds,"checkpoint_count":len(found),"dataset_sha256":next(iter(dataset_hashes)) if len(dataset_hashes)==1 else None,"files":files,"errors":errors}
 a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n"); print(json.dumps(report,indent=2,sort_keys=True)); return 0 if report["passed"] else 2
if __name__=="__main__": raise SystemExit(main())
