# Part B Scientific Research Audit

Date: 2026-09-12

## Scope

This audit evaluates whether the repository satisfies the Part B requirement to propose and scientifically evaluate a technique, method, or scheme that improves a defined system-performance dimension.

The method is **Physics-Gated Reliability-Constrained Adaptive PC-FMCW ISAC**. The project is a model-based 77-GHz RF/mmWave vehicular PC-FMCW PHY study. It contains no new RF/OTA hardware measurements and must not describe simulation outputs as measured hardware performance.

## Current scientific status

The repository implements:

- separate one-way communication and monostatic two-way sensing paths;
- a dechirped-IF FMCW sensing model;
- a source-grounded TI parking-style profile and a separately identified composite high-mobility capability profile;
- deterministic physical-feasibility gating;
- a finite PHY action set;
- B0/B1/B2/B3/B4 policies plus a non-deployable hindsight Oracle;
- uncertainty-aware B4 selection with one-sided Wilson confidence treatment;
- paired Monte Carlo comparison and paired bootstrap intervals;
- waveform/receiver sanity tests, mismatch studies, uncertainty sweeps, ablations, finite-draw calibration, physical-resource reporting, and runtime measurements;
- CI, manuscript compilation checks, artifact provenance, and machine-readable evidence gates.

## Source-model correction under revalidation

A final source audit found that the Texas Instruments parking reference reports **858 MHz valid sweep bandwidth** and **40 MHz/us programmed chirp slope** separately. Earlier code inferred slope as `858 MHz / 25.6 us`. The corrected implementation uses the source-reported 40 MHz/us slope for beat-frequency/range-support calculations and the 858 MHz valid sweep for `c/(2B)` range resolution.

The corrected short-range positive-IF support is approximately **18.74 m**, not 22.36 m. Because physical feasibility is part of the policy evaluation path, frozen and supplemental evidence are being rerun as distinct corrected-model evidence instances. Historical numerical results remain immutable provenance but are not automatically promoted to final corrected-model claims.

## Scientifically supported interpretation

Historical evidence establishes that the robust B4 policy was more conservative than deterministic B3: it selected fewer states but achieved higher conditional joint sensing/communication reliability on its selected subset. Historical paired unconditional comparisons were negative for B4 versus B3, so the work does not support unconditional or universal B4 superiority.

The scientifically appropriate framing is a **reliability--availability--complexity trade-off**. The corrected-model reruns must confirm the final numerical magnitudes before those statistics are used in a submission.

## Negative results and boundaries that must remain visible

- Universal or unconditional B4 superiority is unsupported.
- Severe mismatch can defeat the robust policy.
- Confidence-qualified reliability can fail even when a raw empirical success rate remains high.
- The unoptimized Python implementation is not an embedded real-time controller.
- The high-mobility profile is a composite capability reference, not a commercial preset.
- The normalized resource cost is dimensionless and is not physical energy.
- Packet-level PER is **not** established because the receiver model does not declare an independent packet/error model. PER must not be inferred from BER alone.
- No RF/hardware validation is provided by this project.

## Metrics that are scientifically valid for this model

The final evidence package should consolidate, where applicable:

- BER and effective communication rate;
- range and velocity error/RMSE;
- joint QoS;
- selection, abstention, and physical-infeasibility rates;
- profile/action-selection frequencies;
- confidence bounds and paired policy differences;
- physical resource coordinates / dimensionless normalized cost;
- runtime measured on the declared host environment.

**PER is intentionally excluded unless a packet model is explicitly introduced and validated in a future study.**

## Remaining publication gate

Before calling the corrected work final, require:

1. passing CI and physical-invariant regression tests;
2. a corrected 1000-seed frozen benchmark tied to an exact commit/run;
3. a corrected complete reviewer-grade supplemental suite with fail-closed evidence gate;
4. regenerated manuscript tables/narrative from those exact artifacts;
5. confidence-qualified statistical summaries with paired units where comparisons are paired;
6. a verified bibliography and conservative novelty positioning;
7. a passing LaTeX audit and visual PDF inspection;
8. immutable artifact/run provenance plus checksums;
9. a final source/reproducibility archive tied to one canonical `main` commit.

## Part B suitability

**Yes, conditional on the corrected-model revalidation for the final reported numbers.** The methodology, baselines, physical gate, uncertainty treatment, statistical comparison, negative-result retention, and reproducibility infrastructure are sufficient for a strong simulation-based Part B research contribution. The correct performance-improvement claim concerns conditional reliability on selected operating states and must always be paired with its availability and computational costs.

## Publication-readiness verdict

**PENDING CORRECTED-MODEL REVALIDATION.** The project should not be described as final/submission-ready until the corrected frozen and supplemental runs, manuscript, PDF audit, and archival package all agree on the same corrected source model.
