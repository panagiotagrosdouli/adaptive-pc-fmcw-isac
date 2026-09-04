#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import numpy as np

from pcfmcw_isac.models import QoS, State
from pcfmcw_isac.simulator import run_trial


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--config", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()
    cfg = json.loads(Path(args.config).read_text())
    q = QoS(**cfg["qos"])
    rng = np.random.default_rng(cfg["seed"])
    rows = []
    trials = int(cfg["trials"])
    for i in range(trials):
        snr = float(rng.choice(cfg["snr_db"]))
        vel = float(rng.choice(cfg["velocity_mps"]))
        interference = float(rng.choice(cfg["interference_db"]))
        cfo = float(rng.choice(cfg["cfo_hz"]))
        pn = float(rng.choice(cfg["phase_noise_std_rad"]))
        u = float(rng.choice(cfg["state_uncertainty_scale"]))
        doppler = vel / 3e8 * 77e9
        truth = State(snr, doppler, interference, cfo, pn)
        estimate = State(snr + rng.normal(0, 1.5*u), doppler + rng.normal(0, 100*u), interference,
                         cfo + rng.normal(0, 50*u), pn)
        for row in run_trial(truth, estimate, q, rng, u):
            row.update({"trial": i, "snr_db": snr, "velocity_mps": vel, "doppler_hz": doppler,
                        "interference_db": interference, "cfo_hz": cfo,
                        "phase_noise_std_rad": pn, "uncertainty_scale": u})
            rows.append(row)
    summary = {}
    for policy in sorted({r["policy"] for r in rows}):
        pr = [r for r in rows if r["policy"] == policy]
        summary[policy] = {
            "n": len(pr),
            "joint_qos_rate": float(np.mean([r["joint_qos_met"] for r in pr])),
            "mean_resource_cost": float(np.mean([r["resource_cost"] for r in pr])),
            "mean_ber": float(np.mean([r["ber"] for r in pr])),
            "mean_rate_mbps": float(np.mean([r["effective_rate_mbps"] for r in pr])),
        }
    out = {"config": cfg, "summary": summary, "rows": rows}
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
