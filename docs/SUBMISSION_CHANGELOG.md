# Submission-Ready Changelog

Frozen scientific baseline: `3904c4c2a69c4af96751d64614f7228ddea24b56`.
Submission branch: `paper/submission-ready`.

This branch preserves the frozen publication-v2.1 evidence and records all post-freeze changes needed to make the repository easier to audit, reproduce, and submit.

## Rules

- Frozen evidence under `artifacts/publication/v2_1/` is not overwritten.
- Changes that would alter scientific outputs must be documented and must trigger regeneration of affected evidence before any result is called submission-ready.
- Documentation, manuscript, CI, and provenance changes that do not alter the underlying simulator are marked as non-result-changing.

## Changes

### 2026-09-13 — Initialize submission-ready branch

- **Files:** `docs/SUBMISSION_CHANGELOG.md`
- **Type:** documentation / provenance
- **Reason:** establish an auditable record of post-freeze work.
- **Frozen results affected:** no.
- **Experiments rerun required:** no.
