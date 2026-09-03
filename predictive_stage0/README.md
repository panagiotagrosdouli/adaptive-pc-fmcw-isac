# Stage 0 — Freeze and Provenance

**Canonical implementation:** `stages/00_freeze_and_provenance/`

## Scope
Freeze the exact code, dataset identities, split ownership and experiment protocol before paper-scale experiments are interpreted as final evidence.

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
Use the executable implementation and tests in `stages/00_freeze_and_provenance/`.
