# Submission-Ready Changelog

Frozen scientific baseline: `3904c4c2a69c4af96751d64614f7228ddea24b56`.

The original submission-readiness branch `paper/submission-ready` was merged into `main` by PR #57. Further audit/repair work is performed on review branches and must not rewrite frozen publication-v2.1 evidence.

## Rules

- Frozen evidence under `artifacts/publication/v2_1/` is not overwritten.
- Changes that alter scientific outputs must be documented and require regeneration under a new protocol/version before those outputs are used as publication evidence.
- Documentation, manuscript, CI, provenance, and diagnostic-output corrections that do not alter frozen evidence are recorded as post-freeze maintenance.

## Changes

### 2026-09-13 — Initialize submission-ready branch

- **File:** `docs/SUBMISSION_CHANGELOG.md`.
- **Type:** documentation / provenance.
- **Reason:** establish an auditable record of post-freeze work.
- **Frozen results affected:** no.

### 2026-09-13 — Add repository/evidence/policy/reproducibility audits

- **Files:** `docs/REPOSITORY_RESEARCH_MAP.md`, `docs/EVIDENCE_MAP.md`, `docs/POLICY_DEFINITIONS.md`, `docs/REPRODUCIBILITY.md`, `docs/EQUATION_TO_CODE_AUDIT.md`.
- **Type:** documentation / reproducibility / scientific audit.
- **Frozen results affected:** no.

### 2026-09-13 — Add paper claim and reviewer audit files

- **Files:** `paper/CLAIM_AUDIT.md`, `paper/EXCLUDED_UNVERIFIED_CLAIMS.md`, `paper/REVIEWER_DEFENSE.md`, `paper/SOURCE_TO_CLAIM_TRACEABILITY.md`.
- **Type:** manuscript support / claim discipline.
- **Frozen results affected:** no.

### 2026-09-13 — Lock finite-draw confidence invariants

- **File:** `tests/test_statistics.py`.
- **Type:** test / statistical invariant.
- **Reason:** lock the one-sided Wilson publication semantics and structural certification thresholds for 32, 64, 128, 256, and 512 draws.
- **Frozen results affected:** no.

### 2026-09-13 — Fresh literature audit and submission references

- **Files:** `paper/references_submission.bib`, `paper/literature_positioning.tex`, `paper/SUBMISSION_SOURCE_MANIFEST.txt`.
- **Type:** bibliography / scientific positioning.
- **Frozen results affected:** no.

### 2026-09-13 — Expand IEEE methodology and correct stale manuscript evidence

- **Files:** `paper/manuscript_v2_1.tex`, abstract/conclusion/result inputs, `README.md`.
- **Type:** manuscript / documentation.
- **Reason:** document the 54-action construction, receiver semantics, normalized resource cost, one-sided Wilson rule, paired protocol, and reproducibility; correct stale 256-draw wording and obsolete runtime values.
- **Frozen results affected:** no.

### 2026-09-13 — Merge submission-readiness work into main

- **PR:** #57.
- **Merge commit:** `8a2a3db302026759866a8c56ddd20d94550344d2`.
- **Type:** repository integration.
- **Frozen results affected:** no; `artifacts/publication/v2_1/` preserved.

### 2026-09-14 — Full-repository audit and repair pass

- **Branch:** `audit/full-repo-final`.
- **Type:** code / test / CI / provenance / documentation audit.
- **Changes:**
  - make the submission manifest fail instead of recording `UNKNOWN` commit provenance;
  - include generated action-space data, vector figure source, literature-positioning source, build inputs, and CI definitions in submission provenance;
  - add tests for manifest provenance requirements;
  - derive profile ADC occupancy from validated profile objects instead of hard-coded sample counts;
  - distinguish policy abstention from hard physical infeasibility in new v2.1 records through `any_physics_feasible_action` and `selection_status`;
  - add regression tests for the abstention/physics distinction;
  - add `scripts/audit_repository.py`, `make repo-audit`, and a mandatory CI repository-wide consistency gate;
  - refresh reproducibility documentation after PR #57 merge.
- **Frozen results affected:** no. Historical frozen JSON/CSV evidence is unchanged.
- **Experiments rerun required:** no for frozen evidence; smoke/unit/submission gates must pass on the repair branch before merge.
