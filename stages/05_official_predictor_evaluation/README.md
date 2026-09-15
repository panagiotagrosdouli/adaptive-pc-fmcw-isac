# Stage 05 — Official Predictor Evaluation

This stage is the controlled bridge between the frozen mobility/predictor evidence and the packet-level scheduler in Stage 06.

## Scientific role

Stage 05 evaluates a fixed, deployable predictor on the **official validation corpus**. Predictions are decision inputs only. They are never treated as realized channel capacity; Stage 06 scores delivery from shared ground-truth traces.

The stage is intentionally blocked until the real official validation corpus and the frozen predictor/checkpoint are available. No synthetic smoke test may be promoted to publication evidence.

## Required input contract

The official validation artifact must:

- be disjoint from training/development at scenario level;
- preserve `scenario_id`, `track_id`, and `sdc_track_id`;
- expose the canonical 11-step observed history and 80-step future horizon;
- use only causal history as predictor input;
- identify the exact predictor checkpoint and preprocessing configuration;
- provide cryptographic hashes for the checkpoint, preprocessing/configuration, and input corpus.

## Required output contract

The Stage-05 prediction artifact must retain, at minimum:

| Field | Semantics |
|---|---|
| `scenario_id` | stable WOMD scenario identity |
| `track_id` | actor identity |
| `sdc_track_id` | true SDC identity |
| `predicted_xy` | `[N,80,2]` predicted future trajectory in the declared frame |
| `prediction_valid` | `[N,80]` prediction validity mask |
| `horizon_s` | declared prediction horizon |
| `checkpoint_sha256` | exact model checkpoint provenance |
| `preprocessing_sha256` | exact preprocessing/config provenance |
| `input_corpus_sha256` | exact validation-corpus provenance |

Additional predictor-specific scores are allowed, but downstream stages must not silently reinterpret them as realized communications performance.

## Gate

Stage 05 becomes `READY` only when all required real artifacts exist and pass schema, provenance, leakage, and frozen-configuration checks. It becomes `DONE` only after the complete declared official validation evaluation is executed and independently audited.

Until then, status remains `BLOCKED` and Stage 06/07 smoke tests remain engineering validation rather than publication evidence.
