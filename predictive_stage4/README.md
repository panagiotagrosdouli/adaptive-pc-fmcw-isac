# Stage 4 — Communication-Aware GRU

**Canonical implementation:** this directory, `predictive_stage4/`.

## Scope
Train the common learned trajectory architecture under four predeclared objectives and determine whether communication-aware supervision improves future link-state fidelity without changing model capacity.

## Included implementation
- `model.py` — canonical 4-D-input, two-layer GRU(128) trajectory predictor;
- `data.py` — causal corpus loading and training-only normalization;
- `objectives.py` — trajectory/link/outage/full objective composition;
- `surrogates.py` — differentiable communication surrogates;
- `train.py` — learned-model training runner;
- `run_lambda_sweep.py` — development-only lambda sweep orchestration;
- `calibration.py` — development-only residual uncertainty calibration;
- `evaluate_checkpoint.py` — checkpoint trajectory/link evaluation;
- `verify_archive.py` — checkpoint-evidence gate;
- `aggregate_ablation.py` — descriptive four-objective aggregation;
- `test_calibration.py` and `test_evidence_gate.py` — calibration/archive tests;
- `stage.json` — machine-readable stage definition/status.

## Inputs
- Stage-01 training/development corpus only;
- Stage-02 frozen link-model configuration;
- training-only normalization statistics;
- predeclared seeds and lambda-search protocol.

Official WOMD validation is not available for lambda selection, early stopping, model selection or uncertainty calibration.

## Model
The canonical predictor uses a 4-D history input, a two-layer GRU with hidden size 128, and an MLP horizon head producing 80 future 2-D positions. Architecture and training protocol remain fixed across objective ablations.

## Learned objectives
```text
GRU-Traj : L_traj
GRU-Link : L_traj + lambda_link * L_link
GRU-Out  : L_traj + lambda_out * L_outage
GRU-Full : L_traj + lambda_link * L_link + lambda_out * L_outage
```

Lambda selection must use a predeclared lambda-independent development criterion. Weighted training-objective values from different lambda settings are not directly comparable because the score definition changes with lambda.

## Outputs
Development-only lambda sweep and selection record, four objectives × five paired seeds = 20 final checkpoint records, checkpoint metadata/hashes, development-only calibration artifacts and descriptive ablation summaries.

## Acceptance gate
Stage 4 is complete only when the lambda-selection rule is scientifically fixed, all 20 required runs are present and provenance-compatible, training normalization is training-only, calibration uses development data only, and the archive evidence gate passes.

## Current status
`PARTIAL`. Implementation exists, but code presence is not equivalent to a completed five-seed/four-objective publication archive.

## Scientific role
This stage tests whether communication-relevant supervision improves future link-state fidelity beyond trajectory-only training. Final claims require Stage-05 held-out evaluation and Stage-06 realized scheduling outcomes.

## Commands
Use the implementations and tests directly from `predictive_stage4/`. The older `stages/04_communication_aware_gru/` path is retained temporarily for compatibility/history.
