# Stage 1 — WOMD Data Pipeline

**Canonical implementation:** this directory, `predictive_stage1/`.

## Scope
Build and audit the causal WOMD mobility corpus used by the predictive-connectivity paper.

## Included implementation
- `export_womd_tfrecord.py` — WOMD TFRecord → canonical NPZ export;
- `audit_corpus.py` — schema, finiteness and true-SDC geometry audit;
- `audit_split_ownership.py` — scenario-level split leakage audit;
- `test_audit_corpus.py` and `test_export_contract.py` — data-contract tests;
- `stage.json` — machine-readable stage definition/status.

## Inputs
- official WOMD training TFRecords;
- official WOMD validation TFRecords for final held-out evaluation;
- frozen scenario-level split policy.

## Method
Use 11 observed history steps and 80 future target steps, preserve scenario/track identity, use the true SDC track, and construct future communication geometry relative to the actual future SDC. The SDC itself is not a communication target.

The canonical geometry contract is:

```text
future_relative_xy = future_xy - sdc_future_xy
```

with all three quantities represented in the same anchor-SDC orientation.

## Outputs
Canonical NPZ assets with actor history/future, validity masks, scenario IDs, split ownership, `sdc_future_xy`, `future_relative_xy`, and integrity/overlap audits.

## Acceptance gate
No NaN/Inf, deterministic scenario ownership, exact train/development/official-validation separation, and verified true-SDC future geometry identity.

## Commands
```bash
python predictive_stage1/export_womd_tfrecord.py /data/womd/training/*.tfrecord \
  --output data/processed/womd_official_samples.npz

python predictive_stage1/audit_corpus.py data/processed/womd_official_samples.npz \
  --output artifacts/paper_final/data_audit/training_audit.json
```

Raw WOMD remains local and is never redistributed. The older `stages/01_womd_data_pipeline/` path is retained temporarily for compatibility/history.
