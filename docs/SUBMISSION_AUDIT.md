# IEEE submission readiness audit

Status: manuscript content and literature positioning have undergone a deep 2026-09-30 audit. Source compilation and bibliography checks are enforced by repository CI; the newest literature-update commits must complete the same workflows before the package is considered frozen.

## Verified

- IEEEtran source compiles to a six-page PDF in CI.
- Final LaTeX pass has no unresolved citations or references.
- Material table overfull boxes were removed by the two-column table layout cleanup.
- `paper/supplemental_v2_1_tables.tex` is the correct root-level supplemental table input.
- `paper/final_results_discussion.tex` keeps the simulation/measurement claim boundary explicit.
- The short-range sensing statement is supported by `artifacts/stage7/pilot_validation.json`: range RMSE is about 7.4--8.0 m at -40 to -30 dB IF-SNR and about 0.021 m at -25 dB.
- The temporary `paper/.latex-audit-trigger` file is removed in this cleanup branch.

## Submission-time blockers / decisions

1. **Target venue must be fixed before final packaging.** The manuscript currently uses `\\documentclass[journal]{IEEEtran}`. Do not switch to `conference` unless the selected venue requires the IEEE conference template.
2. **Author metadata is intentionally anonymous.** Replace `Anonymous Author(s)` and the temporary internal `\\thanks{...}` text only when the venue's blind-review policy and author list are known.
3. **Deep scholarly positioning audit completed; final venue-level bibliography verification remains.** The 2026-09-30 audit now covers the closest recent PC-FMCW/FMCW ISAC, synchronization, adaptive waveform, and robust-ISAC papers, including Temiz et al. TCOM 2026 and Wang et al. TSP 2024. Before submission, re-check publisher metadata and venue formatting for every cited entry.
4. **Final PDF compliance must be checked with the venue-prescribed IEEE tool.** Use IEEE LaTeX Analyzer for source validation and IEEE PDF Checker/PDF eXpress when required by the venue. Confirm embedded/subset fonts, permitted PDF version, no security restrictions, and venue-specific metadata.
5. **Final source ZIP should contain only files actually required by `manuscript_v2_1.tex` plus the bibliography and any figures.** Do not include CI trigger files, build products, logs, repository artifacts, or reviewer-only working files unless the venue requests them.

## Minimal current source set

- `paper/manuscript_v2_1.tex`
- `paper/final_abstract_conclusion_abstract_only.tex`
- `paper/final_abstract_conclusion_conclusion_only.tex`
- `paper/results_v2_1_tables.tex`
- `paper/supplemental_v2_1_tables.tex`
- `paper/final_results_discussion.tex`
- `paper/references_v2_1.bib`

No figures are currently required by the integrated manuscript source.

## Literature audit provenance

- Deep audit: `docs/research/DEEP_LITERATURE_AUDIT_2026-09-30.md`
- Final verdict: `docs/research/FINAL_LITERATURE_VERDICT.md`
- Claim rule: do not use universal first-of-kind wording; position the contribution as the admissibility-first, confidence-qualified PC-FMCW operating-region architecture.
