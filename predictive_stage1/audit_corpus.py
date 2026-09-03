#!/usr/bin/env python3
"""Audit the canonical WOMD predictive-connectivity NPZ contract."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import numpy as np
REQUIRED={"history_xy":(3,(11,2)),"history_vxy":(3,(11,2)),"future_xy":(3,(80,2)),"future_relative_xy":(3,(80,2)),"sdc_future_xy":(3,(80,2)),"history_valid":(2,(11,)),"future_valid":(2,(80,)),"scenario_id":(1,()),"track_id":(1,()),"sdc_track_id":(1,()),"split":(1,())}
NUMERIC_KEYS=("history_xy","history_vxy","future_xy","future_relative_xy","sdc_future_xy"); VALID_KEYS=("history_valid","future_valid")
def sha256(path):
 h=hashlib.sha256()
 with path.open("rb") as f:
  for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
 return h.hexdigest()
def strings(a): return {str(x) for x in a.tolist()}
def audit(path,expected_split=None):
 errors=[]
 with np.load(path,allow_pickle=False) as data:
  missing=sorted(set(REQUIRED)-set(data.files));
  if missing: errors.append(f"missing required arrays: {missing}")
  arrays={k:data[k] for k in REQUIRED if k in data}; ns={a.shape[0] for a in arrays.values() if a.ndim>=1}; n=next(iter(ns)) if len(ns)==1 else None
  if len(ns)!=1: errors.append(f"inconsistent sample dimension: {sorted(ns)}")
  for key,(ndim,tail) in REQUIRED.items():
   if key not in arrays: continue
   a=arrays[key]
   if a.ndim!=ndim: errors.append(f"{key}: expected ndim={ndim}, got {a.ndim}")
   elif tail and a.shape[1:]!=tail: errors.append(f"{key}: expected tail shape {tail}, got {a.shape[1:]}")
  for key in NUMERIC_KEYS:
   if key in arrays and not np.isfinite(arrays[key]).all(): errors.append(f"{key}: contains NaN or Inf")
  for key in VALID_KEYS:
   if key in arrays and not set(np.unique(arrays[key]).tolist()).issubset({0,1,False,True}): errors.append(f"{key}: validity mask is not boolean/0-1")
  # Identity: future_relative must exactly represent actor future minus true SDC future in the common anchor orientation.
  if all(k in arrays for k in ("future_xy","sdc_future_xy","future_relative_xy")) and not np.allclose(arrays["future_xy"]-arrays["sdc_future_xy"],arrays["future_relative_xy"],rtol=1e-5,atol=1e-4): errors.append("future_relative_xy violates actor_future - sdc_future geometry identity")
  sids=strings(arrays["scenario_id"]) if "scenario_id" in arrays else set(); splits=strings(arrays["split"]) if "split" in arrays else set()
  if not sids: errors.append("scenario_id is empty")
  if any(not x.strip() for x in sids): errors.append("scenario_id contains empty identity")
  if expected_split is not None and splits!={expected_split}: errors.append(f"expected split={expected_split!r}, observed={sorted(splits)}")
  return {"schema":"womd_predictive_connectivity_npz_v2","path":str(path),"sha256":sha256(path),"sample_count":n,"scenario_count":len(sids),"splits":sorted(splits),"arrays":{k:{"shape":list(v.shape),"dtype":str(v.dtype)} for k,v in arrays.items()},"true_sdc_future_geometry":not any("geometry identity" in e for e in errors) and all(k in arrays for k in ("future_relative_xy","sdc_future_xy")),"finite_numeric_arrays":not any("NaN or Inf" in e for e in errors),"passed":not errors,"errors":errors}
def main():
 p=argparse.ArgumentParser(); p.add_argument("npz",type=Path); p.add_argument("--expected-split"); p.add_argument("--output",type=Path,required=True); a=p.parse_args(); r=audit(a.npz,a.expected_split); a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n"); print(json.dumps(r,indent=2,sort_keys=True)); return 0 if r["passed"] else 2
if __name__=="__main__": raise SystemExit(main())
