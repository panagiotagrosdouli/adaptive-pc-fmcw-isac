# Stage 1 — causal WOMD scene and geometry contract

Stage 1 creates the canonical clean/oracle upstream artifact used by the
trajectory, beam-selection, and ADB stages. It is intentionally **not** a
sensor-realistic observation. The optional noisy PC-FMCW branch is evaluated
later as a separate experimental condition.

## Scientific contract

- Only WOMD states at `t <= current_time_index` are read.
- Every actor preserves `(scenario_id, track_id, anchor_timestamp_s)` as
  metadata; identifiers are never predictor features.
- WOMD annotated velocities, `tracks_to_predict`, and `objects_of_interest`
  are excluded from the realistic numeric feature payload.
- Velocity is reconstructed causally from adjacent valid positions.
- Valid actor dimensions must be positive and causal timestamps strictly
  increasing.
- Headlamp and receiver geometry are defined in `configs/stage1.json`.
- Receiver offset covariance must be finite, symmetric, and positive
  semidefinite before it is rotated into the anchor headlamp frame `H0`.
- The canonical dependency-free scenario adapter is
  `src/iscai_stage1/io/womd_adapter.py`.

## Validation

```bash
PYTHONPATH=iscai_stage1/src python -m unittest discover \
  -s iscai_stage1/tests -p 'test_*.py' -v
```

The future-mutation tests verify that changing or removing post-anchor WOMD
states cannot change the Stage-1 causal hash.

The dependency-free unit tests cover LiDAR point association/statistics. Real
WOMD LiDAR decoding additionally requires `waymo-open-dataset` and accessible
WOMD files; it must be reported as not executed when either is unavailable.
