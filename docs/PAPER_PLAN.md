# Paper Plan

## Working title

**Physics-Gated Reliability-Constrained Adaptive Phase-Coded FMCW ISAC for High-Mobility Vehicular Links**

Alternative title if the profile-selection result becomes central:

**From Physical Feasibility to Robust PHY Adaptation in Phase-Coded FMCW Vehicular ISAC**

## Story

High-mobility PC-FMCW ISAC must satisfy two coupled services from one transmitted waveform: reliable communications and accurate sensing. A crucial first result is that not every waveform/profile is physically valid for every vehicular state. Short-range parking-style FMCW timing can provide fine range resolution while imposing a low monostatic unambiguous-velocity limit. High-mobility states therefore require a different timing/resource region before any stochastic reliability optimizer can succeed.

The paper consequently uses a two-layer design:

1. **physics gate** — remove configurations that violate hard range/velocity/rate capability limits;
2. **robust reliability selection** — among physically admissible configurations, choose the minimum-cost action that satisfies joint communication and sensing QoS with a predeclared probability under imperfect state knowledge.

This makes the contribution more specific than generic adaptive ISAC resource allocation: the action set is PC-FMCW-specific, the sensing and communication paths have correct one-way/two-way propagation semantics, and the feasible region is tied to actual automotive-radar timing/hardware capabilities.

## Intended contributions

1. A reproducible PC-FMCW joint sensing/communication model that separates the one-way V2V link from the monostatic two-way sensing echo and samples sensing at the dechirped IF, consistent with automotive radar hardware.
2. Literature-grounded 77-GHz operating profiles plus analytical capability boundaries for range and radial velocity, with explicit provenance and claim hierarchy.
3. A physics-gated finite-action PC-FMCW adaptation framework that rejects configurations outside their unambiguous operating region before reliability optimization.
4. A robust chance-constrained configuration policy that jointly enforces communication BER/rate and sensing range/velocity QoS under uncertain SNR, residual synchronization error and interference.
5. Feasible-region and Pareto characterization showing the resource cost of maintaining joint reliability and identifying states where the declared action set is genuinely infeasible.

## Baselines

- B0 fixed conservative profile/action;
- B1 communication-only adaptation;
- B2 sensing-only adaptation;
- B3 deterministic joint adaptation at the estimated state;
- B4 physics-gated robust joint adaptation (proposed);
- Oracle with perfect instantaneous state, used only as an evaluation bound.

A useful ablation is **B4-no-gate**, which runs the same stochastic policy without hard physical profile gating. It tests whether explicit physical feasibility adds value beyond a learned/empirical reliability model.

## Main figures

F1 system architecture: one PC-FMCW transmitter, one-way communication receiver, monostatic sensing receiver and two-layer controller.
F2 literature-grounded profile capability plot: range resolution / max IF range / velocity resolution / max unambiguous velocity.
F3 communication DBPSK Monte-Carlo BER versus analytical AWGN reference.
F4 sensing RMSE versus IF SNR for short-range and high-mobility profiles.
F5 range-velocity physical-feasibility map with profile-selection regions.
F6 SNR-residual-frequency joint communication-feasibility heatmap.
F7 joint QoS reliability by B0-B4/Oracle.
F8 resource cost versus joint reliability.
F9 three-objective communication-sensing-resource Pareto frontier.
F10 robustness cost versus state-estimation uncertainty and model mismatch.
F11 oracle gap and infeasible-region decomposition.

## Main tables

T1 source-derived PC-FMCW/77-GHz hardware and chirp parameters with provenance and evidence type.
T2 derived physical limits for each operating profile.
T3 policy definitions, information access and physical-gating behavior.
T4 frozen aggregate results with confidence intervals.
T5 per-regime violation/failure rates.
T6 ablations and runtime/complexity.

## Current pilot evidence

Stage 7 already contains diagnostic simulation evidence showing that the 858-MHz parking-style profile has approximately 0.175 m range resolution but only approximately 8.4 m/s monostatic unambiguous radial velocity. A published 77-GHz one-way Doppler example of 5.1 kHz corresponds to approximately 19.86 m/s and therefore lies outside that parking profile's velocity region but inside the declared high-mobility capability profile. The multi-chip DBPSK reference also tracks the analytical AWGN curve when residual frequency error is zero.

These pilot values are implementation evidence only and are not yet frozen paper results.

## Submission rule

Do not write a positive conclusion before the frozen experiments. Negative or regime-dependent findings remain reportable. External hardware measurements remain external measurements; this repository's Monte-Carlo outputs remain simulations. The Oracle is never described as deployable.
