# Stage 3 — Classical Baselines

**Canonical implementation:** `stages/03_classical_baselines/`

## Scope
Establish causal non-learned motion-prediction and scheduling baselines before learned communication-aware models are evaluated.

## Inputs
- Stage-01 causal WOMD histories and future evaluation targets;
- Stage-02 frozen PC-FMCW/DPSK link model;
- common prediction horizons and scheduler interfaces.

## Method
Evaluate history-only kinematic predictors such as last-position, constant velocity, constant acceleration, linear Kalman and IMM-style forecasting through a common forecast interface. Convert each forecast to predicted future link state using the same frozen Stage-02 model. Establish non-learned packet policies including Random, Round Robin, Reactive Greedy, proportional-fair, Predictive Utility and Link-Lifetime scheduling where applicable.

The information-oracle forecast may use ground-truth future only as an evaluation upper-information baseline. It is not deployable and is not a proof of globally optimal scheduling.

## Outputs
- scenario-level classical predictor metrics;
- trajectory-to-link fidelity metrics;
- reproducible baseline scheduler outputs;
- aggregate baseline tables used for later learned-model comparisons.

## Acceptance gate
All deployable predictors must use observed history only, share the same evaluation geometry/link model, preserve scenario identity in raw outputs, and produce deterministic results for fixed inputs/seeds. Oracle results must be labeled explicitly as information-oracle evidence.

## Scientific role
These baselines answer whether learned GRU complexity is actually necessary. Learned gains are meaningful only relative to strong causal classical prediction and current-state scheduling baselines.

## Commands
Use predictor implementations, IMM adapter, evaluator, scheduler implementations, aggregation utilities and tests in `stages/03_classical_baselines/`.
