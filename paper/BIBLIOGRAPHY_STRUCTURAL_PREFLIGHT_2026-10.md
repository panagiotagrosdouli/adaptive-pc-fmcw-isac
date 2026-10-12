# Bibliography structural preflight — 2026-10-12

Scope: exact repository branch preceding this note; not an external publisher/DOI verification.

- `paper/manuscript_v2_1.tex` has 40 literal citation tokens, with no missing keys against `references_v2_1.bib` + `references_submission.bib`.
- The journal uses 12 and 23 bibliography entries respectively; no duplicate BibTeX keys across that combined pair.
- `paper/radarconf2027_physics_gate.tex` has 28 literal citation tokens, with no missing keys against 17 entries in `paper1_references.bib`.
- Keys shared *across the separate papers* are expected references to common prior work, not automatically a conflict. Bibliography compilation was independently validated in successful GitHub workflows on commit `9a149e5c98432922ee12e25347bfb5191d4fdd1b`.
- This static scan covers literal `\\cite{...}` syntax, not all possible citation macros or included manuscript fragments.

**Still open:** Crossref/IEEE Xplore publisher checks for each DOI, title, authors, dates, venues, volume/page metadata; literature novelty assessment; explicit textual/figure reuse audit; venue originality and disclosure compliance. None of these was certified by the structural scan.

Checklists are intentionally conservative. Do not alter frozen scientific data or interpret a passing LaTeX build as publisher verification.
