# IEEE submission readiness audit

Status: source compiles reproducibly under the repository Manuscript LaTeX Audit, with bibliography resolution and table-overflow checks already passing on the current manuscript line.

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
3. **Reference coverage needs a venue-level scholarly audit.** The current bibliography contains four core provenance/positioning references. Compilation is clean, but bibliographic completeness is a scientific-review issue rather than a LaTeX-validity issue.
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
