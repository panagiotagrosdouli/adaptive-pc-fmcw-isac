# Stage 05 — Official Predictor Evaluation

This directory contains the fail-closed aggregation and acceptance gate for the
first evaluation on untouched official WOMD validation data.

The Stage-03 classical evaluator and Stage-04 learned-checkpoint evaluator must
first write one row per scenario and predictor (and per seed for learned
models). `aggregate_official_evaluation.py` then verifies the official split,
the complete four-objective by five-seed archive, development-only calibration,
metric support, uniqueness, and cryptographic provenance before producing:

- `scenario_metrics.csv` — immutable scenario-level evidence;
- `aggregate_metrics.csv` — descriptive means with support counts;
- `aggregate_metrics.json` — the same descriptive summary for machines;
- `calibration_metrics.csv` — NLL and coverage summary where supported;
- `model_ranking.csv` — per-metric rankings, without model selection;
- `manifests/stage05.json` — hashes and acceptance result.

The aggregate tables are descriptive. Stage 07 remains responsible for paired
scenario-cluster inference, confidence intervals, multiplicity correction, and
publication figures.

Run unit tests with `make stage05-test`. The full invocation is documented in
`predictive_stage5/README.md`.
