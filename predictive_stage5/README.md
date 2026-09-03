# Stage 5 — Official WOMD Predictor Evaluation

**Canonical implementation:** `stages/05_official_predictor_evaluation/`

## Scope
Perform the first untouched official-WOMD validation evaluation of the frozen classical and learned predictors, measuring both trajectory accuracy and communication-state fidelity.

## Inputs
- Stage-01 official-validation corpus with true-SDC future geometry;
- frozen Stage-02 link model and hashes;
- frozen Stage-03 classical predictors;
- Stage-04 selected 20-checkpoint learned archive and development-only calibration artifacts.

No hyperparameter, lambda, checkpoint, normalization or calibration choice may be changed after official-validation results are inspected.

## Method
Run every frozen predictor on the same held-out scenarios and preserve scenario identity in the raw outputs. Evaluate predicted actor trajectories and the communication states induced by those trajectories relative to the true future SDC.

## Required metrics
- trajectory: ADE and FDE;
- geometry: range MAE and bearing MAE;
- link fidelity: SNR MAE and goodput MAE;
- outage prediction: F1 and AUROC;
- temporal connectivity: link-lifetime MAE;
- probabilistic quality: NLL and empirical 50%, 90%, and 95% coverage.

Metrics must be retained at scenario level before aggregation so later inference can respect the WOMD scenario as the statistical cluster.

## Outputs
- per-scenario/per-model held-out predictor CSV;
- aggregate descriptive JSON/table;
- calibration/NLL/coverage table;
- provenance manifest tying results to dataset, checkpoint, calibration and link-model hashes.

Publication outputs belong under `artifacts/paper_final/predictor_eval/` and `artifacts/paper_final/manifests/`.

## Acceptance gate
Stage 5 is complete only when all frozen predictors are evaluated on the untouched official split, required metrics are finite or explicitly marked undefined with support counts, scenario IDs are retained, and no official-validation information has influenced model selection.

## Current status
`BLOCKED` until the Stage-04 experiment archive and selection/calibration contract are frozen and the official WOMD validation corpus is available under the Stage-00/01 provenance rules.

## Scientific role
This stage tests the paper's central intermediate hypothesis: the predictor with the lowest displacement error need not be the predictor with the best future communication-state fidelity. Network-level benefit is evaluated separately in Stage 6.

## Commands
Official-validation build/evaluation commands and acceptance checks belong in `stages/05_official_predictor_evaluation/`. Generated official-validation data remain local and are not committed to the repository.
