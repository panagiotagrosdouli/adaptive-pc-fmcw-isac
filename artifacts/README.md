# Publication Artifacts

This directory is the single publication-output workspace for the predictive-connectivity paper.

Do not commit raw WOMD data. Large checkpoints may remain external when necessary, but their hashes, manifests and selection records must be preserved.

Expected final layout:

```text
artifacts/paper_final/
├── manifests/          code/data/config/split provenance
├── data_audit/         corpus integrity and zero-overlap reports
├── ber/                frozen Part-A receiver-derived DBPSK BER LUT
├── lambda_sweep/       raw development sweep and frozen selection record
├── checkpoints/        canonical 4 objectives x 5 seeds archive
├── predictor_eval/     per-scenario official-validation metrics
├── scheduler_eval/     per-scenario x seed x policy packet results
├── statistics/         bootstrap CIs, paired tests, effects, Holm outputs
├── joined_analysis/    trajectory/link fidelity vs realized scheduler performance
├── figures/            vector PDF/SVG plus preview PNG
├── tables/             CSV and LaTeX tables generated from frozen artifacts
├── complexity/         runtime/compute evidence
└── reproduction/       immutable experiment and reproduction manifests
```

A directory being present does not imply that its evidence is complete. Stage `stage.json` status and acceptance artifacts remain authoritative.
