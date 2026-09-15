# Stage 01 — Official WOMD Data Pipeline

Stage 01 defines the canonical motion-corpus boundary for the predictive-connectivity research path. It does not claim that official WOMD evidence is present in this repository.

## Scientific contract

At the WOMD 10 Hz cadence, the prediction anchor uses 11 history states (`t=-1.0,...,0.0 s`) and 80 future label states (`t=0.1,...,8.0 s`). Scenario identity and the true SDC track identity must be retained.

Training/development ownership is assigned deterministically at **scenario level**. Official WOMD validation is a separate corpus labeled exactly `official_validation`; it is not a development set and must not be used to tune models, preprocessing, calibration, scheduler parameters, or stopping rules.

Trajectory prediction coordinates may be represented in the SDC pose at the anchor. Downstream communication geometry must additionally preserve the actor-minus-SDC future displacement using the true future SDC trajectory in that common anchor orientation. Future SDC motion must never be silently replaced by zero.

## Canonical NPZ schema

Required arrays are `history_xy [N,11,2]`, `history_vxy [N,11,2]`, `future_xy [N,80,2]`, `future_relative_xy [N,80,2]`, `sdc_future_xy [N,80,2]`, `history_valid [N,11]`, `future_valid [N,80]`, `scenario_id [N]`, `track_id [N]`, `sdc_track_id [N]`, and `split [N]`.

The geometry identity is

`future_relative_xy = future_xy - sdc_future_xy`

when all three arrays are expressed in the common SDC-at-anchor orientation.

## Status

`BLOCKED` until the real official WOMD training and validation corpora are available and independently pass the schema, finite-value, geometry, identity, and split-ownership audits. Unit tests or synthetic fixtures validate code only; they are not publication evidence.
