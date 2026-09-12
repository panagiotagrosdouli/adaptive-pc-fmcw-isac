# Claim Audit

Date: 2026-09-12

## Audit status

A source-model correction is under revalidation. Historical frozen/supplemental statistics below remain valid descriptions of their original evidence instances, but they must not be presented as final corrected-model statistics until the new frozen and supplemental runs complete and their artifacts are audited.

The correction separates the Texas Instruments parking profile's 858 MHz valid sweep bandwidth from its independently specified 40 MHz/us programmed chirp slope. This changes the modeled short-range positive-IF range support from the earlier 22.36 m value to approximately 18.74 m.

| Claim | Status | Evidence / reason | Required wording |
|---|---|---|---|
| PC-FMCW supports joint sensing and communication | SUPPORTED | Established prior PC-FMCW literature; not novel here. | Background only. |
| The repository separates one-way communication from monostatic two-way sensing | SUPPORTED | Explicit system-model design and repository documentation. | Methodological correctness claim. |
| The corrected TI short-range profile uses 858 MHz valid sweep and 40 MHz/us programmed slope | SUPPORTED | Texas Instruments TIDEP-01011 / TIDUEO9 source parameters; regression-tested implementation. | Keep bandwidth and slope semantically separate. |
| Corrected short-range positive-IF support is approximately 18.74 m at 10 MSPS | SUPPORTED | `c Fs/(4 mu)` with source-reported `mu=40 MHz/us`. | Do not reintroduce 22.36 m. |
| Physics gating prevents use of profiles outside declared modeled FMCW capability | SUPPORTED | Architectural mechanism and physical-invariant tests. | Do not call it a guarantee beyond modeled constraints. |
| B4 achieved 1468/1468 selected successes in the historical frozen run | HISTORICAL_SUPPORTED | Original frozen evidence; one-sided 95% Wilson lower bound 0.99816. | Identify as historical until corrected rerun is compared. |
| B4 achieved 150/150 selected successes in historical supplemental run 34696063382 | HISTORICAL_SUPPORTED | Historical supplemental evidence; Wilson lower 95% = 0.98228. | Identify run/commit; do not silently transfer to corrected model. |
| B4 improves unconditional joint QoS over B3 | DO_NOT_CLAIM | Historical frozen and supplemental paired differences are negative. | Report negative result; re-check corrected runs. |
| B4 universally outperforms B0/B3 | DO_NOT_CLAIM | Existing evidence contradicts this. | Use reliability--availability trade-off framing. |
| State uncertainty contracts the robust selectable region | HISTORICAL_SUPPORTED_PENDING_REVALIDATION | Historical supplemental sweep shows contraction; corrected supplemental suite is required. | Scope to exact run and tested state bank. |
| CFO is physically relevant to PC-FMCW communication | SUPPORTED | Communication stress validation and prior synchronization/Doppler literature. | Physical impairment claim only. |
| CFO materially changes B4 aggregate selection boundary | NOT_YET_SUPPORTED | Aggregate ablation does not establish a general boundary shift. | Do not infer decision importance from stress curves alone. |
| Interference materially changes B4 aggregate selection boundary | NOT_YET_SUPPORTED | Aggregate ablation does not establish a general boundary shift. | Needs boundary-focused study. |
| Moderate model mismatch can favor B4 conditional reliability | HISTORICAL_SUPPORTED_PENDING_REVALIDATION | Historical tested CFO, Doppler, and moderate-interference banks favored B4. | Pair with severe-mismatch failure cases and exact run scope. |
| B4 is robust to arbitrary distribution shift | DO_NOT_CLAIM | Tested shifts cannot establish arbitrary-distribution robustness. | Scope robustness to specific tested shifts only. |
| 256 Monte-Carlo draws are sufficient as a universal guarantee | DO_NOT_CLAIM | Historical calibration is empirical, not a theorem. | Report finite-bank calibration and reference-draw protocol. |
| 32 robust draws satisfy the declared confidence target | DO_NOT_CLAIM | Historical acceptance rule could not attain the target at 32 draws. | Do not use 32 draws for confidence-qualified final claims. |
| The method provides real-world/hardware validation | DO_NOT_CLAIM | Evidence is model-based simulation; external measurements are literature evidence only. | State simulation explicitly. |
| The method is real-time | DO_NOT_CLAIM | Historical host timings are far from an embedded certification and were measured on GitHub Actions. | Report host runtime only. |
| Robust/chance-constrained ISAC is novel | DO_NOT_CLAIM | Established literature. | Novelty must be narrower. |
| Adaptive ISAC waveform selection is novel | DO_NOT_CLAIM | Established/recent literature. | Avoid first-of-kind wording. |
| PC-FMCW-specific physics-gated probabilistic profile selection is comparatively underexplored | PARTIALLY_SUPPORTED | Verified literature audit did not identify the same complete composition; categorical priority is not established. | Use cautious comparative wording only. |
| Frozen E9 raw-mean flags are 95% reliability guarantees | DO_NOT_CLAIM | Raw flags are empirical means, not confidence lower bounds. | Call them sampled operating-region characterization. |
| The empirical Pareto set proves global Pareto optimality | DO_NOT_CLAIM | Pareto analysis covers realized selected operating points only. | Say empirical Pareto partition over observed selected points. |
| Normalized resource cost is physical energy | DO_NOT_CLAIM | It is an experiment-defined dimensionless metric. | Call it normalized resource cost. |
| Packet-level PER is established | DO_NOT_CLAIM | The receiver model does not independently estimate PER and no packet model is declared. | Do not infer packet-level PER from BER alone. |

## Current highest-confidence claim

> The corrected implementation enforces source-grounded PC-FMCW physical-capability limits before stochastic selection. Historical evidence supports a reliability--availability trade-off for robust adaptation, but the final quantitative claim set is intentionally pending fresh frozen and supplemental evidence on the corrected source model.

## Reproducibility boundary

- Historical frozen and supplemental runs remain immutable provenance records.
- Corrected-model reruns are distinct evidence instances and require their own commit SHA, run ID, artifact digest, seed ranges, robust-draw counts, bootstrap resamples, and confidence-bound method.
- Paired comparisons must retain common state/seed units.
- Wilson lower bounds qualify binomial conditional-reliability claims.
- Finite-draw calibration remains empirical against a declared reference-draw protocol.
- Distribution-shift and mismatch claims remain limited to explicitly tested families and severities.

## Evidence hierarchy

1. Analytical identities and source-grounded physical invariants.
2. Controlled waveform/receiver simulation validation.
3. Receiver-level Monte Carlo evidence tied to an exact commit/run.
4. Confidence-qualified statistical summaries.
5. Supplemental sensitivity, mismatch, calibration, and runtime evidence.
6. External literature measurements/specifications used only to ground assumptions and provenance.

No item in this hierarchy is a new RF hardware measurement by this project.
