# Stage 2 — PC-FMCW / DPSK Link Model

**Canonical implementation:** this directory, `predictive_stage2/`.

## Scope
Freeze the communication layer that converts future actor–SDC geometry into PC-FMCW/DPSK link quantities.

## Included implementation
- `part_a_receiver.py` — Part-A-derived DBPSK receiver logic;
- `build_ber_lut.py` — BER-vs-SNR LUT generation;
- `link_model.py` — geometry-to-link evaluator;
- `link_model_config.json` — frozen model assumptions/configuration;
- `run_link_sensitivity.py` — range/pointing sensitivity runner;
- `test_part_a_receiver.py` and `test_link_model.py` — receiver/link-model tests;
- `stage.json` — machine-readable stage definition/status.

## Inputs
- frozen Part-A receiver implementation/parameters;
- Stage-01 relative future geometry;
- frozen paper link configuration.

## Method
Derive the DBPSK BER-vs-SNR calibration from the Part-A receiver, then apply the explicitly model-based geometry extension to obtain SNR, BER/PER, predicted goodput, outage state and usable-link lifetime.

The BER calibration is Part-A-derived. Range loss, pointing/FoV and atmospheric assumptions belong to the new vehicular link model and are not claimed as WOMD measurements.

## Outputs
Canonical BER LUT + hash, link-model configuration + hash, deterministic geometry-to-link evaluation and sensitivity artifacts.

Final publication artifacts belong under `artifacts/paper_final/ber/` and the provenance manifests.

## Acceptance gate
The LUT/configuration are frozen and hashed, link quantities are deterministic for fixed inputs, FoV/outage semantics are explicit, and sensitivity evidence is archived.

## Scientific boundary
WOMD supplies real motion only. Communication quantities are physics/model/simulation outputs; the Part-A receiver is not presented as a complete measured vehicular optical link budget.

## Commands
Use the implementations and tests directly from `predictive_stage2/`. The older `stages/02_pc_fmcw_dpsk_link/` path is retained temporarily for compatibility/history.
