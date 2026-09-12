# Claim Audit

Date: 2026-09-12
Evidence base: frozen publication v2.1 simulation artifacts plus literature audit.

| Claim | Status | Evidence / reason | Required wording |
|---|---|---|---|
| PC-FMCW supports joint sensing and communication | SUPPORTED | Established prior PC-FMCW literature; not novel here. | Background only. |
| The repository separates one-way communication from monostatic two-way sensing | SUPPORTED | Explicit system-model design and repository documentation. | Methodological correctness claim. |
| Physics gating prevents use of profiles outside declared FMCW capability | SUPPORTED | Architectural mechanism; final importance depends on gate ablation. | Do not call it a guarantee beyond modeled constraints. |
| B4 achieves very high conditional joint QoS on selected frozen states | SUPPORTED | 1468/1468 selected successes; one-sided 95% Wilson lower bound 0.99816. | Always report selection/abstention simultaneously. |
| B4 improves unconditional joint QoS over B3 | DO_NOT_CLAIM | Paired difference -0.03942, 95% CI [-0.04292,-0.03600]. | Report as negative result. |
| B4 universally outperforms B0/B3 | DO_NOT_CLAIM | Frozen unconditional results contradict this. | Use reliability–availability trade-off framing. |
| State uncertainty contracts the robust selectable region | SUPPORTED | E11: 12.5% full B4 vs 16.67% without state uncertainty in frozen slice. | Scope claim to tested state set until broader sweep confirms. |
| CFO is physically relevant to PC-FMCW communication | SUPPORTED | Communication stress validation and prior synchronization/Doppler literature. | Physical impairment claim only. |
| CFO materially changes B4 aggregate selection boundary | NOT_YET_SUPPORTED | E11 no-CFO aggregate equals full B4 in tested slice. | Do not infer decision importance from stress curves alone. |
| Interference materially changes B4 aggregate selection boundary | NOT_YET_SUPPORTED | E11 no-interference aggregate equals full B4 in tested slice. | Needs boundary-focused study. |
| The method provides real-world/hardware validation | DO_NOT_CLAIM | Evidence is model-based simulation; external measurements are literature evidence only. | State simulation explicitly. |
| The method is real-time | NOT_YET_SUPPORTED | Requires measured online decision timing under final implementation. | Use only measured runtime statements. |
| Robust/chance-constrained ISAC is novel | DO_NOT_CLAIM | Established literature. | Novelty must be narrower. |
| Adaptive ISAC waveform selection is novel | DO_NOT_CLAIM | Established/recent literature. | Avoid first-of-kind wording. |
| PC-FMCW-specific physics-gated probabilistic profile selection is comparatively underexplored | PARTIALLY_SUPPORTED | Current literature audit did not identify the same ordered formulation; categorical priority is not established. | Say 'comparatively underexplored' / 'to the best of our review'. |
| Frozen E9 raw-mean flags are 95% reliability guarantees | DO_NOT_CLAIM | Flags are based on empirical means, not confidence lower bounds. | Call them sampled operating-region characterization. |
| Normalized resource cost is physical energy | DO_NOT_CLAIM | It is an experiment-defined dimensionless metric. | Call it normalized resource cost. |

## Highest-confidence paper claim

> Under the declared simulation uncertainty model, robust PC-FMCW adaptation selects a substantially smaller operating subset than deterministic adaptation, but the accepted subset exhibits very high confidence-qualified conditional joint sensing/communication reliability. The resulting contribution is a reliability–availability–resource operating-region characterization, not universal unconditional superiority.

## Evidence hierarchy

1. Analytical identities and physical invariants.
2. Controlled waveform/receiver simulation validation.
3. Frozen receiver-level Monte Carlo evidence.
4. Confidence-qualified statistical summaries.
5. External literature measurements used only to ground assumptions/impairment ranges.

No item in this hierarchy is a new RF hardware measurement by this project.
