#!/usr/bin/env python3
"""Export WOMD into the canonical predictive-connectivity corpus.

Trajectory targets are expressed in the SDC pose at the prediction anchor.
Communication geometry is separately stored as actor-minus-SDC at each future
time, rotated by the anchor SDC heading. This distinction prevents the future
motion of the SDC from being silently treated as zero.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import numpy as np
HISTORY,FUTURE,CURRENT=11,80,10

def stable_dev(scenario_id,dev_fraction): return int(hashlib.sha256(scenario_id.encode()).hexdigest()[:16],16)/2**64<dev_fraction
def rotate(points,origin,yaw):
 d=points-origin; c,s=np.cos(yaw),np.sin(yaw); return np.stack((c*d[...,0]+s*d[...,1],-s*d[...,0]+c*d[...,1]),-1)
def state_xy(track):
 st=list(track.states); return np.asarray([[x.center_x,x.center_y] for x in st],np.float32),np.asarray([bool(x.valid) for x in st],bool)
def velocities(h,dt=.1):
 o=np.zeros_like(h); o[1:]=(h[1:]-h[:-1])/dt; o[0]=o[1]; return o

def export(files,output,fixed_split,dev_fraction,max_vehicles=None):
 import tensorflow as tf
 from waymo_open_dataset.protos import scenario_pb2
 keys=("history_xy","history_vxy","future_xy","future_relative_xy","sdc_future_xy","history_valid","future_valid","scenario_id","track_id","sdc_track_id","split")
 rows={k:[] for k in keys}; seen=set(); rejected={"short":0,"sdc_invalid":0,"sdc_future_invalid":0,"non_vehicle":0,"self_sdc":0,"invalid_window":0}
 for file in files:
  for raw in tf.data.TFRecordDataset(str(file)):
   sc=scenario_pb2.Scenario.FromString(bytes(raw.numpy())); sid=str(sc.scenario_id); seen.add(sid)
   if sc.current_time_index!=CURRENT: rejected["short"]+=1; continue
   tracks=list(sc.tracks)
   if not 0<=sc.sdc_track_index<len(tracks): rejected["sdc_invalid"]+=1; continue
   sdc=tracks[sc.sdc_track_index]; sxy,sv=state_xy(sdc)
   if len(sxy)<HISTORY+FUTURE or not sv[:HISTORY+FUTURE].all(): rejected["sdc_future_invalid"]+=1; continue
   anchor=sdc.states[CURRENT]; origin=np.asarray([anchor.center_x,anchor.center_y],np.float32); yaw=float(anchor.heading); sdc_id=int(sdc.id)
   sdc_future_anchor=rotate(sxy[HISTORY:HISTORY+FUTURE],origin,yaw).astype(np.float32)
   split=fixed_split or ("development" if stable_dev(sid,dev_fraction) else "training")
   candidates=[]
   for track in tracks:
    if int(track.object_type)!=1: rejected["non_vehicle"]+=1; continue
    if int(track.id)==sdc_id: rejected["self_sdc"]+=1; continue
    if len(track.states)<HISTORY+FUTURE: rejected["short"]+=1; continue
    xy,v=state_xy(track); hv=v[:HISTORY]; fv=v[HISTORY:HISTORY+FUTURE]
    if not hv.all() or not fv.all(): rejected["invalid_window"]+=1; continue
    h=rotate(xy[:HISTORY],origin,yaw).astype(np.float32); f=rotate(xy[HISTORY:HISTORY+FUTURE],origin,yaw).astype(np.float32)
    # Deterministic nearest-at-anchor selection if a vehicle cap is requested.
    candidates.append((float(np.linalg.norm(h[-1])),int(track.id),h,f,hv,fv))
   candidates.sort(key=lambda x:(x[0],x[1]))
   if max_vehicles is not None: candidates=candidates[:max_vehicles]
   for _,tid,h,f,hv,fv in candidates:
    rows["history_xy"].append(h); rows["history_vxy"].append(velocities(h)); rows["future_xy"].append(f)
    rows["future_relative_xy"].append((f-sdc_future_anchor).astype(np.float32)); rows["sdc_future_xy"].append(sdc_future_anchor)
    rows["history_valid"].append(hv); rows["future_valid"].append(fv); rows["scenario_id"].append(sid); rows["track_id"].append(tid); rows["sdc_track_id"].append(sdc_id); rows["split"].append(split)
 if not rows["scenario_id"]: raise RuntimeError("No eligible non-SDC vehicle samples were exported")
 arrays={"history_xy":np.asarray(rows["history_xy"],np.float32),"history_vxy":np.asarray(rows["history_vxy"],np.float32),"future_xy":np.asarray(rows["future_xy"],np.float32),"future_relative_xy":np.asarray(rows["future_relative_xy"],np.float32),"sdc_future_xy":np.asarray(rows["sdc_future_xy"],np.float32),"history_valid":np.asarray(rows["history_valid"],bool),"future_valid":np.asarray(rows["future_valid"],bool),"scenario_id":np.asarray(rows["scenario_id"],str),"track_id":np.asarray(rows["track_id"],np.int64),"sdc_track_id":np.asarray(rows["sdc_track_id"],np.int64),"split":np.asarray(rows["split"],str)}
 output.parent.mkdir(parents=True,exist_ok=True); np.savez_compressed(output,**arrays)
 return {"output":str(output),"samples":len(arrays["scenario_id"]),"source_scenarios":len(seen),"retained_scenarios":len(set(rows["scenario_id"])),"splits":{x:int(np.sum(arrays["split"]==x)) for x in np.unique(arrays["split"])},"rejected":rejected,"geometry_contract":"trajectory in anchor-SDC frame; communication future_relative_xy = actor_future - true_SDC_future in same anchor orientation","true_sdc_future_geometry":True,"history_steps":HISTORY,"future_steps":FUTURE,"max_vehicles":max_vehicles}

def main():
 p=argparse.ArgumentParser(); p.add_argument("inputs",type=Path,nargs="*"); p.add_argument("--input",dest="flag_inputs",type=Path,nargs="+"); p.add_argument("--output",type=Path,required=True); p.add_argument("--fixed-split",choices=["official_validation"]); p.add_argument("--development-fraction",type=float,default=.10); p.add_argument("--max-vehicles",type=int); p.add_argument("--report",type=Path); a=p.parse_args()
 if not 0<=a.development_fraction<1: p.error("--development-fraction must be in [0,1)")
 supplied=list(a.inputs)+(list(a.flag_inputs) if a.flag_inputs else []); files=[]
 for item in supplied: files.extend(sorted(item.glob("*.tfrecord*")) if item.is_dir() else [item])
 if not files: p.error("no TFRecord files found")
 report=export(files,a.output,a.fixed_split,a.development_fraction,a.max_vehicles); text=json.dumps(report,indent=2,sort_keys=True)+"\n"
 if a.report: a.report.parent.mkdir(parents=True,exist_ok=True); a.report.write_text(text)
 print(text,end=""); return 0
if __name__=="__main__": raise SystemExit(main())
