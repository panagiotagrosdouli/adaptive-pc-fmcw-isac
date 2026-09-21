# Paper 2 Evidence Manifest

| Manuscript element | Repository evidence | Evidence class |
|---|---|---|
| Frozen six-policy benchmark | `artifacts/publication/v2_1/FINAL_RESULTS.json` | frozen simulation/statistics |
| Frozen E9/E11 results | `artifacts/publication/v2_1/E9_E11_RESULTS.json` | frozen supplemental simulation |
| Frozen policy tables | `paper/results_v2_1_tables.tex` | generated from frozen JSON |
| Supplemental tables | `paper/supplemental_v2_1_tables.tex` | generated reviewer-grade evidence |
| Runtime / finite-draw / mismatch discussion | `paper/final_results_discussion.tex` | manuscript interpretation of supplemental evidence |
| System model and algorithms | `src/pcfmcw_isac/` and `paper/manuscript_v2_1.tex` | implementation + manuscript model |
| 77-GHz profile provenance | `configs/ti_77ghz_parking_profile.json`, `configs/ti_77ghz_high_mobility_capability_profile.json` | source-grounded/composite capability reference |
| Literature positioning | `paper/references_v2_1.bib`, `paper/references_submission.bib`, `paper/literature_positioning.tex` | peer-reviewed/standards literature |

## Claim boundary

All adaptive-controller results are simulation, analytical, statistical, or host-runtime evidence. No result in this manifest is an RF hardware measurement. Paper 2 does not replace the frozen benchmark with smoke runs or with the nested 4096-draw comparator.
