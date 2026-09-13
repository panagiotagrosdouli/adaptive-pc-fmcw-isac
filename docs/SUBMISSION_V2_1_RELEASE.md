# Submission v2.1 Release Record

This document records the release-facing state of the PC-FMCW ISAC repository after the full repository audit and repair pass.

## Scientific baseline

Frozen publication baseline commit:

`3904c4c2a69c4af96751d64614f7228ddea24b56`

The frozen publication evidence under `artifacts/publication/v2_1/` is preserved as historical scientific evidence and is not rewritten by the submission-packaging layer.

## Audited repository state

The full-repository audit/repair PR was merged to `main` as:

`f63740b706cb0c83bcf9009fce460fb4e1ff50f3`

That merge contains the repository-wide scientific, provenance, workflow, documentation, and manuscript repairs performed after the frozen baseline.

## Submission package scope

The generated submission bundle contains:

- compiled IEEE manuscript PDF;
- manuscript LaTeX and bibliography sources;
- source manifest and source-to-claim traceability;
- figure provenance, claim audit, reviewer defense, and excluded-claim register;
- frozen publication-v2.1 machine-readable evidence;
- frozen/supplemental publication tables and provenance stored under `artifacts/publication/v2_1/`;
- the frozen v2.1 protocol configuration;
- generated 54-action-space CSV;
- SHA-256 submission manifest;
- reproducibility and equation-to-code audit documentation;
- repository-level README, Makefile, and package metadata.

The bundle is intentionally not a replacement for the Git repository. The Git commit recorded in `artifacts/publication/submission/manifest.json` remains the authoritative source-code provenance pointer.

## Scientific claim boundary

This release is a simulation/analytical/statistical research package with host-runtime measurements. It is not a new RF hardware measurement campaign and does not certify embedded real-time operation.

The primary B4 claim is confidence-qualified reliability on the selected subset under the declared uncertainty model. The release does not claim unconditional superiority over B3, universal robustness, global Pareto optimality, or field reliability guarantees.

## Release validation gates

A release candidate is acceptable only when all of the following succeed on the same commit:

- `pytest -q`;
- 54-action export validation;
- SHA-256 submission manifest generation;
- full repository audit;
- Stage-7 validation smoke test;
- E1-E5 executable validation smoke test;
- E6-E12 paired-policy benchmark smoke test;
- full supplemental research-surface smoke test;
- IEEE LaTeX build;
- unresolved citation/reference check;
- duplicate-label check;
- visual inspection of the compiled manuscript;
- deterministic submission ZIP generation.

If any mandatory gate fails, the candidate must not be described as submission-ready.
