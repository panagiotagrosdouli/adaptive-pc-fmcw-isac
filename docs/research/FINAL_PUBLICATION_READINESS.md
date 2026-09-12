# Publication-Readiness Audit

Date: 2026-09-12

## Current status

**REVALIDATION REQUIRED — DO NOT SUBMIT THIS SNAPSHOT AS FINAL YET.**

A source-provenance/model audit found that the Texas Instruments parking profile reports **858 MHz valid sweep bandwidth** and **40 MHz/us programmed chirp slope** as separate quantities. Earlier repository code inferred the short-range chirp slope as `858 MHz / 25.6 us`, which is not the source-reported slope. The corrected model uses 858 MHz for range resolution and 40 MHz/us for beat-frequency/range-support calculations, giving approximately 18.74 m positive-IF support instead of the earlier 22.36 m value.

The correction is scientifically material to the physical-feasibility map. Therefore no historical evidence run is silently relabeled as post-correction evidence.

## Historical evidence state

The previously completed reviewer-grade supplemental evidence is GitHub Actions run `34696063382` at source commit `37958fdca328e4434ca670cf667e33719edced44`, with aggregate artifact digest `sha256:0e9d21d5964e23bd5ed9eae25dfd58c8d8d557968ba7e6d7d2256e7e66055169`.

That run remains a reproducible **historical/pre-correction evidence instance**. It must not be described as the final evidence for the corrected source model.

Historical central results included:

- supplemental B3 selection 20.0% and conditional joint QoS 80.83%;
- supplemental B4 selection 12.5% and observed conditional joint QoS 100%, one-sided 95% Wilson lower bound 98.23%;
- paired B4-B3 unconditional difference -0.03667, 95% paired-bootstrap interval [-0.04833, -0.02583];
- historical B4 runtime at 256 draws: median 138.89 ms and p95 279.71 ms.

These values remain documented for provenance but are not automatically assumed to survive the corrected model.

## Corrected-model validation requirement

Before restoring a final publication-readiness verdict, all of the following must pass on the corrected source model:

1. general CI and physical-invariant regression tests;
2. the 1000-seed frozen publication-v2.1 benchmark as a new evidence instance;
3. the complete reviewer-grade supplemental suite and fail-closed evidence gate;
4. regenerated statistics/tables/narrative from the corrected evidence;
5. a manuscript LaTeX audit and visual PDF inspection matching the corrected source commit.

If any primary or supplemental statistic changes, the manuscript must report the corrected value rather than preserving an earlier number for consistency.

## Claim boundaries that remain unchanged

Regardless of numerical revalidation outcome, the project does not support:

- universal or unconditional B4 superiority;
- RF/hardware validation by this project;
- global Pareto optimality;
- arbitrary-mismatch or arbitrary-distribution robustness;
- embedded/hard-real-time readiness;
- physical-energy interpretation of normalized resource cost;
- packet-level PER without a declared packet model;
- categorical first-of-kind claims for PC-FMCW, generic ISAC, chance constraints, or adaptive waveform selection.

The intended contribution remains a confidence-qualified reliability--availability--complexity characterization of a finite, physics-gated PC-FMCW operating region under a declared simulation model.

## Evidence class

Simulation/analytical evidence only. External hardware measurements and specifications are literature/source provenance, not measurements produced by this repository.

## Publication decision

**PENDING CORRECTED-MODEL REVALIDATION.** A final `READY WITH CLAIM BOUNDARIES` decision may be restored only after the corrected frozen and supplemental evidence, CI, manuscript audit, and final source archive all agree on one canonical commit.
