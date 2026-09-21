# Final Submission Snapshot

Date: 2026-09-12

## Canonical repository state

Canonical manuscript/source commit: `943f63cc0ea221cd90d411c578c0bb9578ccc3aa`.

Post-merge CI run `34714367508` completed successfully, including pytest, Stage 7 validation, E1--E5, E6--E12, the full supplemental research smoke test, and artifact upload.

The manuscript LaTeX audit used for the corrected runtime-table manuscript is run `34714168818`, artifact `manuscript-v2-1-pdf` (artifact id `10304781078`), generated from PR #54 head `56890661a0a7551f2ffd8d2497f533b8db4d89eb`. PR #54 was squash-merged as canonical commit `943f63cc0ea221cd90d411c578c0bb9578ccc3aa`; the merge contains the audited manuscript changes.

## Evidence provenance

Frozen publication-v2.1 primary results remain the primary benchmark and are not replaced by supplemental reruns.

Reviewer-grade supplemental evidence:

- Actions run: `34696063382`
- source commit: `37958fdca328e4434ca670cf667e33719edced44`
- aggregate evidence SHA-256: `0e9d21d5964e23bd5ed9eae25dfd58c8d8d557968ba7e6d7d2256e7e66055169`
- runtime artifact id: `10300013349`

Runtime values used by the manuscript are the completed-run medians: B4 36.292, 70.470, 138.886, and 272.810 ms at 64, 128, 256, and 512 robust draws. At 256 draws, B4 p95 is 279.712 ms. These are host-runtime measurements on GitHub Actions, not embedded-target timing.

## Claim boundary

Evidence class is controlled simulation/analytical evidence. This repository snapshot does not establish RF/hardware validation, hard-real-time readiness, universal B4 superiority, global Pareto optimality, arbitrary distributional robustness, physical-energy interpretation of normalized resource cost, or packet-level PER without a declared packet model.

The supported interpretation is a confidence-qualified reliability--availability--complexity trade-off over the declared finite PC-FMCW operating region.

## Archival policy

The editable submission sources are exactly those listed in `paper/SUBMISSION_SOURCE_MANIFEST.txt`. A submission archive should include those sources, the matching compiled PDF/build log, `FINAL_PUBLICATION_READINESS.md`, `CLAIM_AUDIT.md`, `RUNTIME_TABLE_PROVENANCE.md`, `SOURCE_ARCHIVE_PLAN.md`, provenance metadata, and SHA-256 checksums.

Future reruns are distinct evidence instances. They must not silently replace the run IDs, commits, statistics, or digests recorded here.

## Publication status

**READY WITH CLAIM BOUNDARIES.**
