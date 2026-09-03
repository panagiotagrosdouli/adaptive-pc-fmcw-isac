# Stage 0 — Freeze and Provenance

**Canonical implementation:** this directory, `predictive_stage0/`.

## Scope
Freeze the exact code, dataset identities, split ownership and experiment protocol before paper-scale experiments are interpreted as final evidence.

## Included implementation
- `scripts/freeze_stage00.py` — provenance freeze and split-overlap gate;
- `experiment_protocol.template.json` — frozen paper experiment contract;
- `stage.json` — machine-readable stage definition/status;
- `tests/test_freeze_stage00.py` — provenance and overlap-contract tests.

## Inputs
- repository commit SHA;
- training/development corpus;
- official-validation corpus when locally available;
- experiment protocol/configuration.

## Method
Hash code/data/configuration inputs, audit scenario ownership and enforce zero train/development/official-validation overlap.

## Outputs
Publication manifests, split-overlap audit and Stage-00 status report under `artifacts/paper_final/manifests/` and `artifacts/paper_final/data_audit/`.

## Acceptance gate
The stage is `DONE` only when immutable provenance artifacts exist and the scenario-overlap audit passes. Script presence alone is insufficient.

## Commands
```bash
python predictive_stage0/scripts/freeze_stage00.py \
  --train-npz data/processed/womd_official_samples.npz \
  --official-validation-npz data/processed/womd_v131_official_validation.npz \
  --output-root artifacts/paper_final

pytest -q predictive_stage0/tests
```

The older `stages/00_freeze_and_provenance/` path is retained temporarily for compatibility/history while the predictive-stage layout becomes the active repository organization.
