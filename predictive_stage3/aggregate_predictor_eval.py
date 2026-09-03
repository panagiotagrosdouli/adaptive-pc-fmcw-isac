#!/usr/bin/env python3
"""Aggregate per-scenario classical evaluation without hiding scenario-level rows."""
import argparse,csv,hashlib,json
from collections import defaultdict
from pathlib import Path
import numpy as np

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(); p.add_argument("csv",type=Path); p.add_argument("--output",type=Path,required=True); a=p.parse_args()
 with a.csv.open() as f: rows=list(csv.DictReader(f))
 if not rows: raise RuntimeError("empty evaluation CSV")
 numeric=[k for k in rows[0] if k not in {"scenario_id","predictor","split","actor_samples"}]
 by=defaultdict(list)
 for r in rows: by[r["predictor"]].append(r)
 out={"source":str(a.csv),"source_sha256":sha(a.csv),"aggregation_unit":"scenario","predictors":{}}
 for name,rs in sorted(by.items()):
  out["predictors"][name]={"scenario_count":len(rs),"metrics":{k:{"mean":float(np.mean([float(x[k]) for x in rs])),"median":float(np.median([float(x[k]) for x in rs]))} for k in numeric}}
 a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n"); print(json.dumps(out,indent=2,sort_keys=True)); return 0
if __name__=="__main__": raise SystemExit(main())
