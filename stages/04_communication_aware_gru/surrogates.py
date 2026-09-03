"""Differentiable communication-aware losses with explicit scientific scope.

These losses preserve Stage-02 geometry semantics but do not pretend that the
non-differentiable BER LUT/outage threshold itself is differentiable. Final
communication evidence is always evaluated through the frozen Stage-02 model.
"""
from __future__ import annotations
import math
import torch

def relative_geometry(actor_xy,sdc_xy):
    rel=actor_xy-sdc_xy; r=torch.linalg.vector_norm(rel,dim=-1).clamp_min(1e-3); b=torch.atan2(rel[...,1],rel[...,0]); return r,b

def soft_snr_db(actor_xy,sdc_xy,*,reference_range_m=20.,reference_snr_db=20.,range_power_exponent=2.,atmospheric_loss_db_per_km=.5,pointing_sigma_deg=4.):
    r,b=relative_geometry(actor_xy,sdc_xy); sigma=math.radians(pointing_sigma_deg)
    range_loss=10.*range_power_exponent*torch.log10(r/reference_range_m)
    atmospheric=atmospheric_loss_db_per_km*r/1000.
    angular=(10./math.log(10.))*(b/sigma)**2
    return reference_snr_db-range_loss-atmospheric-angular

def link_fidelity_loss(pred_actor_xy,true_actor_xy,sdc_future_xy,**kwargs):
    return torch.mean((soft_snr_db(pred_actor_xy,sdc_future_xy,**kwargs)-soft_snr_db(true_actor_xy,sdc_future_xy,**kwargs))**2)

def outage_margin_loss(pred_actor_xy,true_actor_xy,sdc_future_xy,*,fov_half_angle_deg=12.,margin_deg=1.,**kwargs):
    _,bp=relative_geometry(pred_actor_xy,sdc_future_xy); _,bt=relative_geometry(true_actor_xy,sdc_future_xy)
    half=math.radians(fov_half_angle_deg); margin=math.radians(margin_deg)
    # Softly penalize disagreement in signed distance to the FoV boundary.
    mp=(half-bp.abs())/margin; mt=(half-bt.abs())/margin
    return torch.mean((torch.sigmoid(mp)-torch.sigmoid(mt))**2)
