# Stage 00 — Freeze and Provenance

This stage converts the research plan into an immutable experiment contract before any final held-out evaluation.

## Gate

Stage 00 remains **PARTIAL** until the separate official WOMD validation corpus is present and its scenario IDs have been audited against the internal training/development scenarios.

## Required outputs

```text
artifacts/paper_final/
├── manifests/
│   ├── code_manifest.json
│   ├── dataset_manifest.json
│   └── experiment_protocol.json
└── data_audit/
    └── split_overlap.json
```

## Canonical execution

```bash
python stages/00_freeze_and_provenance/scripts/freeze_stage00.py \
  --train-npz data/processed/womd_official_samples.npz \
  --official-validation-npz data/processed/womd_v131_official_validation.npz \
  --output-root artifacts/paper_final
```

If official validation is not available yet, run with only `--train-npz`. The script will still freeze code/protocol metadata but will report the stage as blocked rather than pretending that the held-out gate is complete.

## Scientific invariants

- splitting is scenario-level, never sample-level;
- development is derived only from official WOMD training;
- official WOMD validation is untouched by lambda/model selection;
- deployable predictors receive observed history only;
- future ground truth is used only for supervision/evaluation and the information oracle;
- communication outputs are physics/model-based PC-FMCW/DPSK results over real WOMD mobility, not measured optical links.

## Acceptance criteria

1. exact repository commit is recorded;
2. every supplied dataset file has SHA-256 provenance;
3. train/development/official-validation scenario sets have zero overlap;
4. the experiment protocol is frozen before Stage 05;
5. official validation has not been used for tuning.
