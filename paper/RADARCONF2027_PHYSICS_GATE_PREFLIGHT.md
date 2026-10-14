# RadarConf 2027 physics-gate preflight — 2026-10-14

**Candidate manuscript:** `paper/radarconf2027_physics_gate.tex`. This document is not an approval for upload. No frozen publication-v2.1 results were modified.

## Checks performed
- Confirmed `conference,a4paper` IEEEtran source format.
- Static scan: abstract contains 87 whitespace-delimited words (conference portal limit: 100; enter the appropriate final abstract in portal).
- Static scan: 28 citation uses, 16 unique citation keys, all found among 17 bibliography entries in `paper1_references.bib`. This does not verify DOI/publisher metadata.
- The author block includes `Affiliation and contact email to be verified before submission`, which **must be replaced with genuine author-supplied details**.
- The old frozen Paper 1 results (132 supportable / 238; 114 invalid ungated among supportable states) are unchanged.
- The post-freeze diagnostic identifies five potentially misclassified grid states when signed combined beat frequency is enforced under the declared ±Fs/2 diagnostic convention (132 to 127). This is **not** a validated replacement for the original experiment or manuscript statistics.

## Release blockers
1. Validate complex-IF / positive-IF passband convention and radar receiver processing at the coupled R/v boundary; perform a separate, versioned replay and decide which results the conference should report. Do not keep 132 and 114 if they no longer describe the accepted model.
2. Compile the exact candidate SHA and confirm 3–6 pages, no undefined citations/labels, and manually inspect every rendered PDF page and embedded fonts.
3. Verify each referenced publication DOI, title, authors, date and venue from publisher sources. Static key completeness is insufficient.
4. Confirm the official venue rules, originality and overlap requirements, and author/coauthor declarations.
5. Add verified author institution, department, email, and any coauthors. Never invent them.
6. Package the complete publisher-specific TeX source including `radarconf2027_physics_gate.tex`, `paper1_figures.tex`, `paper1_gate_ablation_section.tex`, `paper1_physics_gate_ablation_table.tex`, `paper1_physics_gate_ablation_figure.tex`, `paper1_references.bib`, and referenced assets. Verify all transitive input and figure dependencies on the final SHA.
7. Do not upload, merge, or certify submission-ready before a final independent review.

## Official primary venue links
- https://radarconf2027.org/paper-submission/
- https://ieee-aess.org/event/conference/2027-ieee-radar-conference

**Deadline:** October 31, 2026 (reconfirm just before final upload).

### Reproduction notes
`python scripts/check_combined_if_grid.py` computes the supplementary grid census.
`pytest -q tests/test_combined_if_feasibility_diagnostic.py` checks selected cases.
The source/PR CI must pass on the final commit, not an ancestor; earlier CI passes are not a proxy.
