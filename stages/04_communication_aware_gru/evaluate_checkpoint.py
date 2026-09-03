#!/usr/bin/env python3
"""Evaluate a learned checkpoint; optionally fit/freeze or apply calibration."""
from __future__ import annotations
import argparse,csv,hashlib,importlib.util,json
from collections import defaultdict
from pathlib import Path
import numpy as np,torch
HERE=Path(__file__).resolve().parent
def load(name):
 s=importlib.util.spec_from_file_location(name,HERE/f"{name}.py"); m=importlib.util.module_from_spec(s); assert s.loader; s.loader.exec_module(m); return m
modelm,cal=load("model"),load("calibration")
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def predict(ckpt,npz,split,batch=1024):
 d=torch.load(ckpt,map_location="cpu",weights_only=False); net=modelm.CommunicationAwareGRU(**d["architecture"]); net.load_state_dict(d["state_dict"]); net.eval(); norm=d["normalization"]
 with np.load(npz,allow_pickle=False) as z:
  m=np.asarray(z["split"]).astype(str)==split; x=np.concatenate([z["history_xy"][m],z["history_vxy"][m]],axis=-1).astype(np.float32); y=np.asarray(z["future_xy"])[m].astype(np.float32); sid=np.asarray(z["scenario_id"])[m].astype(str)
 if not len(y): raise RuntimeError(f"no samples for split {split}")
 x=(x-np.asarray(norm["mean"],np.float32))/np.asarray(norm["std"],np.float32); out=[]
 with torch.no_grad():
  for i in range(0,len(x),batch): out.append(net(torch.from_numpy(x[i:i+batch])).numpy())
 return np.concatenate(out),y,sid,d
def main():
 p=argparse.ArgumentParser(); p.add_argument("npz",type=Path); p.add_argument("checkpoint",type=Path); p.add_argument("--split",choices=["development","official_validation"],required=True); p.add_argument("--output",type=Path,required=True); p.add_argument("--summary",type=Path,required=True); p.add_argument("--fit-calibration",type=Path); p.add_argument("--calibration",type=Path); a=p.parse_args()
 if a.fit_calibration and a.calibration: p.error("choose fit or apply calibration, not both")
 if a.fit_calibration and a.split!="development": p.error("calibration fitting is development-only")
 yh,y,sids,meta=predict(a.checkpoint,a.npz,a.split); residual=yh-y; var=None
 if a.fit_calibration:
  var=cal.fit_isotropic_variance(residual); cal.save_calibration(a.fit_calibration,var,checkpoint_sha256=sha(a.checkpoint),development_dataset_sha256=sha(a.npz))
 if a.calibration:
  c=json.loads(a.calibration.read_text())
  if c.get("official_validation_used_for_fit") is not False or c.get("fit_split")!="development": raise RuntimeError("invalid calibration provenance")
  if c.get("checkpoint_sha256")!=sha(a.checkpoint): raise RuntimeError("calibration belongs to a different checkpoint")
  var=np.asarray(c["variance_xy_m2"],float)
 acc=defaultdict(list)
 for i,s in enumerate(sids):
  e=np.linalg.norm(residual[i],axis=-1); acc[s].append((float(e.mean()),float(e[-1]),i))
 rows=[]
 for s,items in sorted(acc.items()):
  idx=[q[2] for q in items]; row={"scenario_id":s,"split":a.split,"actor_samples":len(idx),"ade_m":float(np.mean([q[0] for q in items])),"fde_m":float(np.mean([q[1] for q in items]))}
  if var is not None: row["nll"]=cal.gaussian_nll(residual[idx],var); row.update({f"coverage_{k}":v for k,v in cal.coverage(residual[idx],var).items()})
  rows.append(row)
 a.output.parent.mkdir(parents=True,exist_ok=True); fields=list(rows[0]);
 with a.output.open("w",newline="") as f: w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
 summary={"schema":"stage04_learned_eval_v1","split":a.split,"scenario_count":len(rows),"sample_count":len(y),"checkpoint_sha256":sha(a.checkpoint),"dataset_sha256":sha(a.npz),"objective":meta["objective"],"seed":meta["seed"],"ade_m":float(np.mean([r["ade_m"] for r in rows])),"fde_m":float(np.mean([r["fde_m"] for r in rows])),"aggregation_unit":"scenario"}
 if var is not None: summary["nll"]=float(np.mean([r["nll"] for r in rows])); summary.update({f"coverage_{k}":float(np.mean([r[f"coverage_{k}"] for r in rows])) for k in ("50","90","95")})
 a.summary.parent.mkdir(parents=True,exist_ok=True); a.summary.write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n"); print(json.dumps(summary,indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
