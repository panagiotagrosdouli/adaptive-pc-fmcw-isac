# Stage 6 — Predictive Packet Scheduling

**Canonical implementation:** `stages/06_packet_scheduling/`

## Scope
Measure whether future-motion and future-link prediction produces realized packet-level communication gains under controlled multi-vehicle traffic, queue and deadline conditions.

## Inputs
- frozen Stage-02 link model;
- Stage-03 reactive/classical scheduling baselines;
- frozen Stage-04 learned predictors;
- Stage-05 held-out prediction outputs;
- predeclared traffic, queue, deadline, horizon, vehicle-count, load and random-seed protocol.

## Scheduler matrix
The core comparison includes Reactive, proportional-fair (PF), classical predictive policies such as CV/IMM, learned `GRU-Traj`, `GRU-Link`, `GRU-Out`, `GRU-Full`, Link-Lifetime scheduling and an Information Oracle. Random/Round-Robin may be retained as sanity/reference baselines where specified by the experiment manifest.

The oracle uses unavailable future information and therefore represents an information upper-reference, not a claim of globally optimal scheduling.

## Experimental grid
Core paper sweeps use:

- prediction horizon `H ∈ {0.3, 0.5, 1.0, 2.0} s`;
- active vehicles `N ∈ {3, 5, 10}`;
- offered load `ρ ∈ {0.35, 0.55, 0.75, 0.90}`;
- five paired random seeds;
- predeclared motion, FoV-edge and density scenario slices.

All schedulers in a paired comparison must see the same scenario, traffic realization, seed, queue/deadline rules and physical/link assumptions.

## Required metrics
- realized goodput;
- packet-delivery ratio (PDR);
- outage-related performance;
- deadline success/miss behavior;
- latency, including P95 latency;
- fairness;
- runtime/complexity evidence.

Raw results must retain scenario × seed × scheduler × operating-condition identity.

## Outputs
- paired raw scheduler CSVs;
- aggregate operating-point summaries;
- horizon, vehicle-count and load sweep artifacts;
- scenario-slice outputs;
- runtime/complexity records;
- manifests linking every result to predictor/link/traffic configuration hashes.

Publication evidence belongs under `artifacts/paper_final/scheduler_eval/` and `artifacts/paper_final/complexity/`.

## Acceptance gate
Stage 6 is complete only when the required scheduler matrix and operating grid have been executed with paired seeds, raw per-scenario evidence is preserved, all policies use identical exogenous realizations within each comparison, and learned schedulers consume only information available under their declared causal interface.

## Current status
`NOT_STARTED` for the final publication matrix. Existing scheduler implementations or synthetic staged experiments do not constitute the required official learned-scheduling evidence.

## Scientific role
This is the decisive network-level stage. A predictor may improve ADE or future-link fidelity yet fail to improve realized scheduling because queues, deadlines, load, fairness constraints or insufficient scheduling flexibility can limit the value of prediction. Positive and negative operating regimes are both publication evidence.

## Commands
Final experiment runners, manifests, evidence checks and scheduler-result aggregation belong in `stages/06_packet_scheduling/`.
