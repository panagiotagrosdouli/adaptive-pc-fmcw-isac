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

### 2026-09-13 — Add repository/evidence/policy/reproducibility audits

- **Files:** `docs/REPOSITORY_RESEARCH_MAP.md`, `docs/EVIDENCE_MAP.md`, `docs/POLICY_DEFINITIONS.md`, `docs/REPRODUCIBILITY.md`, `docs/EQUATION_TO_CODE_AUDIT.md`.
- **Type:** documentation / reproducibility / scientific audit.
- **Reason:** map architecture, evidence classes, policy semantics, and code-to-equation provenance before submission.
- **Frozen results affected:** no.
- **Experiments rerun required:** no.

### 2026-09-13 — Add paper claim and reviewer audit files

- **Files:** `paper/CLAIM_AUDIT.md`, `paper/EXCLUDED_UNVERIFIED_CLAIMS.md`, `paper/REVIEWER_DEFENSE.md`, `paper/SOURCE_TO_CLAIM_TRACEABILITY.md`.
- **Type:** manuscript support / claim discipline.
- **Reason:** prevent unconditional-superiority, hardware-validation, global-Pareto, real-time, and other unsupported wording.
- **Frozen results affected:** no.
- **Experiments rerun required:** no.

### 2026-09-13 — Lock finite-draw confidence invariants

- **File:** `tests/test_statistics.py`.
- **Type:** test / statistical invariant.
- **Reason:** lock the one-sided Wilson publication semantics and structural certification thresholds for 32, 64, 128, 256, and 512 draws.
- **Frozen results affected:** no; test-only change.
- **Experiments rerun required:** no, but CI must pass.

### 2026-09-13 — Fresh literature audit and submission references

- **Files:** `paper/references_submission.bib`, `paper/literature_positioning.tex`, `paper/SUBMISSION_SOURCE_MANIFEST.txt`.
- **Type:** bibliography / scientific positioning.
- **Reason:** add independently verified recent vehicular-ISAC, robust-ISAC, confidence-interval, scenario-optimization, selective-prediction, and 3GPP sources.
- **Frozen results affected:** no.
- **Experiments rerun required:** no; LaTeX/bibliography audit required.

### 2026-09-13 — Expand IEEE methodology and correct stale manuscript evidence

- **Files:** `paper/manuscript_v2_1.tex`, `paper/final_abstract_conclusion_abstract_only.tex`, `paper/final_results_discussion.tex`, `paper/final_abstract_conclusion_conclusion_only.tex`, `README.md`.
- **Type:** manuscript / documentation.
- **Reason:** document actual 54-action construction, receiver semantics, dimensionless resource cost, one-sided Wilson rule, paired protocol, current literature context, and reproducibility. Correct stale 256-draw wording and obsolete runtime values so the abstract/results/conclusion agree with the frozen 512-draw protocol and final supplemental evidence.
- **Frozen results affected:** no; no numerical evidence artifacts were altered.
- **Experiments rerun required:** no; CI and manuscript compilation must pass before submission-ready status.
