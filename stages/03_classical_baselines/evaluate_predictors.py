#!/usr/bin/env python3
"""Evaluate causal forecasts; communication metrics use true future SDC motion."""
from __future__ import annotations
import argparse,csv,importlib.util,json
from collections import defaultdict
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
def load(path,name):
 s=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(s); assert s.loader; s.loader.exec_module(m); return m
pred=load(HERE/"predictors.py","predictors"); imm=load(HERE/"imm.py","imm"); PREDICTORS={"last":pred.LastPosition,"cv":pred.ConstantVelocity,"ca":pred.ConstantAcceleration,"kalman":pred.LinearKalmanCV,"imm":imm.IMM}
def trajectory_metrics(yh,y): e=np.linalg.norm(yh-y,axis=-1); return float(e.mean()),float(e[-1])
def range_bearing(xy): return np.linalg.norm(xy,axis=-1),np.arctan2(xy[...,1],xy[...,0])
def angular_error(a,b): return np.abs(np.arctan2(np.sin(a-b),np.cos(a-b)))
def binary_auroc(labels,scores):
 labels=np.asarray(labels,bool); scores=np.asarray(scores,float); pos=int(labels.sum()); neg=int((~labels).sum())
 if not pos or not neg: return None
 order=np.argsort(scores,kind="stable"); ranks=np.empty(len(scores),float); i=0
 while i<len(order):
  j=i+1
  while j<len(order) and scores[order[j]]==scores[order[i]]: j+=1
  ranks[order[i:j]]=(i+j+1)/2.; i=j
 return float((ranks[labels].sum()-pos*(pos+1)/2)/(pos*neg))
def load_link_model(config,lut):
 m=load(HERE.parent/"02_pc_fmcw_dpsk_link"/"link_model.py","link_model"); return m.LinkModel.from_dict(json.loads(config.read_text()),m.BerLut.from_csv(lut))
def link_metrics(model,pred_relative,true_relative,dt=.1):
 rp,bp=range_bearing(pred_relative); rt,bt=range_bearing(true_relative); ps=[model.evaluate(range_m=max(float(r),1e-3),pointing_error_rad=float(abs(b))) for r,b in zip(rp,bp)]; ts=[model.evaluate(range_m=max(float(r),1e-3),pointing_error_rad=float(abs(b))) for r,b in zip(rt,bt)]
 snrp=np.array([s.snr_db for s in ps]); snrt=np.array([s.snr_db for s in ts]); gp=np.array([s.goodput_bps for s in ps]); gt=np.array([s.goodput_bps for s in ts]); op=np.array([s.outage for s in ps],bool); ot=np.array([s.outage for s in ts],bool); outage_score=np.array([s.per for s in ps])
 # SNR is undefined outside FoV (-inf); score SNR fidelity only where both links are in FoV.
 joint=np.isfinite(snrp)&np.isfinite(snrt); snr_mae=float(np.mean(np.abs(snrp[joint]-snrt[joint]))) if joint.any() else None
 def life(o): i=np.flatnonzero(o); return float((i[0] if len(i) else len(o))*dt)
 tp=int(np.sum(op&ot)); fp=int(np.sum(op&~ot)); fn=int(np.sum(~op&ot)); f1=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 1.
 return {"range_mae_m":float(np.mean(abs(rp-rt))),"bearing_mae_rad":float(np.mean(angular_error(bp,bt))),"snr_mae_db":snr_mae,"snr_joint_in_fov_steps":int(joint.sum()),"goodput_mae_bps":float(np.mean(abs(gp-gt))),"outage_f1":float(f1),"outage_auroc":binary_auroc(ot,outage_score),"outage_auroc_support":int(len(ot)) if np.any(ot) and np.any(~ot) else 0,"link_lifetime_abs_error_s":abs(life(op)-life(ot))}
def main():
 p=argparse.ArgumentParser(); p.add_argument("npz",type=Path); p.add_argument("--split",default="development"); p.add_argument("--predictors",nargs="+",default=list(PREDICTORS),choices=PREDICTORS); p.add_argument("--link-config",type=Path); p.add_argument("--ber-lut",type=Path); p.add_argument("--output",type=Path,required=True); a=p.parse_args()
 if bool(a.link_config)!=bool(a.ber_lut): p.error("--link-config and --ber-lut must be supplied together")
 model=load_link_model(a.link_config,a.ber_lut) if a.link_config else None
 with np.load(a.npz,allow_pickle=False) as d:
  mask=np.asarray(d["split"]).astype(str)==a.split; H=np.asarray(d["history_xy"])[mask]; Y=np.asarray(d["future_xy"])[mask]; S=np.asarray(d["scenario_id"])[mask].astype(str)
  if model:
   for key in ("sdc_future_xy","future_relative_xy"):
    if key not in d.files: raise RuntimeError(f"link evaluation requires canonical {key}")
   SD=np.asarray(d["sdc_future_xy"])[mask]; REL=np.asarray(d["future_relative_xy"])[mask]
  else: SD=REL=[None]*len(S)
 if not len(S): raise RuntimeError(f"no samples for split {a.split}")
 acc=defaultdict(lambda:defaultdict(list))
 for h,y,sdc_f,true_rel,sid in zip(H,Y,SD,REL,S):
  for name in a.predictors:
   yh=PREDICTORS[name]().predict(h,len(y)).mean_xy; ade,fde=trajectory_metrics(yh,y); vals={"ade_m":ade,"fde_m":fde}
   if model: vals.update(link_metrics(model,yh-sdc_f,true_rel))
   for k,v in vals.items():
    if v is not None: acc[(sid,name)][k].append(v)
 rows=[]
 for (sid,name),metrics in sorted(acc.items()):
  row={"scenario_id":sid,"predictor":name,"split":a.split,"actor_samples":len(metrics["ade_m"])}; row.update({k:float(np.mean(v)) for k,v in metrics.items() if v}); rows.append(row)
 a.output.parent.mkdir(parents=True,exist_ok=True)
 fields=sorted(set().union(*(r.keys() for r in rows)))
 with a.output.open("w",newline="") as f: w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
 print(json.dumps({"rows":len(rows),"scenarios":len(set(S)),"split":a.split,"predictors":a.predictors,"link_metrics":model is not None,"true_sdc_future_geometry":bool(model),"snr_policy":"joint-in-FoV only"},indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
