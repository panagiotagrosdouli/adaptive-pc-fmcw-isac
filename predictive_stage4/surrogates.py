"""Differentiable communication-aware losses derived from frozen Stage-02 assumptions.

The surrogates preserve the geometry/SNR semantics of Stage 02 while remaining
differentiable. They do not replace the receiver-derived BER LUT or the frozen
Stage-02 model used for final evidence.
"""
from __future__ import annotations
import json,math
from pathlib import Path
import torch

CONFIG_KEYS=("reference_range_m","reference_snr_db","range_power_exponent","atmospheric_loss_db_per_km","pointing_sigma_deg","fov_half_angle_deg")

def load_surrogate_config(path):
    payload=json.loads(Path(path).read_text())
    ext=payload.get("paper_extension_assumptions",payload)
    missing=[k for k in CONFIG_KEYS if k not in ext]
    if missing: raise ValueError(f"link config missing surrogate fields: {missing}")
    return {k:float(ext[k]) for k in CONFIG_KEYS}

def relative_geometry(actor_xy,sdc_xy):
    rel=actor_xy-sdc_xy
    r=torch.linalg.vector_norm(rel,dim=-1).clamp_min(1e-3)
    b=torch.atan2(rel[...,1],rel[...,0])
    return r,b

def soft_snr_db(actor_xy,sdc_xy,*,reference_range_m,reference_snr_db,range_power_exponent,atmospheric_loss_db_per_km,pointing_sigma_deg,**_):
    r,b=relative_geometry(actor_xy,sdc_xy); sigma=math.radians(pointing_sigma_deg)
    range_loss=10.*range_power_exponent*torch.log10(r/reference_range_m)
    atmospheric=atmospheric_loss_db_per_km*r/1000.
    angular=(10./math.log(10.))*(b/sigma)**2
    return reference_snr_db-range_loss-atmospheric-angular

def link_fidelity_loss(pred_actor_xy,true_actor_xy,sdc_future_xy,**cfg):
    return torch.mean((soft_snr_db(pred_actor_xy,sdc_future_xy,**cfg)-soft_snr_db(true_actor_xy,sdc_future_xy,**cfg))**2)

def outage_margin_loss(pred_actor_xy,true_actor_xy,sdc_future_xy,*,fov_half_angle_deg,margin_deg=1.,**_):
    _,bp=relative_geometry(pred_actor_xy,sdc_future_xy); _,bt=relative_geometry(true_actor_xy,sdc_future_xy)
    half=math.radians(fov_half_angle_deg); margin=math.radians(margin_deg)
    mp=(half-bp.abs())/margin; mt=(half-bt.abs())/margin
    return torch.mean((torch.sigmoid(mp)-torch.sigmoid(mt))**2)
