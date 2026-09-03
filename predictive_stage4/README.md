# Stage 4 — Communication-Aware GRU

**Canonical implementation:** `stages/04_communication_aware_gru/`

## Scope
Train the common learned trajectory architecture under four predeclared objectives and determine whether communication-aware supervision improves future link-state fidelity without changing the model capacity.

## Inputs
- Stage-01 training/development corpora only;
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

Lambda selection must use a predeclared **lambda-independent development criterion**. Weighted training-objective values from different lambda settings are not directly comparable because the score definition itself changes with lambda.

## Outputs
- raw development-only lambda sweep and frozen selection record;
- four objectives × five paired seeds = 20 final checkpoint records;
- checkpoint metadata with data/config/code hashes and normalization provenance;
- development-only uncertainty calibration artifact;
- descriptive ablation summary.

Final evidence belongs under `artifacts/paper_final/lambda_sweep/` and `artifacts/paper_final/checkpoints/`.

## Acceptance gate
Stage 4 is complete only when the lambda-selection rule is scientifically fixed, all 20 required runs are present and provenance-compatible, training normalization is verified as training-only, calibration uses development data only, and the checkpoint archive passes its evidence gate.

## Current status
`PARTIAL`. Implementation exists, but code presence is not equivalent to a completed five-seed/four-objective experiment archive. Existing preliminary runs remain internal-development evidence until the final frozen protocol is executed.

## Scientific role
This stage tests whether optimizing communication-relevant surrogate losses changes predictor quality in ways that ADE/FDE alone cannot reveal. Final claims require Stage-05 held-out link evaluation and Stage-06 realized scheduling outcomes.

## Commands
Use the model, data loader, objectives, communication surrogates, trainer, lambda-sweep runner, calibration utilities, checkpoint verifier and tests in `stages/04_communication_aware_gru/`.
