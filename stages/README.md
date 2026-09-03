# Publication Workflow — Stage Gates

This directory is the active paper workflow for the predictive-connectivity research line.

Each stage is a **scientific gate**, not merely a documentation folder. A stage is complete only when its code has run on the specified data, raw artifacts exist, tests/gates pass, provenance is recorded, and the acceptance criteria are satisfied.

## Dependency graph

```text
00 Freeze & Provenance
        |
        v
01 WOMD Data Pipeline -----------+
        |                        |
        v                        v
02 PC-FMCW/DPSK Link         03 Classical Baselines
        |                        |
        +-----------+------------+
                    |
                    v
04 Communication-Aware GRU
                    |
                    v
05 Official Predictor Evaluation
                    |
                    v
06 Packet Scheduling
                    |
                    v
07 Statistics & Figures
                    |
                    v
08 Final Paper

Optional RL extension: after the core Stage 06/07 evidence exists.
```

## Status semantics

- `DONE`: implementation + real execution + artifacts + gate all complete.
- `PARTIAL`: implementation/evidence exists, but the final gate is incomplete.
- `BLOCKED`: cannot proceed because a required external dependency/data asset is absent.
- `NOT_STARTED`: final implementation/evidence has not begun.

## Stage contract

Every stage folder contains a `stage.json` that defines:

- scientific purpose;
- dependencies;
- required inputs;
- required outputs;
- work items;
- acceptance criteria;
- forbidden shortcuts/leakage;
- expected artifact locations.

The JSON is designed to be machine-readable and suitable for a later stage runner/validator.

## Core paper gate

The core paper requires Stages 00–08. Predictive RL is optional and must not block submission of the central trajectory-to-link-to-scheduling paper.
