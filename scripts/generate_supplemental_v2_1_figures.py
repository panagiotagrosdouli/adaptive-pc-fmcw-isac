#!/usr/bin/env python3
"""Generate supplemental figures directly from machine-readable experiment artifacts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--input-dir", default="artifacts/supplemental")
    p.add_argument("--output-dir", default="paper/figures/v2_1_supplemental")
    return p.parse_args()


def _load(root: Path, name: str) -> dict:
    path = root / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(f"missing experiment artifact: {path}")
    payload = json.loads(path.read_text())
    if "results" not in payload:
        raise ValueError(f"artifact has no results envelope: {path}")
    return payload["results"]


def _plotting(out: Path):
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ModuleNotFoundError as exc:
        raise RuntimeError("figure generation requires matplotlib and numpy") from exc
    out.mkdir(parents=True, exist_ok=True)
    return plt, np


def uncertainty_figure(root: Path, out: Path) -> None:
    data = _load(root, "uncertainty")["summary"]
    plt, np = _plotting(out)
    x = np.array(sorted(float(k) for k in data))
    b3 = [data[str(float(v))]["B3_DETERMINISTIC_JOINT"] for v in x]
    b4 = [data[str(float(v))]["B4_ROBUST_JOINT"] for v in x]
    fig, ax = plt.subplots(figsize=(7.2, 4.5))
    ax.plot(x, [r["joint_qos_conditional_on_selection"] for r in b3], marker="o", label="B3 conditional joint QoS")
    ax.plot(x, [r["joint_qos_conditional_on_selection"] for r in b4], marker="o", label="B4 conditional joint QoS")
    ax.plot(x, [r["selection_rate"] for r in b3], marker="s", linestyle="--", label="B3 selection rate")
    ax.plot(x, [r["selection_rate"] for r in b4], marker="s", linestyle="--", label="B4 selection rate")
    ax.set(xlabel="State-uncertainty scale", ylabel="Probability / rate", ylim=(0, 1.05))
    ax.grid(True, alpha=.25); ax.legend(fontsize=8); fig.tight_layout()
    fig.savefig(out / "uncertainty_tradeoff.svg"); plt.close(fig)


def ablation_figure(root: Path, out: Path) -> None:
    data = _load(root, "ablations")["summary"]
    plt, np = _plotting(out)
    labels = list(data); x = np.arange(len(labels)); w = .36
    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    ax.bar(x-w/2, [data[k]["selection_rate"] for k in labels], w, label="Selection rate")
    ax.bar(x+w/2, [data[k]["joint_qos_conditional_on_selection"] or 0.0 for k in labels], w, label="Conditional joint QoS")
    ax.set_xticks(x); ax.set_xticklabels([s.replace("_", "\n") for s in labels], fontsize=8)
    ax.set(ylim=(0, 1.05), ylabel="Probability / rate"); ax.legend(); fig.tight_layout()
    fig.savefig(out / "ablation.svg"); plt.close(fig)


def runtime_figure(root: Path, out: Path) -> None:
    data = _load(root, "runtime")
    plt, np = _plotting(out)
    rows = data.get("summary", data)
    # Runtime payload is keyed by robust draw count in current supplemental code.
    numeric = []
    for key, value in rows.items():
        try:
            draws = int(key)
        except (TypeError, ValueError):
            continue
        numeric.append((draws, value))
    if not numeric:
        raise ValueError("runtime artifact contains no draw-count summary")
    numeric.sort()
    draws = np.array([d for d, _ in numeric])
    b3 = [v.get("B3_DETERMINISTIC_JOINT", v.get("b3", {})).get("median_ms") for _, v in numeric]
    b4 = [v.get("B4_ROBUST_JOINT", v.get("b4", {})).get("median_ms") for _, v in numeric]
    if any(v is None for v in b3 + b4):
        raise ValueError("runtime artifact missing median_ms for B3/B4")
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    ax.plot(draws, b3, marker="o", label="B3 median")
    ax.plot(draws, b4, marker="o", label="B4 median")
    ax.set(xlabel="B4 robust uncertainty draws", ylabel="Decision latency (ms)")
    ax.grid(True, alpha=.25); ax.legend(); fig.tight_layout()
    fig.savefig(out / "runtime_scaling.svg"); plt.close(fig)


def physics_figure(root: Path, out: Path) -> None:
    data = _load(root, "physics")
    plt, np = _plotting(out)
    ranges = list(data["axes"]["range_m"]); velocities = list(data["axes"]["radial_velocity_mps"])
    index = {(c["range_m"], c["radial_velocity_mps"]): c for c in data["cells"]}
    z = np.zeros((len(velocities), len(ranges)))
    for i, v in enumerate(velocities):
        for j, r in enumerate(ranges):
            support = index[(r, v)]["profiles"]
            count = sum(bool(x) for x in support.values())
            z[i, j] = min(count, 2)
    fig, ax = plt.subplots(figsize=(7.3, 4.7))
    im = ax.imshow(z, origin="lower", aspect="auto", extent=[min(ranges), max(ranges), min(velocities), max(velocities)], vmin=0, vmax=2)
    ax.set(xlabel="Range (m)", ylabel="Radial velocity (m/s)")
    cb = fig.colorbar(im, ax=ax, ticks=[0, 1, 2]); cb.ax.set_yticklabels(["No profile", "One profile", "Both profiles"])
    fig.tight_layout(); fig.savefig(out / "physics_gate_map.svg"); plt.close(fig)


def mismatch_figure(root: Path, out: Path) -> None:
    data = _load(root, "mismatch")
    summary = data["summary"]
    plt, np = _plotting(out)
    labels = [] ; b3 = [] ; b4 = []
    for case, policies in summary.items():
        labels.append(case)
        b3.append(policies["B3_DETERMINISTIC_JOINT"]["joint_qos_unconditional"])
        b4.append(policies["B4_ROBUST_JOINT"]["joint_qos_unconditional"])
    y = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(8.0, max(4.5, 0.36*len(labels))))
    ax.scatter(b3, y, label="B3")
    ax.scatter(b4, y, label="B4", marker="x")
    ax.set_yticks(y); ax.set_yticklabels(labels, fontsize=8)
    ax.set(xlim=(-.02, 1.02), xlabel="Unconditional joint QoS")
    ax.grid(True, axis="x", alpha=.25); ax.legend(); fig.tight_layout()
    fig.savefig(out / "model_mismatch.svg"); plt.close(fig)


def reliability_calibration_figure(root: Path, out: Path) -> None:
    data = _load(root, "reliability-calibration")["summary"]
    plt, np = _plotting(out)
    draws = np.array(sorted(int(k) for k in data))
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    ax.plot(draws, [data[str(d)]["false_feasible_rate"] for d in draws], marker="o", label="False feasible")
    ax.plot(draws, [data[str(d)]["false_infeasible_rate"] for d in draws], marker="o", label="False infeasible")
    ax.plot(draws, [data[str(d)]["decision_disagreement_rate"] for d in draws], marker="s", linestyle="--", label="Decision disagreement")
    ax.set(xlabel="Robust Monte Carlo draws", ylabel="Rate", ylim=(0, 1.0))
    ax.grid(True, alpha=.25); ax.legend(); fig.tight_layout()
    fig.savefig(out / "reliability_calibration.svg"); plt.close(fig)


def action_space_figure(root: Path, out: Path) -> None:
    data = _load(root, "action-space")["summary"]
    plt, np = _plotting(out)
    labels = list(data); x = np.arange(len(labels)); w = .28
    fig, ax = plt.subplots(figsize=(9.0, 4.8))
    ax.bar(x-w, [data[k]["selection_rate"] for k in labels], w, label="Selection")
    ax.bar(x, [data[k]["joint_qos_probability_conditional"] or 0.0 for k in labels], w, label="Conditional QoS")
    ax.bar(x+w, [data[k]["mean_normalized_resource_cost_selected"] or 0.0 for k in labels], w, label="Normalized cost")
    ax.set_xticks(x); ax.set_xticklabels([s.replace("_", "\n") for s in labels], fontsize=7)
    ax.set_ylabel("Metric value"); ax.legend(fontsize=8); fig.tight_layout()
    fig.savefig(out / "action_space_sensitivity.svg"); plt.close(fig)


def main() -> None:
    args = parse_args(); root = Path(args.input_dir); out = Path(args.output_dir)
    uncertainty_figure(root, out)
    ablation_figure(root, out)
    runtime_figure(root, out)
    physics_figure(root, out)
    mismatch_figure(root, out)
    reliability_calibration_figure(root, out)
    action_space_figure(root, out)


if __name__ == "__main__":
    main()
