# Claim Audit

Date: 2026-09-12
Evidence base: frozen publication v2.1 simulation artifacts, completed reviewer-grade supplemental run 34696063382, and literature audit.

| Claim | Status | Evidence / reason | Required wording |
|---|---|---|---|
| PC-FMCW supports joint sensing and communication | SUPPORTED | Established prior PC-FMCW literature; not novel here. | Background only. |
| The repository separates one-way communication from monostatic two-way sensing | SUPPORTED | Explicit system-model design and repository documentation. | Methodological correctness claim. |
| Physics gating prevents use of profiles outside declared FMCW capability | SUPPORTED | Architectural mechanism plus completed gate ablation. | Do not call it a guarantee beyond modeled constraints. |
| B4 achieves very high conditional joint QoS on selected frozen states | SUPPORTED | 1468/1468 selected successes; one-sided 95% Wilson lower bound 0.99816. | Always report selection/abstention simultaneously. |
| B4 achieves very high conditional joint QoS on the supplemental full-metric bank | SUPPORTED | 150/150 selected successes; Wilson lower 95% = 0.98228. | Scope to the tested bank and declared uncertainty model. |
| B4 improves unconditional joint QoS over B3 | DO_NOT_CLAIM | Frozen paired difference -0.03942, 95% CI [-0.04292,-0.03600]; supplemental paired difference -0.03667, 95% CI [-0.04833,-0.02583]. | Report as a reproducible negative result. |
| B4 universally outperforms B0/B3 | DO_NOT_CLAIM | Frozen and supplemental unconditional results contradict this. | Use reliability–availability trade-off framing. |
| State uncertainty contracts the robust selectable region | SUPPORTED | Supplemental sweep: B4 selection falls from 16.67% at scale 0 to 5.92% at scale 3 while conditional reliability remains high until the confidence-qualified boundary fails at scale 3. | Scope claim to tested uncertainty scales/state bank. |
| CFO is physically relevant to PC-FMCW communication | SUPPORTED | Communication stress validation and prior synchronization/Doppler literature. | Physical impairment claim only. |
| CFO materially changes B4 aggregate selection boundary | NOT_YET_SUPPORTED | Aggregate ablation does not establish a general boundary shift. | Do not infer decision importance from stress curves alone. |
| Interference materially changes B4 aggregate selection boundary | NOT_YET_SUPPORTED | Aggregate ablation does not establish a general boundary shift. | Needs boundary-focused study. |
| Moderate model mismatch can favor B4 conditional reliability | SUPPORTED | Tested CFO, Doppler, and moderate-interference mismatch banks favor B4. | Explicitly pair with severe-mismatch failure cases and tested-bank scope. |
| B4 is robust to arbitrary distribution shift | DO_NOT_CLAIM | Distribution-shift banks retain negative unconditional B4-B3 effects and only cover declared shifts. | Say robustness was evaluated for specific tested shifts only. |
| 256 Monte-Carlo draws are sufficient as a universal guarantee | DO_NOT_CLAIM | Calibration against 4096 draws shows 0.083% observed decision disagreement on the tested bank; this is empirical calibration, not a theorem. | Report finite-bank calibration and reference-draw protocol. |
| 32 robust draws satisfy the declared confidence target | DO_NOT_CLAIM | The acceptance target is not attainable at 32 draws in the completed calibration. | Do not use 32 draws for confidence-qualified final claims. |
| The method provides real-world/hardware validation | DO_NOT_CLAIM | Evidence is model-based simulation; external measurements are literature evidence only. | State simulation explicitly. |
| The method is real-time | DO_NOT_CLAIM | At 256 draws, measured prototype median latency is 138.89 ms and p95 is 279.71 ms on GitHub Actions; 512-draw median is 272.81 ms. | Report measured prototype timing only; no hard real-time claim. |
| Robust/chance-constrained ISAC is novel | DO_NOT_CLAIM | Established literature. | Novelty must be narrower. |
| Adaptive ISAC waveform selection is novel | DO_NOT_CLAIM | Established/recent literature. | Avoid first-of-kind wording. |
| PC-FMCW-specific physics-gated probabilistic profile selection is comparatively underexplored | PARTIALLY_SUPPORTED | Current literature audit did not identify the same ordered formulation; categorical priority is not established. | Say 'comparatively underexplored' / 'to the best of our review'. |
| Frozen E9 raw-mean flags are 95% reliability guarantees | DO_NOT_CLAIM | Flags are based on empirical means, not confidence lower bounds. | Call them sampled operating-region characterization. |
| The empirical Pareto set proves global Pareto optimality | DO_NOT_CLAIM | Supplemental Pareto analysis covers realized B4-selected receiver-level operating points only. | Say empirical Pareto partition over observed selected points. |
| Normalized resource cost is physical energy | DO_NOT_CLAIM | It is an experiment-defined dimensionless metric. | Call it normalized resource cost. |

## Highest-confidence paper claim

> Under the declared simulation uncertainty model, robust PC-FMCW adaptation selects a substantially smaller operating subset than deterministic adaptation, but the accepted subset exhibits very high confidence-qualified conditional joint sensing/communication reliability. The completed supplemental evidence independently reproduces this reliability–availability trade-off while rejecting unconditional B4 superiority. The resulting contribution is a confidence-qualified reliability–availability–complexity operating-region characterization, not universal policy dominance.

## Reproducibility / statistical boundary

- Frozen primary claims remain tied to the frozen v2.1 benchmark; supplemental experiments strengthen interpretation but do not replace the frozen benchmark.
- Supplemental run 34696063382 completed all experiment jobs, the fail-closed submission gate, conservative verdict generation, artifact-driven figures/tables, and evidence-manifest assembly.
- Bootstrap intervals are paired where policy comparisons use common state/seed units.
- Wilson lower bounds qualify binomial conditional-reliability claims.
- Finite-draw calibration is empirical against a 4096-draw reference and must not be described as a universal convergence guarantee.
- Distribution-shift and mismatch claims are limited to the explicitly tested families and severities.

## Evidence hierarchy

1. Analytical identities and physical invariants.
2. Controlled waveform/receiver simulation validation.
3. Frozen receiver-level Monte Carlo evidence.
4. Confidence-qualified statistical summaries.
5. Completed reviewer-grade supplemental evidence and sensitivity analyses.
6. External literature measurements used only to ground assumptions/impairment ranges.

No item in this hierarchy is a new RF hardware measurement by this project.
