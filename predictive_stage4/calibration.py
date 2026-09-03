"""Post-hoc Gaussian calibration for deterministic learned forecasts.

Variance is fit on DEVELOPMENT residuals only. Official validation may only be
scored using a previously frozen calibration artifact.
"""
from __future__ import annotations
import json,math
from pathlib import Path
import numpy as np
LEVELS=(0.50,0.90,0.95)
# Chi-square(2) quantile: F(q)=1-exp(-q/2).
def chi2_df2_quantile(level): return -2.*math.log(1.-level)
def fit_isotropic_variance(residual_xy):
 r=np.asarray(residual_xy,float)
 if r.ndim!=3 or r.shape[-1]!=2: raise ValueError("residuals must be [N,H,2]")
 # Per-horizon MLE sigma^2, pooling x/y but not horizons.
 var=np.mean(r*r,axis=(0,2)); return np.maximum(var,1e-6)
def gaussian_nll(residual_xy,var_h):
 r=np.asarray(residual_xy,float); v=np.asarray(var_h,float)[None,:,None]
 return float(np.mean(.5*(np.log(2.*np.pi*v)+(r*r)/v)))
def coverage(residual_xy,var_h,levels=LEVELS):
 r2=np.sum(np.asarray(residual_xy,float)**2,axis=-1); v=np.asarray(var_h,float)[None,:]
 return {str(int(100*l)):float(np.mean(r2<=v*chi2_df2_quantile(l))) for l in levels}
def save_calibration(path:Path,var_h,*,checkpoint_sha256,development_dataset_sha256):
 payload={"schema":"stage04_gaussian_calibration_v1","fit_split":"development","official_validation_used_for_fit":False,"distribution":"isotropic Gaussian per horizon","variance_xy_m2":np.asarray(var_h,float).tolist(),"checkpoint_sha256":checkpoint_sha256,"development_dataset_sha256":development_dataset_sha256}
 path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n"); return payload
