#!/usr/bin/env python3
"""Export official WOMD Scenario TFRecords to the Stage-01 v2 NPZ contract.

TensorFlow and Waymo Open Dataset protos are runtime-only dependencies. Geometry
is expressed in the SDC-at-anchor orientation while retaining the true future
SDC trajectory, so downstream relative geometry is actor minus SDC, not actor
minus a stationary origin.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np

HISTORY, FUTURE, CURRENT = 11, 80, 10

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def stable_dev(scenario_id: str, fraction: float) -> bool:
    u = int(hashlib.sha256(scenario_id.encode()).hexdigest()[:16], 16) / 2**64
    return u < fraction

def rotate_anchor(points: np.ndarray, origin: np.ndarray, yaw: float) -> np.ndarray:
    d = points - origin; c, s = np.cos(yaw), np.sin(yaw)
    return np.stack((c*d[...,0] + s*d[...,1], -s*d[...,0] + c*d[...,1]), axis=-1)

def states_xy(track):
    states=list(track.states)
    return np.asarray([[x.center_x,x.center_y] for x in states],np.float32), np.asarray([bool(x.valid) for x in states],bool)

def velocities(x: np.ndarray, dt: float=.1) -> np.ndarray:
    y=np.zeros_like(x); y[1:]=(x[1:]-x[:-1])/dt; y[0]=y[1]; return y

def export(files: list[Path], output: Path, fixed_split: str|None, dev_fraction: float) -> dict:
    import tensorflow as tf
    from waymo_open_dataset.protos import scenario_pb2
    keys=("history_xy","history_vxy","future_xy","future_relative_xy","sdc_future_xy","history_valid","future_valid","scenario_id","track_id","sdc_track_id","split")
    rows={k:[] for k in keys}; seen=set(); rejected={"time_contract":0,"sdc_invalid":0,"non_vehicle":0,"invalid_window":0}
    for file in files:
        for raw in tf.data.TFRecordDataset(str(file)):
            sc=scenario_pb2.Scenario.FromString(bytes(raw.numpy())); sid=str(sc.scenario_id)
            if not sid: raise RuntimeError(f"empty scenario_id in {file}")
            if sid in seen: raise RuntimeError(f"duplicate scenario_id across input records: {sid}")
            seen.add(sid)
            if int(sc.current_time_index)!=CURRENT: rejected["time_contract"]+=1; continue
            tracks=list(sc.tracks)
            if not 0 <= int(sc.sdc_track_index) < len(tracks): rejected["sdc_invalid"]+=1; continue
            sdc=tracks[int(sc.sdc_track_index)]
            if len(sdc.states)<HISTORY+FUTURE: rejected["sdc_invalid"]+=1; continue
            sdc_xy,sdc_valid=states_xy(sdc)
            if not sdc_valid[:HISTORY+FUTURE].all(): rejected["sdc_invalid"]+=1; continue
            anchor=sdc.states[CURRENT]; origin=np.asarray([anchor.center_x,anchor.center_y],np.float32); yaw=float(anchor.heading)
            sdc_future=rotate_anchor(sdc_xy[HISTORY:HISTORY+FUTURE],origin,yaw).astype(np.float32)
            split=fixed_split or ("development" if stable_dev(sid,dev_fraction) else "training")
            for track in tracks:
                if int(track.object_type)!=1: rejected["non_vehicle"]+=1; continue
                if len(track.states)<HISTORY+FUTURE: rejected["invalid_window"]+=1; continue
                xy,valid=states_xy(track); hv=valid[:HISTORY]; fv=valid[HISTORY:HISTORY+FUTURE]
                if not hv.all() or not fv.all(): rejected["invalid_window"]+=1; continue
                h=rotate_anchor(xy[:HISTORY],origin,yaw).astype(np.float32)
                f=rotate_anchor(xy[HISTORY:HISTORY+FUTURE],origin,yaw).astype(np.float32)
                rows["history_xy"].append(h); rows["history_vxy"].append(velocities(h)); rows["future_xy"].append(f)
                rows["sdc_future_xy"].append(sdc_future); rows["future_relative_xy"].append(f-sdc_future)
                rows["history_valid"].append(hv); rows["future_valid"].append(fv); rows["scenario_id"].append(sid)
                rows["track_id"].append(int(track.id)); rows["sdc_track_id"].append(int(sdc.id)); rows["split"].append(split)
    if not rows["scenario_id"]: raise RuntimeError("No eligible WOMD samples were exported")
    arrays={
      "history_xy":np.asarray(rows["history_xy"],np.float32),"history_vxy":np.asarray(rows["history_vxy"],np.float32),
      "future_xy":np.asarray(rows["future_xy"],np.float32),"future_relative_xy":np.asarray(rows["future_relative_xy"],np.float32),
      "sdc_future_xy":np.asarray(rows["sdc_future_xy"],np.float32),"history_valid":np.asarray(rows["history_valid"],bool),"future_valid":np.asarray(rows["future_valid"],bool),
      "scenario_id":np.asarray(rows["scenario_id"],str),"track_id":np.asarray(rows["track_id"],np.int64),"sdc_track_id":np.asarray(rows["sdc_track_id"],np.int64),"split":np.asarray(rows["split"],str)}
    output.parent.mkdir(parents=True,exist_ok=True); np.savez_compressed(output,**arrays)
    return {"schema":"womd_predictive_connectivity_npz_v2","output":str(output),"output_sha256":sha256_file(output),"input_files":[{"path":str(path),"sha256":sha256_file(path)} for path in files],"samples":len(arrays["scenario_id"]),"source_scenarios":len(seen),"retained_scenarios":len(set(rows["scenario_id"])),"splits":{x:int(np.sum(arrays["split"]==x)) for x in np.unique(arrays["split"])},"rejected":rejected,"true_future_sdc_geometry":True,"history_steps":HISTORY,"future_steps":FUTURE}

def main() -> int:
    p=argparse.ArgumentParser(); p.add_argument("--input",type=Path,nargs="+",required=True); p.add_argument("--output",type=Path,required=True); p.add_argument("--fixed-split",choices=["official_validation"]); p.add_argument("--development-fraction",type=float,default=.10); p.add_argument("--report",type=Path); a=p.parse_args()
    if not 0 <= a.development_fraction < 1: p.error("--development-fraction must be in [0,1)")
    files=[]
    for item in a.input: files.extend(sorted(item.glob("*.tfrecord*")) if item.is_dir() else [item])
    if not files: p.error("no TFRecord files found")
    report=export(files,a.output,a.fixed_split,a.development_fraction); text=json.dumps(report,indent=2,sort_keys=True)+"\n"
    if a.report: a.report.parent.mkdir(parents=True,exist_ok=True); a.report.write_text(text)
    print(text,end=""); return 0
if __name__=="__main__": raise SystemExit(main())
