# Stage 01 — Official WOMD Data Pipeline

Stage 01 converts official WOMD motion scenarios into the **single canonical corpus contract** consumed by the predictive-connectivity paper.

## Scientific role

WOMD supplies real mobility. This stage does not synthesize trajectories and does not create communication measurements. It preserves enough geometry and identity for later stages to map predicted/realized motion into the model-based PC-FMCW/DPSK link.

The deployable predictor sees observed history only. Future states are labels used for supervised training, evaluation, link realization, and the explicitly named information oracle.

## Frozen temporal contract

At the WOMD 10 Hz cadence:

- history: 11 states (`t=-1.0,...,0.0 s`), including the current state;
- future: 80 states (`t=0.1,...,8.0 s`);
- retained actors must satisfy the frozen validity/eligibility policy;
- SDC geometry comes from the scenario's true `sdc_track_index`;
- scenario identity is never discarded.

## Canonical NPZ schema

Every exported corpus must expose, at minimum:

| Key | Semantics |
|---|---|
| `history_xy` | `[N,11,2]` actor positions in the frozen SDC-relative frame |
| `history_vxy` | `[N,11,2]` causal velocities |
| `future_xy` | `[N,80,2]` future position labels |
| `history_valid` | `[N,11]` validity mask |
| `future_valid` | `[N,80]` validity mask |
| `scenario_id` | `[N]` stable scenario identity |
| `track_id` | `[N]` actor track identity |
| `sdc_track_id` | `[N]` true SDC track identity |
| `split` | `[N]` `training`, `development`, or `official_validation` |

Additional arrays are allowed, but downstream code must not silently reinterpret these fields.

## Split policy

Official WOMD training scenarios are deterministically partitioned at **scenario level** into `training` and `development`. The official WOMD validation TFRecords are exported independently as `official_validation` and are never used to tune lambda values, architectures, early-stopping policy, calibration choices, or scheduler hyperparameters.

`development` is not official validation.

## Required outputs

```text
data/processed/
├── womd_official_samples.npz
└── womd_v131_official_validation.npz

artifacts/paper_final/data_audit/
├── training_audit.json
└── official_validation_audit.json
```

Each audit records corpus hash, array shapes/dtypes, sample/scenario counts, split ownership, finite-value checks, temporal dimensions, and identity checks.

## Gate

Stage 01 is DONE only when both corpora exist separately, pass the canonical audit, contain no non-finite retained numeric values, preserve scenario IDs, use true-SDC geometry, and the official-validation corpus is labeled exactly `official_validation`.

If the official validation dataset is absent, Stage 01 remains BLOCKED/PARTIAL even if the training corpus is valid.
