# Claim Audit

Frozen baseline: `3904c4c2a69c4af96751d64614f7228ddea24b56`.

| Claim | Support | Sample/statistics | Allowed wording | Forbidden stronger wording |
|---|---|---|---|---|
| B4 selected cases were all successful in the frozen benchmark | `artifacts/publication/v2_1/FINAL_RESULTS.json` | 1468/1468; one-sided 95% Wilson lower 0.9981604 | B4 achieved 1468/1468 selected joint-QoS successes under the frozen evaluated uncertainty/model protocol | B4 guarantees 99.8% reliability in real vehicles |
| B4 is more selective than B3 | Frozen paired benchmark | B4 selection 0.12233 vs B3 0.19067 | B4 trades availability for stronger selected-case reliability | B4 dominates B3 |
| B4 does not improve unconditional joint QoS vs B3 | Frozen paired benchmark | mean difference -0.0394167; 95% bootstrap CI [-0.0429167,-0.036] | Unconditional B4-B3 effect is negative under the frozen protocol | B4 is universally worse than B3 |
| Physics gating is necessary in the evaluated controller design | supplemental ablation | no-gate ablation exhibits selected physically invalid cases and joint-QoS collapse in the frozen ablation | The ablation shows that removing the gate is damaging for this evaluated design | All ungated ISAC controllers fail |
| Robustness is bounded | mismatch/uncertainty supplemental families | evaluated CFO/Doppler/SNR/INR grids and uncertainty scales | B4 shows resilience on tested moderate mismatch slices and fails under severe mismatch | B4 is robust to arbitrary model mismatch |
| Runtime is substantial | host runtime artifact | Python/Linux host timing; draw-dependent | B4 host runtime grows roughly linearly with draw count in the reference implementation | Real-time automotive ECU operation is demonstrated |
| High-mobility profile is a useful capability reference | configuration + analytical derivation | source/composite parameters | Composite high-mobility capability profile used by the simulator | Commercial radar preset or hardware validation |

## Global forbidden claims

- universal B4 superiority;
- adaptive-controller RF/hardware measurement validation;
- global Pareto optimality;
- arbitrary distributional robustness;
- production real-time/ECU certification;
- independently measured PER without a packet model;
- field prevalence inferred from fixed scenario probabilities.
