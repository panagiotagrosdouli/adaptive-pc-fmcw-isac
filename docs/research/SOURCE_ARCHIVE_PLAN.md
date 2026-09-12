# Submission Source Archive Plan

The final editable submission archive should be generated only after all manuscript consistency fixes are merged. Its canonical source is the `main` commit that passes both CI and the Manuscript LaTeX Audit.

Required paper sources are exactly those declared in `paper/SUBMISSION_SOURCE_MANIFEST.txt`. The archive should also include the compiled PDF/log from the matching LaTeX audit, `docs/research/FINAL_PUBLICATION_READINESS.md`, `docs/research/CLAIM_AUDIT.md`, this runtime provenance note, and a machine-readable provenance/checksum record.

Supplemental evidence must remain identified separately from the frozen primary benchmark. The completed reviewer-grade evidence is run `34696063382` at source commit `37958fdca328e4434ca670cf667e33719edced44`; aggregate evidence artifact SHA-256 is `0e9d21d5964e23bd5ed9eae25dfd58c8d8d557968ba7e6d7d2256e7e66055169`.

Do not silently substitute rerun results into a submission archive. Any future evidence rerun is a distinct evidence instance and must carry its own run id, commit, artifact digests, and regenerated manuscript consistency audit.
