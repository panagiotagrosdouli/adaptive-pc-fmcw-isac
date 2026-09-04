"""Traceable free-space communication and monostatic radar link-budget helpers."""
from __future__ import annotations
import math

C0 = 299_792_458.0
KTB_DBM_PER_HZ_290K = -173.97518719422808


def wavelength_m(carrier_hz: float) -> float:
    if carrier_hz <= 0:
        raise ValueError("carrier_hz must be positive")
    return C0 / carrier_hz


def free_space_path_loss_db(range_m: float, carrier_hz: float) -> float:
    """One-way free-space propagation loss, excluding antenna gains."""
    if range_m <= 0:
        raise ValueError("range_m must be positive")
    lam = wavelength_m(carrier_hz)
    return 20.0 * math.log10(4.0 * math.pi * range_m / lam)


def communication_received_power_dbm(tx_power_dbm: float, range_m: float, carrier_hz: float,
                                     tx_gain_dbi: float = 0.0, rx_gain_dbi: float = 0.0,
                                     additional_loss_db: float = 0.0) -> float:
    return (
        tx_power_dbm + tx_gain_dbi + rx_gain_dbi
        - free_space_path_loss_db(range_m, carrier_hz)
        - additional_loss_db
    )


def thermal_noise_dbm(noise_bandwidth_hz: float, noise_figure_db: float = 0.0,
                      temperature_k: float = 290.0) -> float:
    if noise_bandwidth_hz <= 0 or temperature_k <= 0:
        raise ValueError("bandwidth and temperature must be positive")
    # Reference -173.975 dBm/Hz at 290 K, adjusted by 10log10(T/290).
    density = KTB_DBM_PER_HZ_290K + 10.0 * math.log10(temperature_k / 290.0)
    return density + 10.0 * math.log10(noise_bandwidth_hz) + noise_figure_db


def communication_snr_db(tx_power_dbm: float, range_m: float, carrier_hz: float,
                         noise_bandwidth_hz: float, noise_figure_db: float,
                         tx_gain_dbi: float = 0.0, rx_gain_dbi: float = 0.0,
                         additional_loss_db: float = 0.0) -> float:
    pr = communication_received_power_dbm(
        tx_power_dbm, range_m, carrier_hz, tx_gain_dbi, rx_gain_dbi, additional_loss_db
    )
    return pr - thermal_noise_dbm(noise_bandwidth_hz, noise_figure_db)


def monostatic_radar_received_power_dbm(tx_power_dbm: float, range_m: float, carrier_hz: float,
                                        rcs_dbsm: float, tx_gain_dbi: float = 0.0,
                                        rx_gain_dbi: float | None = None,
                                        additional_loss_db: float = 0.0) -> float:
    """Classical point-target monostatic radar equation in dB units."""
    if range_m <= 0:
        raise ValueError("range_m must be positive")
    if rx_gain_dbi is None:
        rx_gain_dbi = tx_gain_dbi
    lam = wavelength_m(carrier_hz)
    sigma_m2 = 10.0 ** (rcs_dbsm / 10.0)
    geometric_loss_db = (
        30.0 * math.log10(4.0 * math.pi)
        + 40.0 * math.log10(range_m)
        - 20.0 * math.log10(lam)
        - 10.0 * math.log10(sigma_m2)
    )
    return tx_power_dbm + tx_gain_dbi + rx_gain_dbi - geometric_loss_db - additional_loss_db


def monostatic_radar_snr_db(tx_power_dbm: float, range_m: float, carrier_hz: float,
                            rcs_dbsm: float, noise_bandwidth_hz: float, noise_figure_db: float,
                            tx_gain_dbi: float = 0.0, rx_gain_dbi: float | None = None,
                            additional_loss_db: float = 0.0) -> float:
    pr = monostatic_radar_received_power_dbm(
        tx_power_dbm, range_m, carrier_hz, rcs_dbsm,
        tx_gain_dbi=tx_gain_dbi, rx_gain_dbi=rx_gain_dbi,
        additional_loss_db=additional_loss_db,
    )
    return pr - thermal_noise_dbm(noise_bandwidth_hz, noise_figure_db)
