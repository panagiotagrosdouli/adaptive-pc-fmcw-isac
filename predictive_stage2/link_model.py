"""Geometry-to-link mapping for the predictive-connectivity study.

Scientific boundary: the DPSK BER curve is receiver-derived from Part A. The
range/pointing/atmospheric SNR mapping below is a configurable model extension;
it is not a WOMD measurement and is not claimed to be reported by Part A.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import numpy as np

@dataclass(frozen=True)
class LinkConfig:
    data_rate_bps: float=1e9; packet_bits:int=12000; reference_range_m:float=20.; reference_snr_db:float=20.; range_power_exponent:float=2.; atmospheric_loss_db_per_km:float=.5; pointing_sigma_deg:float=4.; fov_half_angle_deg:float=12.; outage_per_threshold:float=.10
    def validate(self):
        if self.data_rate_bps<=0 or self.packet_bits<=0: raise ValueError("rate and packet size must be positive")
        if self.reference_range_m<=0 or self.range_power_exponent<=0: raise ValueError("range parameters must be positive")
        if self.pointing_sigma_deg<=0 or self.fov_half_angle_deg<=0: raise ValueError("angular parameters must be positive")
        if not 0<=self.outage_per_threshold<=1: raise ValueError("outage PER threshold must be in [0,1]")
class BerLut:
    def __init__(self,snr_db,ber):
        order=np.argsort(snr_db); self.snr_db=np.asarray(snr_db,float)[order]; self.ber=np.asarray(ber,float)[order]
        if self.snr_db.ndim!=1 or len(self.snr_db)<2: raise ValueError("BER LUT needs at least two SNR points")
        if np.any(~np.isfinite(self.snr_db)) or np.any(~np.isfinite(self.ber)): raise ValueError("BER LUT must be finite")
        if np.any((self.ber<0)|(self.ber>1)): raise ValueError("BER must be in [0,1]")
    @classmethod
    def from_csv(cls,path):
        t=np.genfromtxt(path,delimiter=",",names=True); return cls(t["snr_db"],t["ber"])
    def __call__(self,snr_db): return np.interp(snr_db,self.snr_db,self.ber,left=self.ber[0],right=self.ber[-1])
def geometry(range_m,bearing_deg):
    r=np.asarray(range_m,float); b=np.asarray(bearing_deg,float)
    if np.any(~np.isfinite(r)) or np.any(~np.isfinite(b)) or np.any(r<=0): raise ValueError("range must be finite/positive and bearing finite")
    return r,b
def snr_from_geometry(range_m,bearing_deg,cfg):
    cfg.validate(); r,b=geometry(range_m,bearing_deg); range_loss=10.*cfg.range_power_exponent*np.log10(r/cfg.reference_range_m); atmospheric=cfg.atmospheric_loss_db_per_km*r/1000.; pointing=(10./np.log(10.))*(b/cfg.pointing_sigma_deg)**2; snr=cfg.reference_snr_db-range_loss-atmospheric-pointing; fov=np.abs(b)<=cfg.fov_half_angle_deg; return np.where(fov,snr,-np.inf),fov
def packet_error_rate(ber,packet_bits):
    b=np.clip(np.asarray(ber,float),0.,1.); return -np.expm1(packet_bits*np.log1p(-b))
def link_state(range_m,bearing_deg,lut,cfg):
    snr,fov=snr_from_geometry(range_m,bearing_deg,cfg); finite=np.where(fov,snr,lut.snr_db[0]); ber=np.where(fov,np.asarray(lut(finite)),1.); per=packet_error_rate(ber,cfg.packet_bits); goodput=cfg.data_rate_bps*(1.-per); outage=(~fov)|(per>=cfg.outage_per_threshold); return {"snr_db":snr,"ber":ber,"per":per,"goodput_bps":goodput,"outage":outage}
def usable_link_lifetime_s(outage,dt_s=.1):
    x=np.asarray(outage,bool).reshape(-1); first=np.flatnonzero(x); return float((first[0] if len(first) else len(x))*dt_s)
@dataclass(frozen=True)
class LinkState:
    snr_db:float; ber:float; per:float; goodput_bps:float; outage:bool
class LinkModel:
    """Stable scalar adapter shared by sensitivity, predictor and scheduler code."""
    def __init__(self,cfg,lut): cfg.validate(); self.cfg=cfg; self.lut=lut
    @classmethod
    def from_dict(cls,payload,lut):
        ext=payload.get("paper_extension_assumptions",payload); part=payload.get("part_a_fixed",{})
        cfg=LinkConfig(data_rate_bps=float(part.get("data_rate_bps",ext.get("data_rate_bps",1e9))),**{k:ext[k] for k in ("packet_bits","reference_range_m","reference_snr_db","range_power_exponent","atmospheric_loss_db_per_km","pointing_sigma_deg","fov_half_angle_deg","outage_per_threshold") if k in ext}); return cls(cfg,lut)
    def evaluate(self,*,range_m,pointing_error_rad):
        s=link_state(float(range_m),float(np.rad2deg(pointing_error_rad)),self.lut,self.cfg); scalar=lambda x: np.asarray(x).item(); return LinkState(float(scalar(s["snr_db"])),float(scalar(s["ber"])),float(scalar(s["per"])),float(scalar(s["goodput_bps"])),bool(scalar(s["outage"])))
