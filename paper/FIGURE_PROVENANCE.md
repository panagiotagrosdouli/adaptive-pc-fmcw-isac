# Figure Provenance

Final figures must be generated from machine-readable repository evidence, not screenshots.

| Figure family | Primary evidence | Claim boundary |
|---|---|---|
| System architecture | publication policy/receiver source | conceptual architecture |
| PC-FMCW signal flow | `if_model.py`, `comm_reference.py` | model structure, not measurement |
| Physical capability map | profile definitions and physics evidence | declared profiles only |
| Policy comparison | frozen `FINAL_RESULTS.json` | frozen primary scenario bank |
| Finite-draw calibration | supplemental calibration evidence | 4096-draw reference is not physical truth |
| Uncertainty scaling | supplemental uncertainty evidence | tested scales only |
| Confidence maps | supplemental confidence-map evidence | tested state slices only |
| Ablations | supplemental ablation evidence | evaluated design only |
| Distribution shift | supplemental shift evidence | evaluated families only |
| Model mismatch | supplemental mismatch evidence | evaluated CFO/Doppler/SNR/INR slices only |
| Action-space sensitivity | supplemental action-space evidence | declared restrictions only |
| Runtime | supplemental runtime evidence | Python/Linux host timing, not ECU certification |
| Empirical Pareto | supplemental Pareto evidence | realized evaluated points, not global Pareto proof |

Every final caption should identify the experiment, axes and SI units, sample size/state bank where applicable, uncertainty/statistical interval where available, and the interpretation boundary.
