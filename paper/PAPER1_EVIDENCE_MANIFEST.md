# Paper 1 Evidence Manifest

This manifest is intentionally independent from the Paper 2/v2.1 submission manifest.

| Manuscript element | Source | Evidence class |
|---|---|---|
| 77-GHz parking profile | `configs/ti_77ghz_parking_profile.json` + `artifacts/stage7/pilot_validation.json` | source-grounded + derived |
| High-mobility capability profile | `configs/ti_77ghz_high_mobility_capability_profile.json` + `artifacts/stage7/pilot_validation.json` | composite capability reference + derived |
| Range/velocity capability equations | `src/pcfmcw_isac/profiles.py`, `src/pcfmcw_isac/physics.py` | implementation |
| 54-action space | `src/pcfmcw_isac/policies.py` and submission action-space exporter | implementation invariant |
| Parking sensing pilot | `artifacts/stage7/pilot_validation.json` | simulation |
| High-mobility sensing pilot | `artifacts/stage7/pilot_validation.json` | simulation |
| DBPSK AWGN validation | `artifacts/stage7/pilot_validation.json` | simulation vs. analytical reference |
| PC-FMCW literature | `paper/paper1_references.bib` | peer-reviewed literature |

## Claim boundary

No item in this manifest is a hardware measurement. The high-mobility profile is not claimed to be a commercial preset. The pilot evidence is not substituted for the later frozen large-seed reliability benchmark.
