# Reproducibility

Frozen scientific baseline: `3904c4c2a69c4af96751d64614f7228ddea24b56`.
Submission branch: `paper/submission-ready`.

## Principles

- Preserve frozen primary evidence under `artifacts/publication/v2_1/`.
- Use repository-native scripts and Make targets rather than ad-hoc calculations.
- Keep diagnostic/smoke outputs distinct from final publication results.
- Treat the high-draw reference as a Monte Carlo comparator, not physical truth.
- Report host runtime separately from deployment or ECU claims.

## Frozen protocol

Primary source: `configs/paper_protocol_v2_1.json`.

The protocol fixes QoS thresholds, B4 confidence qualification, paired seed bank, final communication/sensing evaluation budgets and bootstrap procedure. Any change to these settings creates a new protocol and must not overwrite v2.1 evidence.

## Reproduction order

1. Install the project using the dependency instructions in `pyproject.toml`/README.
2. Run the full test suite.
3. Run the publication smoke/structural gate.
4. Run the frozen primary publication pipeline only when full regeneration is intended.
5. Run the supplemental publication workflow for reviewer-grade evidence.
6. Regenerate figures/tables from machine-readable artifacts.
7. Compile the IEEE manuscript.
8. Run the submission gate and verify artifact digests/provenance.

Exact repository-native commands are audited on this branch before final submission status is declared.
