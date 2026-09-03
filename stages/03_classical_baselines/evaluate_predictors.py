#!/usr/bin/env python3
"""Evaluate causal classical forecasts on canonical WOMD NPZ, per scenario.

Trajectory metrics are computed directly. Optional link metrics are computed by
passing predicted and realized SDC-relative geometry through the frozen Stage-02
link model. This script never tunes on official_validation.
"""
from __future__ import annotations

import argparse, csv, importlib.util, json
from collections import defaultdict
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
pspec=importlib.util.spec_from_file_location("predictors", HERE/"predictors.py")
pred=importlib.util.module_from_spec(pspec); assert pspec.loader; pspec.loader.exec_module(pred)

PREDICTORS={"last":pred.LastPosition,"cv":pred.ConstantVelocity,"ca":pred.ConstantAcceleration,"kalman":pred.LinearKalmanCV}


def trajectory_metrics(yhat,y):
    e=np.linalg.norm(yhat-y,axis=-1)
    return float(e.mean()),float(e[-1])


def range_bearing(xy):
    r=np.linalg.norm(xy,axis=-1)
    b=np.arctan2(xy[...,1],xy[...,0])
    return r,b


def angular_error(a,b):
    return np.abs(np.arctan2(np.sin(a-b),np.cos(a-b)))


def load_link_model(config,lut):
    lpath=HERE.parent/"02_pc_fmcw_dpsk_link"/"link_model.py"
    spec=importlib.util.spec_from_file_location("link_model",lpath)
    m=importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(m)
    cfg=json.loads(config.read_text())
    return m.LinkModel.from_dict(cfg,m.BerLut.from_csv(lut))


def link_metrics(model,yhat,y,dt=0.1):
    rp,bp=range_bearing(yhat); rt,bt=range_bearing(y)
    pred_states=[model.evaluate(range_m=float(r),pointing_error_rad=float(abs(b))) for r,b in zip(rp,bp)]
    true_states=[model.evaluate(range_m=float(r),pointing_error_rad=float(abs(b))) for r,b in zip(rt,bt)]
    snrp=np.array([s.snr_db for s in pred_states]); snrt=np.array([s.snr_db for s in true_states])
    gp=np.array([s.goodput_bps for s in pred_states]); gt=np.array([s.goodput_bps for s in true_states])
    op=np.array([s.outage for s in pred_states],bool); ot=np.array([s.outage for s in true_states],bool)
    def lifetime(o):
        idx=np.flatnonzero(o); return float((idx[0]+1)*dt) if len(idx) else float(len(o)*dt)
    tp=int(np.sum(op & ot)); fp=int(np.sum(op & ~ot)); fn=int(np.sum(~op & ot))
    f1=2*tp/(2*tp+fp+fn) if (2*tp+fp+fn) else 1.0
    return {
      "range_mae_m":float(np.mean(np.abs(rp-rt))),"bearing_mae_rad":float(np.mean(angular_error(bp,bt))),
      "snr_mae_db":float(np.mean(np.abs(snrp-snrt))),"goodput_mae_bps":float(np.mean(np.abs(gp-gt))),
      "outage_f1":float(f1),"link_lifetime_abs_error_s":abs(lifetime(op)-lifetime(ot)),
    }


def main():
    p=argparse.ArgumentParser(); p.add_argument("npz",type=Path); p.add_argument("--split",default="development")
    p.add_argument("--predictors",nargs="+",default=["last","cv","ca","kalman"],choices=PREDICTORS)
    p.add_argument("--link-config",type=Path); p.add_argument("--ber-lut",type=Path); p.add_argument("--output",type=Path,required=True)
    a=p.parse_args(); model=None
    if bool(a.link_config)!=bool(a.ber_lut): p.error("--link-config and --ber-lut must be supplied together")
    if a.link_config: model=load_link_model(a.link_config,a.ber_lut)
    with np.load(a.npz,allow_pickle=False) as d:
        mask=np.asarray(d["split"]).astype(str)==a.split
        H=np.asarray(d["history_xy"])[mask]; Y=np.asarray(d["future_xy"])[mask]; S=np.asarray(d["scenario_id"])[mask].astype(str)
    accum=defaultdict(lambda:defaultdict(list))
    for h,y,sid in zip(H,Y,S):
      for name in a.predictors:
        yhat=PREDICTORS[name]().predict(h,len(y)).mean_xy; ade,fde=trajectory_metrics(yhat,y)
        vals={"ade_m":ade,"fde_m":fde}; vals.update(link_metrics(model,yhat,y) if model else {})
        for k,v in vals.items(): accum[(sid,name)][k].append(v)
    rows=[]
    for (sid,name),metrics in sorted(accum.items()):
        row={"scenario_id":sid,"predictor":name,"split":a.split,"actor_samples":len(metrics["ade_m"])}
        row.update({k:float(np.mean(v)) for k,v in metrics.items()}); rows.append(row)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print(json.dumps({"rows":len(rows),"scenarios":len(set(S)),"split":a.split,"link_metrics":model is not None},indent=2))
    return 0

if __name__=="__main__": raise SystemExit(main())
