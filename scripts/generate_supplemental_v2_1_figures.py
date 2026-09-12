#!/usr/bin/env python3
"""Generate supplemental figures directly from machine-readable experiment artifacts."""
from __future__ import annotations
import argparse, json
from pathlib import Path


def parse_args():
    p=argparse.ArgumentParser(); p.add_argument("--input-dir",default="artifacts/supplemental"); p.add_argument("--output-dir",default="paper/figures/v2_1_supplemental"); return p.parse_args()


def _load(root:Path,name:str)->dict:
    path=root/f"{name}.json"
    if not path.exists(): raise FileNotFoundError(f"missing experiment artifact: {path}")
    payload=json.loads(path.read_text())
    if "results" not in payload: raise ValueError(f"artifact has no results envelope: {path}")
    return payload["results"]


def _plotting(out:Path):
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ModuleNotFoundError as exc: raise RuntimeError("figure generation requires matplotlib and numpy") from exc
    out.mkdir(parents=True,exist_ok=True); return plt,np


def _runtime_series(data):
    numeric=[]
    for key,value in data.get("summary",data).items():
        try: draws=int(key)
        except (TypeError,ValueError): continue
        numeric.append((draws,value))
    if not numeric: raise ValueError("runtime artifact contains no draw-count summary")
    numeric.sort(); return ([d for d,_ in numeric], [v["B3_DETERMINISTIC_JOINT"]["median_us"]/1000. for _,v in numeric], [v["B4_ROBUST_JOINT"]["median_us"]/1000. for _,v in numeric])


def _mismatch_series(data):
    labels=[]; b3=[]; b4=[]
    for family,pairs in data["summary"].items():
        for pair,policies in pairs.items():
            labels.append(f"{family}: {pair}"); b3.append(policies["B3_DETERMINISTIC_JOINT"]["joint_qos_unconditional"]); b4.append(policies["B4_ROBUST_JOINT"]["joint_qos_unconditional"])
    if not labels: raise ValueError("mismatch artifact contains no cases")
    return labels,b3,b4


def uncertainty_figure(root,out):
    data=_load(root,"uncertainty")["summary"]; plt,np=_plotting(out); x=np.array(sorted(float(k) for k in data)); b3=[data[str(float(v))]["B3_DETERMINISTIC_JOINT"] for v in x]; b4=[data[str(float(v))]["B4_ROBUST_JOINT"] for v in x]
    fig,ax=plt.subplots(figsize=(7.2,4.5)); ax.plot(x,[r["joint_qos_conditional_on_selection"] for r in b3],marker="o",label="B3 conditional joint QoS"); ax.plot(x,[r["joint_qos_conditional_on_selection"] for r in b4],marker="o",label="B4 conditional joint QoS"); ax.plot(x,[r["selection_rate"] for r in b3],marker="s",linestyle="--",label="B3 selection rate"); ax.plot(x,[r["selection_rate"] for r in b4],marker="s",linestyle="--",label="B4 selection rate"); ax.set(xlabel="State-uncertainty scale",ylabel="Probability / rate",ylim=(0,1.05)); ax.grid(True,alpha=.25); ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(out/"uncertainty_tradeoff.svg"); plt.close(fig)


def ablation_figure(root,out):
    data=_load(root,"ablations")["summary"]; plt,np=_plotting(out); labels=list(data); x=np.arange(len(labels)); w=.36; fig,ax=plt.subplots(figsize=(7.4,4.4)); ax.bar(x-w/2,[data[k]["selection_rate"] for k in labels],w,label="Selection rate"); ax.bar(x+w/2,[data[k]["joint_qos_conditional_on_selection"] or 0. for k in labels],w,label="Conditional joint QoS"); ax.set_xticks(x); ax.set_xticklabels([s.replace("_","\n") for s in labels],fontsize=8); ax.set(ylim=(0,1.05),ylabel="Probability / rate"); ax.legend(); fig.tight_layout(); fig.savefig(out/"ablation.svg"); plt.close(fig)


def runtime_figure(root,out):
    plt,np=_plotting(out); draws,b3,b4=_runtime_series(_load(root,"runtime")); fig,ax=plt.subplots(figsize=(7.2,4.4)); ax.plot(np.array(draws),b3,marker="o",label="B3 median"); ax.plot(np.array(draws),b4,marker="o",label="B4 median"); ax.set(xlabel="B4 robust uncertainty draws",ylabel="Decision latency (ms)"); ax.grid(True,alpha=.25); ax.legend(); fig.tight_layout(); fig.savefig(out/"runtime_scaling.svg"); plt.close(fig)


def physics_figure(root,out):
    data=_load(root,"physics"); plt,np=_plotting(out); ranges=list(data["axes"]["range_m"]); velocities=list(data["axes"]["radial_velocity_mps"]); index={(c["range_m"],c["radial_velocity_mps"]):c for c in data["cells"]}; z=np.zeros((len(velocities),len(ranges)))
    for i,v in enumerate(velocities):
        for j,r in enumerate(ranges): z[i,j]=min(sum(bool(x) for x in index[(r,v)]["profiles"].values()),2)
    fig,ax=plt.subplots(figsize=(7.3,4.7)); im=ax.imshow(z,origin="lower",aspect="auto",extent=[min(ranges),max(ranges),min(velocities),max(velocities)],vmin=0,vmax=2); ax.set(xlabel="Range (m)",ylabel="Radial velocity (m/s)"); cb=fig.colorbar(im,ax=ax,ticks=[0,1,2]); cb.ax.set_yticklabels(["No profile","One profile","Both profiles"]); fig.tight_layout(); fig.savefig(out/"physics_gate_map.svg"); plt.close(fig)


def mismatch_figure(root,out):
    plt,np=_plotting(out); labels,b3,b4=_mismatch_series(_load(root,"mismatch")); y=np.arange(len(labels)); fig,ax=plt.subplots(figsize=(8.,max(4.5,.36*len(labels)))); ax.scatter(b3,y,label="B3"); ax.scatter(b4,y,label="B4",marker="x"); ax.set_yticks(y); ax.set_yticklabels(labels,fontsize=8); ax.set(xlim=(-.02,1.02),xlabel="Unconditional joint QoS"); ax.grid(True,axis="x",alpha=.25); ax.legend(); fig.tight_layout(); fig.savefig(out/"model_mismatch.svg"); plt.close(fig)


def distribution_shift_figure(root,out):
    data=_load(root,"distribution-shift")["summary"]; plt,np=_plotting(out); labels=list(data); x=np.arange(len(labels)); w=.36
    fig,ax=plt.subplots(figsize=(8.4,4.6)); ax.bar(x-w/2,[data[k]["B3_DETERMINISTIC_JOINT"]["joint_qos_probability_unconditional"] for k in labels],w,label="B3 unconditional joint QoS"); ax.bar(x+w/2,[data[k]["B4_ROBUST_JOINT"]["joint_qos_probability_unconditional"] for k in labels],w,label="B4 unconditional joint QoS"); ax.set_xticks(x); ax.set_xticklabels([s.replace("_","\n") for s in labels],fontsize=8); ax.set(ylim=(0,1.05),ylabel="Probability"); ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(out/"distribution_shift.svg"); plt.close(fig)


def reliability_calibration_figure(root,out):
    data=_load(root,"reliability-calibration")["summary"]; plt,np=_plotting(out); draws=np.array(sorted(int(k) for k in data)); fig,ax=plt.subplots(figsize=(7.2,4.4)); ax.plot(draws,[data[str(d)]["false_feasible_rate"] for d in draws],marker="o",label="False feasible"); ax.plot(draws,[data[str(d)]["false_infeasible_rate"] for d in draws],marker="o",label="False infeasible"); ax.plot(draws,[data[str(d)]["decision_disagreement_rate"] for d in draws],marker="s",linestyle="--",label="Decision disagreement"); ax.set(xlabel="Robust Monte Carlo draws",ylabel="Rate",ylim=(0,1.)); ax.grid(True,alpha=.25); ax.legend(); fig.tight_layout(); fig.savefig(out/"reliability_calibration.svg"); plt.close(fig)


def action_space_figure(root,out):
    data=_load(root,"action-space")["summary"]; plt,np=_plotting(out); labels=list(data); x=np.arange(len(labels)); w=.36; fig,ax=plt.subplots(figsize=(9.,4.8)); ax.bar(x-w/2,[data[k]["selection_rate"] for k in labels],w,label="Selection"); ax.bar(x+w/2,[data[k]["joint_qos_probability_conditional"] or 0. for k in labels],w,label="Conditional QoS"); ax.set_xticks(x); ax.set_xticklabels([s.replace("_","\n") for s in labels],fontsize=7); ax.set(ylim=(0,1.05),ylabel="Probability / rate"); ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(out/"action_space_sensitivity.svg"); plt.close(fig)


def reliability_target_figure(root,out):
    data=_load(root,"reliability-targets")["summary"]; plt,np=_plotting(out); targets=np.array(sorted(float(k) for k in data)); rows=[data[str(float(t))] for t in targets]
    fig,ax=plt.subplots(figsize=(7.3,4.5)); ax.plot(targets,[r["selection_rate"] for r in rows],marker="o",label="Selection rate"); ax.plot(targets,[r["joint_qos_probability_conditional"] or 0. for r in rows],marker="s",label="Conditional joint QoS"); ax.plot(targets,[r["wilson_lower_95_conditional"] or 0. for r in rows],marker="^",linestyle="--",label="Conditional Wilson LCB"); ax.set(xlabel="Reliability target",ylabel="Probability / rate",ylim=(0,1.05)); ax.grid(True,alpha=.25); ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(out/"reliability_target_sensitivity.svg"); plt.close(fig)


def qos_sensitivity_figure(root,out):
    data=_load(root,"qos-sensitivity")["summary"]; plt,np=_plotting(out); labels=list(data); x=np.arange(len(labels)); w=.36
    b3=[data[k]["B3_DETERMINISTIC_JOINT"]["counterfactual_joint_qos_unconditional"] for k in labels]; b4=[data[k]["B4_ROBUST_JOINT"]["counterfactual_joint_qos_unconditional"] for k in labels]
    fig,ax=plt.subplots(figsize=(9.2,4.8)); ax.bar(x-w/2,b3,w,label="B3 unconditional joint QoS"); ax.bar(x+w/2,b4,w,label="B4 unconditional joint QoS"); ax.set_xticks(x); ax.set_xticklabels([s.replace("_","\n") for s in labels],fontsize=7); ax.set(ylim=(0,1.05),ylabel="Counterfactual probability"); ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(out/"qos_threshold_sensitivity.svg"); plt.close(fig)


def uncertainty_sources_figure(root,out):
    data=_load(root,"uncertainty-sources")["summary"]; plt,np=_plotting(out); labels=list(data); x=np.arange(len(labels)); w=.36
    fig,ax=plt.subplots(figsize=(9.0,4.8)); ax.bar(x-w/2,[data[k]["selection_rate"] for k in labels],w,label="Selection rate"); ax.bar(x+w/2,[data[k]["joint_qos_probability_conditional"] or 0. for k in labels],w,label="Conditional joint QoS"); ax.set_xticks(x); ax.set_xticklabels([s.replace("_","\n") for s in labels],fontsize=7); ax.set(ylim=(0,1.05),ylabel="Probability / rate"); ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(out/"uncertainty_source_ablation.svg"); plt.close(fig)


def confidence_map_figures(root,out):
    maps=_load(root,"confidence-maps"); plt,np=_plotting(out)
    for name,data in maps.items():
        xs=list(data["x"]); ys=list(data["y"]); index={(c["x"],c["y"]):c for c in data["cells"]}; z=np.full((len(ys),len(xs)),np.nan)
        for i,y in enumerate(ys):
            for j,x in enumerate(xs):
                value=index[(x,y)].get("wilson_lower_95_conditional"); z[i,j]=np.nan if value is None else float(value)
        fig,ax=plt.subplots(figsize=(7.3,4.7)); im=ax.imshow(z,origin="lower",aspect="auto",extent=[min(xs),max(xs),min(ys),max(ys)],vmin=0,vmax=1); ax.set(xlabel="x-axis value",ylabel="y-axis value",title=f"{name}: conditional 95% Wilson lower bound"); fig.colorbar(im,ax=ax); fig.tight_layout(); fig.savefig(out/f"confidence_map_{name}.svg"); plt.close(fig)


def pareto_figure(root,out):
    data=_load(root,"pareto"); plt,np=_plotting(out); points=data.get("physical_points",[]); partition=data.get("pareto",{}); frontier={int(p["point_index"]) for p in partition.get("non_dominated_points",[])}
    if not points: raise ValueError("pareto artifact contains no physical points")
    fig,ax=plt.subplots(figsize=(7.3,4.5))
    dominated=[(i,p) for i,p in enumerate(points) if i not in frontier]; nondominated=[(i,p) for i,p in enumerate(points) if i in frontier]
    if dominated: ax.scatter([p["tx_power_fraction"] for _,p in dominated],[p["joint_qos_probability"] for _,p in dominated],label="Dominated")
    if nondominated: ax.scatter([p["tx_power_fraction"] for _,p in nondominated],[p["joint_qos_probability"] for _,p in nondominated],marker="x",label="Non-dominated")
    ax.set(xlabel="Transmit-power fraction",ylabel="Joint QoS probability",ylim=(-.02,1.02)); ax.grid(True,alpha=.25); ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(out/"empirical_pareto.svg"); plt.close(fig)


def main():
    args=parse_args(); root=Path(args.input_dir); out=Path(args.output_dir)
    uncertainty_figure(root,out); ablation_figure(root,out); runtime_figure(root,out); physics_figure(root,out)
    mismatch_figure(root,out); distribution_shift_figure(root,out); reliability_calibration_figure(root,out); action_space_figure(root,out)
    reliability_target_figure(root,out); qos_sensitivity_figure(root,out); uncertainty_sources_figure(root,out); confidence_map_figures(root,out); pareto_figure(root,out)


if __name__=="__main__": main()
