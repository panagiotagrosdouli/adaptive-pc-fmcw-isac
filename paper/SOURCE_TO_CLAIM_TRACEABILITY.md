# Source-to-Claim Traceability

| Manuscript claim | Primary source | Evidence class | Claim boundary |
|---|---|---|---|
| Frozen benchmark contains 12000 units per policy / 72000 receiver-level records | `configs/paper_protocol_v2_1.json`, `artifacts/publication/v2_1/FINAL_RESULTS.json` | controlled simulation input + simulation output | protocol-specific, not field prevalence |
| B4 selection = 0.1223333 and 1468/1468 selected successes | `artifacts/publication/v2_1/FINAL_RESULTS.json` | simulation output | conditional on frozen state/seed/model bank |
| B4 conditional Wilson lower 95% ~= 0.9981604 | `artifacts/publication/v2_1/FINAL_RESULTS.json` and confidence implementation | statistical derivation | confidence-qualified simulation result, not hardware guarantee |
| B4-B3 unconditional paired difference ~= -0.0394167 | `artifacts/publication/v2_1/FINAL_RESULTS.json` | paired statistical derivation | rejects unconditional-superiority wording under frozen protocol |
| QoS thresholds and no post-hoc tuning | `configs/paper_protocol_v2_1.json` | controlled protocol input | frozen v2.1 only |
| Parking profile physical scales | source-grounded profile config/docs + analytical formulas | literature/source-derived + analytical | not measured by this project |
| High-mobility profile physical scales | repository profile + analytical formulas | controlled capability reference + analytical | not a claimed commercial preset |
| B4 finite-draw calibration | supplemental reliability-calibration evidence | simulation/statistical derivation | high-draw reference is not physical truth |
| Distribution-shift behavior | supplemental distribution-shift evidence | simulation output + paired statistics | only evaluated families |
| Model-mismatch boundaries | supplemental mismatch evidence | simulation output | only tested CFO/Doppler/SNR/INR slices |
| Host runtime scaling | supplemental runtime evidence | host runtime measurement | not ECU or production real-time certification |
| Empirical Pareto partition | supplemental Pareto evidence | simulation-derived empirical partition | not global Pareto optimality |
