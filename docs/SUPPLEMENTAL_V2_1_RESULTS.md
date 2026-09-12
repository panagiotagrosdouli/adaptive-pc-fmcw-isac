# Supplemental Publication v2.1 — Historical Results Note

Evidence class: `SUPPLEMENTAL_PUBLICATION_V2_1_SIMULATION_NOT_HARDWARE_MEASUREMENT`.

## Status

**HISTORICAL / SUPERSEDED FOR FINAL-SUBMISSION PURPOSES.**

This file originally summarized an early supplemental workflow run `33975266575` at source commit `ef0e135b88c7c9647d72195f80884e380bc33cf6`. It is retained only to preserve provenance of that evidence instance. It must not be cited as the current/final reviewer-grade evidence.

A later completed pre-correction reviewer suite was run `34696063382`, and an even later source audit corrected the Texas Instruments parking-profile chirp-slope semantics. The corrected model uses 858 MHz valid sweep bandwidth for range resolution and the independently source-reported 40 MHz/us programmed chirp slope for beat-frequency/range-support calculations. The corrected short-range positive-IF support is approximately **18.74 m**, not 22.36 m.

Because physical feasibility is part of the policy path, the full reviewer-grade supplemental suite is being rerun as a distinct corrected-model evidence instance. Final manuscript statistics, physical maps, runtime values, and artifact digests must come from that corrected run.

## Historical qualitative findings

The historical supplemental experiments supported a reliability--availability interpretation rather than unconditional B4 superiority: B4 selected a narrower operating subset with higher observed conditional reliability, while severe mismatch exposed explicit failure boundaries. Those qualitative findings remain useful context, but their final quantitative values require corrected-model revalidation.

Historical evidence also showed that the Python B4 implementation was not an embedded real-time controller. Runtime measurements from any historical run remain measurements of that exact host/code instance only and must not be silently copied into the corrected final manuscript.

## Permanent claim boundary

No supplemental run supports claims of universal B4 superiority, arbitrary-mismatch robustness, global Pareto optimality, embedded/hard-real-time readiness, hardware/RF validation by this repository, physical-energy interpretation of normalized cost, or packet-level PER without a declared packet model.

For current status, use `docs/research/FINAL_PUBLICATION_READINESS.md`, `docs/research/CLAIM_AUDIT.md`, and the machine-readable artifacts from the final corrected-model run.
