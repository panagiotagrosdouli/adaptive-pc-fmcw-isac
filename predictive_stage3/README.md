# Stage 3 — Classical Baselines

**Canonical implementation:** this directory, `predictive_stage3/`.

## Scope
Establish causal non-learned motion-prediction and scheduling baselines before learned communication-aware models are evaluated.

## Included implementation
- `predictors.py` — Last Position, CV, CA, Kalman-style and oracle interfaces;
- `imm.py` — IMM-style classical forecasting;
- `evaluate_predictors.py` — trajectory/link-fidelity evaluation;
- `aggregate_predictor_eval.py` — descriptive aggregation;
- `schedulers.py` — Random, Round Robin, Reactive Greedy, PF, Predictive Utility and Link-Lifetime baselines;
- `test_predictors.py`, `test_evaluate_predictors.py`, `test_schedulers.py` — baseline tests;
- `stage.json` — machine-readable stage definition/status.

## Inputs
- Stage-01 causal WOMD histories and future evaluation targets;
- Stage-02 frozen PC-FMCW/DPSK link model;
- common prediction horizons and scheduler interfaces.

## Method
Evaluate history-only kinematic predictors through a common forecast interface and convert each forecast to future link state using the same frozen Stage-02 model. The information oracle may expose ground-truth future only as an evaluation upper-information baseline; it is not deployable and is not a proof of globally optimal scheduling.

## Outputs
Scenario-level classical predictor metrics, trajectory-to-link fidelity metrics, reproducible baseline scheduler outputs and aggregate baseline tables.

## Acceptance gate
Every deployable predictor is causal, scenario identity is retained, evaluation geometry/link assumptions are shared, fixed inputs/seeds are reproducible, and oracle evidence is explicitly labeled as information-oracle evidence.

## Scientific role
These baselines separate gains due to prediction itself from gains due specifically to learned communication-aware prediction.

## Commands
Use the implementations and tests directly from `predictive_stage3/`. The older `stages/03_classical_baselines/` path is retained temporarily for compatibility/history.
