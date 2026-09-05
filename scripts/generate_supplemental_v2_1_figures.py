#!/usr/bin/env python3
"""Generate reviewer-grade supplemental v2.1 paper figures.

Deterministic post-processing only. Values below are copied from successful
GitHub Actions run 33975266575 at commit
ef0e135b88c7c9647d72195f80884e380bc33cf6. This script does not rerun
simulations, alter thresholds, or tune policies.
"""
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper" / "figures" / "v2_1_supplemental"
OUT.mkdir(parents=True, exist_ok=True)

UNCERTAINTY = {
    0.0: {"b3_sel": .1666666667, "b3_cond": 1.0, "b4_sel": .1666666667, "b4_cond": 1.0},
    0.5: {"b3_sel": .1666666667, "b3_cond": 1.0, "b4_sel": .1616666667, "b4_cond": 1.0},
    1.0: {"b3_sel": .185, "b3_cond": .8738738739, "b4_sel": .125, "b4_cond": 1.0},
    1.5: {"b3_sel": .1975, "b3_cond": .7468354430, "b4_sel": .1116666667, "b4_cond": 1.0},
    2.0: {"b3_sel": .2033333333, "b3_cond": .6803278689, "b4_sel": .0975, "b4_cond": 1.0},
    3.0: {"b3_sel": .2283333333, "b3_cond": .6204379562, "b4_sel": .0591666667, "b4_cond": .9859154930},
}

ABLATIONS = {
    "FULL_B4": (.125, 1.0),
    "NO_PHYSICS_GATE": (.3166666667, 0.0),
    "NO_STATE_UNCERTAINTY": (.2, .8083333333),
    "NO_JOINT_CONSTRAINT": (.6725, .8550185874),
}

RUNTIME_MS = {
    64: (.4355065, 30.7122245),
    128: (.43469, 61.0263645),
    256: (.437189, 121.3587365),
    512: (.436046, 240.4423565),
}

MISMATCH = [
    ("CFO 500→1000 Hz", .88, 1.0),
    ("CFO 500→2000 Hz", .87, 1.0),
    ("CFO 500→5000 Hz", .88, 1.0),
    ("SNR 12→10 dB", 0.0, 1.0),
    ("SNR 12→8 dB", 0.0, .17),
    ("SNR 12→6 dB", 0.0, 0.0),
    ("Doppler 20→25 m/s", .86, 1.0),
    ("Doppler 20→30 m/s", .86, 1.0),
    ("Doppler 20→40 m/s", .86, 1.0),
    ("INR -10→0 dB", .18, .86),
    ("INR -10→10 dB", 0.0, 0.0),
    ("INR -10→20 dB", 0.0, 0.0),
]

RANGES = [0, 5, 10, 20, 30, 40, 50, 60]
VELOCITIES = [-60, -50, -30, -10, 0, 10, 30, 50, 60]
PARKING_RMAX = 22.36214138927739
PARKING_VMAX = 8.405458863243837
MOBILE_RMAX = 56.21108587500001
MOBILE_VMAX = 48.66760681818181


def uncertainty_figure():
    x = np.array(sorted(UNCERTAINTY))
    fig, ax = plt.subplots(figsize=(7.2, 4.5))
    ax.plot(x, [UNCERTAINTY[v]["b3_cond"] for v in x], marker="o", label="B3 conditional joint QoS")
    ax.plot(x, [UNCERTAINTY[v]["b4_cond"] for v in x], marker="o", label="B4 conditional joint QoS")
    ax.plot(x, [UNCERTAINTY[v]["b3_sel"] for v in x], marker="s", linestyle="--", label="B3 selection rate")
    ax.plot(x, [UNCERTAINTY[v]["b4_sel"] for v in x], marker="s", linestyle="--", label="B4 selection rate")
    ax.set(xlabel="State-uncertainty scale", ylabel="Probability / rate", ylim=(0, 1.05))
    ax.grid(True, alpha=.25); ax.legend(fontsize=8); fig.tight_layout()
    fig.savefig(OUT / "uncertainty_tradeoff.svg"); plt.close(fig)


def ablation_figure():
    labels = list(ABLATIONS); x = np.arange(len(labels)); w = .36
    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    ax.bar(x-w/2, [ABLATIONS[k][0] for k in labels], w, label="Selection rate")
    ax.bar(x+w/2, [ABLATIONS[k][1] for k in labels], w, label="Conditional joint QoS")
    ax.set_xticks(x); ax.set_xticklabels([s.replace("_", "\n") for s in labels], fontsize=8)
    ax.set(ylim=(0, 1.05), ylabel="Probability / rate"); ax.legend(); fig.tight_layout()
    fig.savefig(OUT / "ablation.svg"); plt.close(fig)


def runtime_figure():
    draws = np.array(sorted(RUNTIME_MS))
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    ax.plot(draws, [RUNTIME_MS[d][0] for d in draws], marker="o", label="B3 median")
    ax.plot(draws, [RUNTIME_MS[d][1] for d in draws], marker="o", label="B4 median")
    ax.set(xlabel="B4 robust uncertainty draws", ylabel="Decision latency (ms)")
    ax.grid(True, alpha=.25); ax.legend(); fig.tight_layout()
    fig.savefig(OUT / "runtime_scaling.svg"); plt.close(fig)


def physics_figure():
    z = np.zeros((len(VELOCITIES), len(RANGES)))
    for i, v in enumerate(VELOCITIES):
        for j, r in enumerate(RANGES):
            parking = r <= PARKING_RMAX and abs(v) <= PARKING_VMAX
            mobile = r <= MOBILE_RMAX and abs(v) <= MOBILE_VMAX
            z[i, j] = 2 if parking and mobile else 1 if mobile else 0
    fig, ax = plt.subplots(figsize=(7.3, 4.7))
    im = ax.imshow(z, origin="lower", aspect="auto", extent=[min(RANGES), max(RANGES), min(VELOCITIES), max(VELOCITIES)], vmin=0, vmax=2)
    ax.set(xlabel="Range (m)", ylabel="Radial velocity (m/s)")
    cb = fig.colorbar(im, ax=ax, ticks=[0, 1, 2]); cb.ax.set_yticklabels(["No profile", "High-mobility only", "Both profiles"])
    fig.tight_layout(); fig.savefig(OUT / "physics_gate_map.svg"); plt.close(fig)


def mismatch_figure():
    y = np.arange(len(MISMATCH))
    fig, ax = plt.subplots(figsize=(8.0, 6.0))
    ax.scatter([x[1] for x in MISMATCH], y, label="B3")
    ax.scatter([x[2] for x in MISMATCH], y, label="B4", marker="x")
    ax.set_yticks(y); ax.set_yticklabels([x[0] for x in MISMATCH], fontsize=8)
    ax.set(xlim=(-.02, 1.02), xlabel="Unconditional joint QoS")
    ax.grid(True, axis="x", alpha=.25); ax.legend(); fig.tight_layout()
    fig.savefig(OUT / "model_mismatch.svg"); plt.close(fig)


if __name__ == "__main__":
    uncertainty_figure(); ablation_figure(); runtime_figure(); physics_figure(); mismatch_figure()
