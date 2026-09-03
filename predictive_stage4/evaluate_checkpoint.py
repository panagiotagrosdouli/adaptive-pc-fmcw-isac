#!/usr/bin/env python3
"""Evaluate one learned checkpoint on trajectory, calibration and frozen-link fidelity."""
from __future__ import annotations
import argparse,csv,hashlib,importlib.util,json,sys
from collections import defaultdict
from pathlib import Path
import numpy as np,torch
HERE=Path(__file__).resolve().parent
def load_path(path,name):
 s=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(s); assert s.loader; sys.modules[s.name]=m; s.loader.exec_module(m); return m
modelm=load_path(HERE/"model.py","predictive_stage4_model"); cal=load_path(HERE/"calibration.py","predictive_stage4_calibration"); lm=load_path(HERE.parent/"predictive_stage2"/"link_model.py","predictive_stage2_link_model")
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def predict(ckpt,npz,split,batch=1024):
 d=torch.load(ckpt,map_location="cpu",weights_only=False)
 if d.get("normalization",{}).get("source_split")!="training": raise RuntimeError("checkpoint normalization must be fitted on training only")
 if d.get("official_validation_used_for_selection") is not False: raise RuntimeError("checkpoint metadata does not prove held-out-safe selection")
 if d.get("selection_split")!="development": raise RuntimeError("checkpoint selection_split must be development")
 net=modelm.CommunicationAwareGRU(**d["architecture"]); net.load_state_dict(d["state_dict"]); net.eval(); norm=d["normalization"]
 with np.load(npz,allow_pickle=False) as z:
  m=np.asarray(z["split"]).astype(str)==split; x=np.concatenate([z["history_xy"][m],z["history_vxy"][m]],axis=-1).astype(np.float32); y=np.asarray(z["future_xy"])[m].astype(np.float32); sid=np.asarray(z["scenario_id"])[m].astype(str); sdc=np.asarray(z["sdc_future_xy"])[m].astype(np.float32) if "sdc_future_xy" in z.files else None; rel=np.asarray(z["future_relative_xy"])[m].astype(np.float32) if "future_relative_xy" in z.files else None
 if not len(y): raise RuntimeError(f"no samples for split {split}")
 x=(x-np.asarray(norm["mean"],np.float32))/np.asarray(norm["std"],np.float32); out=[]
 with torch.no_grad():
  for i in range(0,len(x),batch): out.append(net(torch.from_numpy(x[i:i+batch])).numpy())
 return np.concatenate(out),y,sid,sdc,rel,d
def link_metrics(model,pred_rel,true_rel,dt=.1):
 def rb(x): return np.linalg.norm(x,axis=-1),np.arctan2(x[:,1],x[:,0])
 rp,bp=rb(pred_rel); rt,bt=rb(true_rel); ps=[model.evaluate(range_m=max(float(r),1e-3),pointing_error_rad=float(abs(b))) for r,b in zip(rp,bp)]; ts=[model.evaluate(range_m=max(float(r),1e-3),pointing_error_rad=float(abs(b))) for r,b in zip(rt,bt)]
 sp=np.array([x.snr_db for x in ps]); st=np.array([x.snr_db for x in ts]); gp=np.array([x.goodput_bps for x in ps]); gt=np.array([x.goodput_bps for x in ts]); op=np.array([x.outage for x in ps]); ot=np.array([x.outage for x in ts]); joint=np.isfinite(sp)&np.isfinite(st)
 life=lambda o: float((np.flatnonzero(o)[0] if np.any(o) else len(o))*dt); tp=np.sum(op&ot); fp=np.sum(op&~ot); fn=np.sum(~op&ot); den=2*tp+fp+fn
 ang=np.abs(np.arctan2(np.sin(bp-bt),np.cos(bp-bt)))
 return {"range_mae_m":float(np.mean(abs(rp-rt))),"bearing_mae_rad":float(np.mean(ang)),"snr_mae_db":float(np.mean(abs(sp[joint]-st[joint]))) if joint.any() else None,"snr_joint_in_fov_steps":int(joint.sum()),"goodput_mae_bps":float(np.mean(abs(gp-gt))),"outage_f1":float(2*tp/den) if den else 1.,"link_lifetime_abs_error_s":abs(life(op)-life(ot))}
def main():
 p=argparse.ArgumentParser(); p.add_argument("npz",type=Path); p.add_argument("checkpoint",type=Path); p.add_argument("--split",choices=["development","official_validation"],required=True); p.add_argument("--output",type=Path,required=True); p.add_argument("--summary",type=Path,required=True); p.add_argument("--fit-calibration",type=Path); p.add_argument("--calibration",type=Path); p.add_argument("--link-config",type=Path); p.add_argument("--ber-lut",type=Path); a=p.parse_args()
 if a.fit_calibration and a.calibration: p.error("choose fit or apply calibration, not both")
 if a.fit_calibration and a.split!="development": p.error("calibration fitting is development-only")
 if bool(a.link_config)!=bool(a.ber_lut): p.error("--link-config and --ber-lut must be supplied together")
 yh,y,sids,sdc,true_rel,meta=predict(a.checkpoint,a.npz,a.split); residual=yh-y; var=None; link=None; calibration_sha=None
 if a.link_config:
  if sdc is None or true_rel is None: raise RuntimeError("frozen-link evaluation requires sdc_future_xy and future_relative_xy")
  link=lm.LinkModel.from_dict(json.loads(a.link_config.read_text()),lm.BerLut.from_csv(a.ber_lut))
 if a.fit_calibration: var=cal.fit_isotropic_variance(residual); cal.save_calibration(a.fit_calibration,var,checkpoint_sha256=sha(a.checkpoint),development_dataset_sha256=sha(a.npz)); calibration_sha=sha(a.fit_calibration)
 if a.calibration:
  c=json.loads(a.calibration.read_text());
  if c.get("official_validation_used_for_fit") is not False or c.get("fit_split")!="development" or c.get("checkpoint_sha256")!=sha(a.checkpoint): raise RuntimeError("invalid calibration provenance")
  var=np.asarray(c["variance_xy_m2"],float); calibration_sha=sha(a.calibration)
 acc=defaultdict(list)
 for i,s in enumerate(sids):
  e=np.linalg.norm(residual[i],axis=-1); v={"ade_m":float(e.mean()),"fde_m":float(e[-1])}
  if var is not None: v["nll"]=cal.gaussian_nll(residual[i:i+1],var); v.update({f"coverage_{k}":x for k,x in cal.coverage(residual[i:i+1],var).items()})
  if link: v.update(link_metrics(link,yh[i]-sdc[i],true_rel[i]))
  acc[s].append(v)
 rows=[]
 for s,items in sorted(acc.items()):
  keys=set().union(*(x.keys() for x in items)); row={"scenario_id":s,"split":a.split,"actor_samples":len(items)}
  for k in keys:
   vals=[x[k] for x in items if x.get(k) is not None]; row[k]=float(np.sum(vals)) if k=="snr_joint_in_fov_steps" and vals else (float(np.mean(vals)) if vals else "")
  rows.append(row)
 a.output.parent.mkdir(parents=True,exist_ok=True); fields=sorted(set().union(*(r.keys() for r in rows)))
 with a.output.open("w",newline="") as f: w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
 metric_keys=sorted(set(rows[0])-{"scenario_id","split","actor_samples"}); summary={"schema":"stage04_learned_eval_v3","split":a.split,"scenario_count":len(rows),"sample_count":len(y),"checkpoint_sha256":sha(a.checkpoint),"dataset_sha256":sha(a.npz),"objective":meta["objective"],"seed":meta["seed"],"aggregation_unit":"scenario","link_model_sha256":sha(a.link_config) if link else None,"ber_lut_sha256":sha(a.ber_lut) if link else None,"calibration_sha256":calibration_sha}
 for k in metric_keys:
  vals=[r[k] for r in rows if r.get(k)!=""]; summary[k]=float(np.mean(vals)) if vals else None
 a.summary.parent.mkdir(parents=True,exist_ok=True); a.summary.write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n"); print(json.dumps(summary,indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
