# Submission Snapshot Status

Date: 2026-09-12

## Status

**RETIRED AS A FINAL SNAPSHOT — retained only as provenance of the pre-correction submission state.**

The previously recorded canonical source commit `943f63cc0ea221cd90d411c578c0bb9578ccc3aa`, post-merge CI run `34714367508`, and LaTeX audit run `34714168818` predate a later source-model correction to the Texas Instruments short-range chirp profile.

The correction separates the source-reported 858 MHz valid sweep bandwidth from the independently specified 40 MHz/us programmed chirp slope. The corrected positive-IF short-range support is approximately 18.74 m. Therefore the earlier snapshot must not be used as the final archival/submission record.

## Historical evidence retained for provenance

Historical reviewer-grade supplemental evidence:

- Actions run: `34696063382`
- source commit: `37958fdca328e4434ca670cf667e33719edced44`
- aggregate evidence SHA-256: `0e9d21d5964e23bd5ed9eae25dfd58c8d8d557968ba7e6d7d2256e7e66055169`
- runtime artifact id: `10300013349`

These identifiers remain useful as immutable provenance, but they are explicitly **pre-correction** evidence.

## Replacement requirements

A new final submission snapshot may be declared only after the corrected model has:

- passing general CI;
- a completed corrected 1000-seed frozen benchmark;
- a completed corrected reviewer-grade supplemental suite and fail-closed evidence gate;
- manuscript statistics/tables regenerated from those exact evidence instances;
- a passing LaTeX audit and visual PDF inspection;
- a source/reproducibility archive tied to the resulting canonical `main` commit.

The replacement snapshot must record exact run IDs, commit SHAs, artifact digests, source-manifest contents, and SHA-256 checksums. Historical values must not be silently substituted into the corrected snapshot.

## Permanent claim boundary

The project remains simulation/analytical evidence only and does not establish RF/hardware validation, universal B4 superiority, arbitrary-distribution robustness, global Pareto optimality, embedded/hard-real-time readiness, physical-energy interpretation of normalized resource cost, or packet-level PER without a declared packet model.
