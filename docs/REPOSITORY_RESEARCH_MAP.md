# Repository Research Map

Frozen baseline: `3904c4c2a69c4af96751d64614f7228ddea24b56`.

The project studies adaptive 77-GHz PC-FMCW ISAC under mobility and imperfect PHY knowledge. The key pipeline is: configuration and provenance -> analytical capability checks -> deterministic physics gate -> B0-B4/Oracle policy evaluation -> communication and sensing receiver metrics -> B4 confidence qualification -> frozen paired benchmark -> supplemental robustness/calibration experiments -> figures/tables -> IEEE manuscript.

## Main areas

- `configs/`: frozen experiment definitions and QoS/statistical rules.
- `src/pcfmcw_isac/`: waveform, physical feasibility, communication/sensing models, uncertainty and policy implementation.
- `scripts/`: reproducible experiment and publication entry points.
- `tests/`: scientific invariants and regression checks.
- `artifacts/stage7/`: diagnostic validation evidence, not final primary results.
- `artifacts/publication/v2_1/`: frozen primary publication evidence; preserve unchanged.
- `artifacts/publication/v2_1/supplemental/`: reviewer-grade supplemental evidence.
- `paper/`: IEEE manuscript, tables and bibliography.
- `.github/workflows/`: CI and publication/reproduction gates.

## Provenance classes

Literature source; source-derived parameter; analytical derivation; controlled simulation input; simulation output; statistical derivation; host runtime measurement; hardware measurement.

The adaptive-controller results are simulation/analytical evidence, not an RF hardware-measurement campaign.
