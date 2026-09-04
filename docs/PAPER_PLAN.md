# Paper Plan

## Working title

**Robust Reliability-Constrained Adaptive Phase-Coded FMCW ISAC for High-Mobility Vehicular Links**

## Story

High-mobility PC-FMCW ISAC must satisfy two coupled services from one physical-layer configuration: reliable communications and accurate sensing. Fixed configurations are conservative, while single-objective adaptation can violate the other service. The paper formulates discrete robust PHY adaptation under imperfect channel/impairment knowledge and characterizes the feasible operating region where both services can be guaranteed.

## Intended contributions

1. A reproducible PC-FMCW joint sensing/communication PHY model with explicit high-mobility impairments and uncertainty boundaries.
2. A robust reliability-constrained configuration policy that jointly enforces communication and sensing QoS.
3. Feasible-region characterization across SNR, Doppler, interference, CFO and phase noise.
4. Communication-sensing-resource Pareto analysis against fixed, single-objective, deterministic-joint and oracle baselines.
5. Failure-mode and sensitivity analysis showing when joint guarantees become impossible with the available configuration set.

## Main figures

F1 system architecture and adaptation loop.
F2 validated communication/sensing model sanity curves.
F3 SNR-Doppler joint-feasibility heatmap.
F4 interference-CFO joint-feasibility heatmap.
F5 BER/PER/effective-rate comparison by policy.
F6 range/velocity error comparison by policy.
F7 resource cost versus joint reliability.
F8 three-objective Pareto frontier.
F9 robustness cost versus state uncertainty.
F10 oracle gap and infeasible-region decomposition.

## Main tables

T1 PC-FMCW and channel parameters with provenance.
T2 policy definitions and information access.
T3 formal aggregate results with confidence intervals.
T4 per-regime failure rates.
T5 ablations and runtime/complexity.

## Submission rule

Do not write a positive conclusion before the frozen experiments. Negative or regime-dependent findings remain reportable. The oracle is never described as deployable.
