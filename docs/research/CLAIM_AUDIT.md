# Claim Audit

Date: 2026-09-12
Evidence base: frozen publication v2.1 simulation artifacts plus completed reviewer-grade supplemental run `34696063382` and literature audit.

| Claim | Status | Evidence / reason | Required wording |
|---|---|---|---|
| PC-FMCW supports joint sensing and communication | SUPPORTED | Established prior PC-FMCW literature; not novel here. | Background only. |
| The repository separates one-way communication from monostatic two-way sensing | SUPPORTED | Explicit system-model design and repository documentation. | Methodological correctness claim. |
| Physics gating prevents use of profiles outside declared FMCW capability | SUPPORTED | Architectural mechanism plus physics/ablation evidence. | Do not call it a guarantee beyond modeled constraints. |
| B4 achieves very high conditional joint QoS on selected frozen states | SUPPORTED | Frozen benchmark: 1468/1468 selected successes; one-sided 95% Wilson lower bound 0.99816. | Always report selection/abstention simultaneously. |
| B4 achieves high confidence-qualified conditional reliability in supplemental full metrics | SUPPORTED | 150/150 selected successes; one-sided 95% Wilson lower bound 0.98228. | Scope to tested bank and declared uncertainty model. |
| B4 improves unconditional joint QoS over B3 | DO_NOT_CLAIM | Supplemental paired difference -0.03667, 95% CI [-0.04833,-0.02583]; frozen evidence is also negative. | Report as negative result. |
| B4 universally outperforms B0/B3 | DO_NOT_CLAIM | Frozen and supplemental unconditional results contradict this. | Use reliability-availability trade-off framing. |
| State uncertainty contracts the robust selectable region | SUPPORTED | Uncertainty sweep and ablations show B4 selection contracts as uncertainty grows. | Scope claim to tested state/uncertainty families. |
| Distribution shift reverses the unconditional B4-vs-B3 result | NOT_SUPPORTED | All four tested shift families retain negative B4-B3 unconditional joint-QoS differences with 95% CIs below zero. | State tested-shift robustness of the interpretation, not universal distributional robustness. |
| CFO is physically relevant to PC-FMCW communication | SUPPORTED | Communication stress validation and prior synchronization/Doppler literature. | Physical impairment claim only. |
| CFO materially changes B4 aggregate selection boundary | NOT_YET_SUPPORTED | Stress evidence establishes impairment relevance, not general decision-boundary importance. | Do not infer aggregate decision importance from stress curves alone. |
| Interference materially changes B4 aggregate selection boundary | PARTIALLY_SUPPORTED | Mismatch experiments expose strong degradation/failure boundaries, but do not establish universal boundary dominance. | Scope to tested mismatch banks. |
| 256 robust draws are sufficient as a universal guarantee | DO_NOT_CLAIM | Calibration disagreement is 0.0833% in the tested bank, but finite empirical calibration is not a theorem. | Call 256 draws empirically well calibrated for this experiment. |
| 32 robust draws can confidence-qualify the declared target | DO_NOT_CLAIM | Target is unattainable under the declared finite-draw confidence treatment. | State explicitly when discussing calibration. |
| The method provides real-world/hardware validation | DO_NOT_CLAIM | Evidence is model-based simulation; external measurements are literature evidence only. | State simulation explicitly. |
| The method is real-time | DO_NOT_CLAIM | Latest B4 median runtime is 138.89 ms at 256 draws and 272.81 ms at 512 on GitHub Actions; 256-draw p95 is 279.71 ms. | Report prototype runtime only; no embedded/hard-real-time claim. |
| Robust/chance-constrained ISAC is novel | DO_NOT_CLAIM | Established literature. | Novelty must be narrower. |
| Adaptive ISAC waveform selection is novel | DO_NOT_CLAIM | Established/recent literature. | Avoid first-of-kind wording. |
| PC-FMCW-specific physics-gated probabilistic profile selection is comparatively underexplored | PARTIALLY_SUPPORTED | Literature audit did not identify the same ordered formulation; categorical priority is not established. | Say 'comparatively underexplored' / 'to the best of our review'. |
| The reported empirical Pareto set is globally optimal | DO_NOT_CLAIM | Six of eight realized selected points are non-dominated only within the realized B4-selected sample. | Call it an empirical Pareto partition. |
| Frozen E9 raw-mean flags are 95% reliability guarantees | DO_NOT_CLAIM | Flags are based on empirical means, not confidence lower bounds. | Call them sampled operating-region characterization. |
| Normalized resource cost is physical energy | DO_NOT_CLAIM | It is an experiment-defined dimensionless metric. | Call it normalized resource cost. |
| Packet-level PER is established | DO_NOT_CLAIM | PER is not independently estimated by the receiver model and no packet model is declared. | Do not derive/report PER from BER alone. |

## Highest-confidence paper claim

> Under the declared simulation uncertainty model, robust PC-FMCW adaptation selects a substantially smaller operating subset than deterministic adaptation, but the accepted subset exhibits high confidence-qualified conditional joint sensing/communication reliability. The resulting contribution is a reliability-availability-resource/complexity operating-region characterization, not universal unconditional superiority.

## Completed supplemental evidence

Reviewer-grade run `34696063382` completed all required experiments and its fail-closed submission gate passed. The aggregate scientific verdict explicitly rejects universal B4 superiority and hardware-validation claims. On 1,200 paired supplemental units, the unconditional B4-B3 joint-QoS difference is -0.03667 with 95% bootstrap CI [-0.04833,-0.02583]. B4 selects 12.5% versus B3's 20.0%; conditional joint QoS is 100% for B4 with Wilson lower 95% bound 98.23%, versus 80.83% for B3.

Finite-draw calibration disagreement relative to the high-draw reference is 0.583% at 64 draws, 0.333% at 128, 0.0833% at 256, and 0% at 512 in the tested bank. Latest B4 median runtimes are 36.29, 70.47, 138.89, and 272.81 ms at 64, 128, 256, and 512 draws, respectively.

## Evidence hierarchy

1. Analytical identities and physical invariants.
2. Controlled waveform/receiver simulation validation.
3. Frozen receiver-level Monte Carlo evidence.
4. Confidence-qualified statistical summaries.
5. Completed reviewer-grade supplemental sensitivity, mismatch, calibration, distribution-shift, and runtime evidence.
6. External literature measurements used only to ground assumptions/impairment ranges.

No item in this hierarchy is a new RF hardware measurement by this project.
