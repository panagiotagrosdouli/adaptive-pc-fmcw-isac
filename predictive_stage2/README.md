# Stage 2 — PC-FMCW / DPSK Link Model

**Canonical implementation:** `stages/02_pc_fmcw_dpsk_link/`

## Scope
Freeze the communication layer that converts future actor–SDC geometry into communication-relevant link quantities for prediction and scheduling experiments.

## Inputs
- Part-A PC-FMCW/DPSK receiver implementation and receiver parameters;
- Stage-01 relative geometry;
- frozen paper link-model configuration.

## Method
Derive the DBPSK BER-versus-SNR lookup from the Part-A receiver, then apply the paper's explicit geometry-dependent extension to obtain SNR, BER/PER, predicted goodput, outage state and usable-link lifetime. The BER calibration is Part-A-derived; range/pointing/atmospheric propagation assumptions are a new model-based paper extension and must be described as such.

## Outputs
- canonical BER LUT and hash;
- frozen link-model configuration and hash;
- geometry-to-link evaluator;
- sensitivity-analysis artifacts for the added propagation assumptions.

Final publication artifacts belong under `artifacts/paper_final/ber/` and the corresponding provenance manifests.

## Acceptance gate
The receiver-derived LUT and model configuration must be frozen and hashed, link quantities must be deterministic for a fixed geometry/configuration, FoV/outage semantics must be explicit, and sensitivity analysis for the paper-extension assumptions must be archived.

## Scientific boundary
WOMD supplies real vehicle motion. The communication quantities produced here are model/simulation based; they are not WOMD communication measurements. The Part-A receiver result must not be overstated as a complete measured vehicular optical link budget.

## Commands
Use the receiver, LUT builder, link-model implementation, sensitivity script and tests in `stages/02_pc_fmcw_dpsk_link/`.
