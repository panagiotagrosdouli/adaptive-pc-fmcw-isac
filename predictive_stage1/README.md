# Stage 1 — WOMD Data Pipeline

**Canonical implementation:** `stages/01_womd_data_pipeline/`

## Scope
Build and audit the causal WOMD mobility corpus used by all downstream trajectory and communication experiments.

## Inputs
- official WOMD training TFRecords;
- official WOMD validation TFRecords for final held-out evaluation;
- frozen scenario-level split policy.

## Method
Use 11 observed history steps and 80 future target steps, preserve scenario/track identity, use the true SDC track, and represent future communication geometry relative to the actual future SDC trajectory. The SDC itself is not a communication target.

## Outputs
Canonical NPZ corpora containing actor history/future states, validity masks, scenario identifiers, split ownership, `sdc_future_xy` and `future_relative_xy`, plus integrity and overlap audits.

## Acceptance gate
No NaN/Inf in required finite arrays, deterministic scenario ownership, exact train/development/official-validation separation, and verified identity `future_relative_xy = future_xy - sdc_future_xy`.

## Commands
Use exporter, audit scripts and tests in `stages/01_womd_data_pipeline/`. Raw WOMD data remain local and are never redistributed.
