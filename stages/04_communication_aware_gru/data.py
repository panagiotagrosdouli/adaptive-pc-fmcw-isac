"""Canonical Stage-04 dataset and training-only normalization."""
from __future__ import annotations
from dataclasses import dataclass
import hashlib,json
from pathlib import Path
import numpy as np

@dataclass(frozen=True)
class Normalization:
    mean: np.ndarray
    std: np.ndarray
    source_split: str="training"
    def transform(self,x): return (x-self.mean)/self.std
    def to_json(self): return {"mean":self.mean.tolist(),"std":self.std.tolist(),"source_split":self.source_split}

def sha256(path:Path): return hashlib.sha256(path.read_bytes()).hexdigest()
def canonical_input(history_xy,history_vxy): return np.concatenate([history_xy,history_vxy],axis=-1).astype(np.float32)
def fit_training_normalization(npz:Path):
    with np.load(npz,allow_pickle=False) as d:
        split=np.asarray(d["split"]).astype(str); mask=split=="training"
        if not mask.any(): raise RuntimeError("no training samples; normalization may not use development/official validation")
        x=canonical_input(np.asarray(d["history_xy"])[mask],np.asarray(d["history_vxy"])[mask])
    mean=x.reshape(-1,4).mean(0); std=x.reshape(-1,4).std(0); std=np.where(std<1e-8,1.0,std)
    return Normalization(mean.astype(np.float32),std.astype(np.float32))
def save_normalization(norm,path:Path,dataset:Path):
    payload={"schema":"stage04_training_normalization_v1","dataset_sha256":sha256(dataset),**norm.to_json()}
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n"); return payload
