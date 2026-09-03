#!/usr/bin/env python3
"""Train one canonical Stage-04 objective using training data and development selection only."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,random,subprocess,sys
from pathlib import Path
import numpy as np, torch
from torch.utils.data import DataLoader,TensorDataset
HERE=Path(__file__).resolve().parent

def mod(name):
 s=importlib.util.spec_from_file_location(f"predictive_stage4_{name}",HERE/f"{name}.py"); m=importlib.util.module_from_spec(s); assert s.loader; sys.modules[s.name]=m; s.loader.exec_module(m); return m
modelm,obj,data,surr=mod("model"),mod("objectives"),mod("data"),mod("surrogates")
def git_sha():
 try:return subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
 except Exception:return "unknown"
def file_sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
 p=argparse.ArgumentParser(); p.add_argument("npz",type=Path); p.add_argument("--objective",choices=obj.OBJECTIVES,required=True); p.add_argument("--seed",type=int,required=True); p.add_argument("--lambda-link",type=float,default=0.); p.add_argument("--lambda-outage",type=float,default=0.); p.add_argument("--epochs",type=int,default=50); p.add_argument("--batch-size",type=int,default=256); p.add_argument("--lr",type=float,default=1e-3); p.add_argument("--link-config",type=Path,default=HERE.parent/"predictive_stage2"/"link_model_config.json"); p.add_argument("--output",type=Path,required=True); a=p.parse_args()
 random.seed(a.seed); np.random.seed(a.seed); torch.manual_seed(a.seed)
 try: torch.use_deterministic_algorithms(True,warn_only=True)
 except Exception: pass
 cfg=surr.load_surrogate_config(a.link_config); norm=data.fit_training_normalization(a.npz)
 with np.load(a.npz,allow_pickle=False) as d:
  sp=np.asarray(d["split"]).astype(str); x=data.canonical_input(d["history_xy"],d["history_vxy"]); y=np.asarray(d["future_xy"],np.float32); sdc=np.asarray(d["sdc_future_xy"],np.float32)
 tr=sp=="training"; dv=sp=="development"
 if not tr.any() or not dv.any(): raise RuntimeError("canonical training and development splits are both required")
 def ds(mask): return TensorDataset(torch.from_numpy(norm.transform(x[mask]).astype(np.float32)),torch.from_numpy(y[mask]),torch.from_numpy(sdc[mask]))
 gen=torch.Generator().manual_seed(a.seed); loader=DataLoader(ds(tr),batch_size=a.batch_size,shuffle=True,generator=gen); dev=DataLoader(ds(dv),batch_size=a.batch_size,shuffle=False)
 net=modelm.CommunicationAwareGRU(); opt=torch.optim.Adam(net.parameters(),lr=a.lr); weights=obj.LossWeights(a.lambda_link,a.lambda_outage); best=float("inf"); best_epoch=-1; best_components=None
 def components(xb,yb,sb):
  yh=net(xb); ade=torch.linalg.vector_norm(yh-yb,dim=-1).mean(); ll=surr.link_fidelity_loss(yh,yb,sb,**cfg); ol=surr.outage_margin_loss(yh,yb,sb,**cfg); total=obj.compose_loss(a.objective,yh,yb,weights=weights,link_loss=ll,outage_loss=ol)[0]; return total,ade,ll,ol
 for epoch in range(1,a.epochs+1):
  net.train()
  for xb,yb,sb in loader:
   opt.zero_grad(); loss,_,_,_=components(xb,yb,sb); loss.backward(); torch.nn.utils.clip_grad_norm_(net.parameters(),5.); opt.step()
  net.eval(); vals=[]; ades=[]; links=[]; outages=[]
  with torch.no_grad():
   for xb,yb,sb in dev:
    total,ade,ll,ol=components(xb,yb,sb); vals.append(float(total)); ades.append(float(ade)); links.append(float(ll)); outages.append(float(ol))
  score=float(np.mean(vals))
  if score<best:
   best=score; best_epoch=epoch; best_components={"development_ade_m":float(np.mean(ades)),"development_link_loss":float(np.mean(links)),"development_outage_loss":float(np.mean(outages))}; best_state={k:v.detach().cpu().clone() for k,v in net.state_dict().items()}
 a.output.parent.mkdir(parents=True,exist_ok=True); dataset_sha=hashlib.sha256(a.npz.read_bytes()).hexdigest()
 payload={"state_dict":best_state,"architecture":{"input_dim":4,"hidden_dim":128,"num_layers":2,"future_steps":80},"objective":a.objective,"seed":a.seed,"lambda_link":a.lambda_link,"lambda_outage":a.lambda_outage,"best_epoch":best_epoch,"development_objective":best,**best_components,"dataset_sha256":dataset_sha,"git_sha":git_sha(),"normalization":norm.to_json(),"selection_split":"development","official_validation_used_for_selection":False,"surrogate_link_config_sha256":file_sha(a.link_config),"surrogate_link_config":cfg}
 torch.save(payload,a.output); print(json.dumps({k:v for k,v in payload.items() if k not in {"state_dict","normalization"}},indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
