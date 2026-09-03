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
    data_rate_bps: float = 1e9
    packet_bits: int = 12000
    reference_range_m: float = 20.0
    reference_snr_db: float = 20.0
    range_power_exponent: float = 2.0
    atmospheric_loss_db_per_km: float = 0.5
    pointing_sigma_deg: float = 4.0
    fov_half_angle_deg: float = 12.0
    outage_per_threshold: float = 0.10

    def validate(self) -> None:
        if self.data_rate_bps <= 0 or self.packet_bits <= 0:
            raise ValueError("rate and packet size must be positive")
        if self.reference_range_m <= 0 or self.range_power_exponent <= 0:
            raise ValueError("range parameters must be positive")
        if self.pointing_sigma_deg <= 0 or self.fov_half_angle_deg <= 0:
            raise ValueError("angular parameters must be positive")
        if not 0 <= self.outage_per_threshold <= 1:
            raise ValueError("outage PER threshold must be in [0,1]")


class BerLut:
    def __init__(self, snr_db: np.ndarray, ber: np.ndarray):
        order = np.argsort(snr_db)
        self.snr_db = np.asarray(snr_db, float)[order]
        self.ber = np.asarray(ber, float)[order]
        if self.snr_db.ndim != 1 or len(self.snr_db) < 2:
            raise ValueError("BER LUT needs at least two SNR points")
        if np.any(~np.isfinite(self.snr_db)) or np.any(~np.isfinite(self.ber)):
            raise ValueError("BER LUT must be finite")
        if np.any((self.ber < 0) | (self.ber > 1)):
            raise ValueError("BER must be in [0,1]")

    @classmethod
    def from_csv(cls, path: str | Path) -> "BerLut":
        table = np.genfromtxt(path, delimiter=",", names=True)
        return cls(table["snr_db"], table["ber"])

    def __call__(self, snr_db):
        return np.interp(snr_db, self.snr_db, self.ber, left=self.ber[0], right=self.ber[-1])


def geometry(range_m, bearing_deg):
    r = np.asarray(range_m, dtype=float)
    b = np.asarray(bearing_deg, dtype=float)
    if np.any(~np.isfinite(r)) or np.any(~np.isfinite(b)) or np.any(r <= 0):
        raise ValueError("range must be finite/positive and bearing finite")
    return r, b


def snr_from_geometry(range_m, bearing_deg, cfg: LinkConfig):
    cfg.validate()
    r, b = geometry(range_m, bearing_deg)
    range_loss = 10.0 * cfg.range_power_exponent * np.log10(r / cfg.reference_range_m)
    atmospheric_loss = cfg.atmospheric_loss_db_per_km * (r / 1000.0)
    # Gaussian angular gain normalized to 0 dB on boresight.
    pointing_loss = (10.0 / np.log(10.0)) * (b / cfg.pointing_sigma_deg) ** 2
    snr = cfg.reference_snr_db - range_loss - atmospheric_loss - pointing_loss
    in_fov = np.abs(b) <= cfg.fov_half_angle_deg
    return np.where(in_fov, snr, -np.inf), in_fov


def packet_error_rate(ber, packet_bits: int):
    b = np.clip(np.asarray(ber, dtype=float), 0.0, 1.0)
    # Stable 1-(1-BER)^L.
    return -np.expm1(packet_bits * np.log1p(-b))


def link_state(range_m, bearing_deg, lut: BerLut, cfg: LinkConfig) -> dict[str, np.ndarray]:
    snr_db, in_fov = snr_from_geometry(range_m, bearing_deg, cfg)
    finite_snr = np.where(in_fov, snr_db, lut.snr_db[0])
    ber = np.asarray(lut(finite_snr))
    ber = np.where(in_fov, ber, 1.0)
    per = packet_error_rate(ber, cfg.packet_bits)
    goodput = cfg.data_rate_bps * (1.0 - per)
    outage = (~in_fov) | (per >= cfg.outage_per_threshold)
    return {"snr_db": snr_db, "ber": ber, "per": per, "goodput_bps": goodput, "outage": outage}


def usable_link_lifetime_s(outage, dt_s: float = 0.1) -> float:
    """Time from prediction anchor until first unusable future step."""
    x = np.asarray(outage, dtype=bool).reshape(-1)
    first = np.flatnonzero(x)
    return float((first[0] if len(first) else len(x)) * dt_s)
