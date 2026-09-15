# Stage 06 — Packet Scheduling

This is a clean rebuild of the packet-level experiment core on the current
repository architecture. It does not import historical Stage-03 branches.

## Scientific contract

- Every policy receives the same seeded arrival trace.
- Every policy is scored against the same ground-truth goodput and outage trace.
- Predictions are decision inputs only; they never replace physical delivery truth.
- Packets are deadline constrained and partially served packets are not counted
  as timely delivery unless the full packet is completed before expiration.
- Raw outputs include PDR, deadline misses, timely goodput, mean/P95 latency,
  outage exposure, and Jain fairness.

## Interface

`SchedulerState` is the stable boundary between Stage 05 predictor outputs and
Stage 06 scheduling. A future predictor can supply per-vehicle predicted
 goodput/outage without requiring any legacy Stage-03 import.

## Status

`PARTIAL`: the simulator and invariants are implemented, but publication-level
results require frozen Stage-05 predictor artifacts, frozen PHY truth traces,
and the declared operating-condition matrix. No synthetic run is promoted to
publication evidence.
