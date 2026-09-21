# Research Contribution and Positioning

## Working paper title

**Physics-Gated Reliability-Constrained Adaptive Phase-Coded FMCW ISAC for High-Mobility Vehicular Links**

## Relationship to prior PC-FMCW ISCAI work

The immediate conceptual predecessor is the 2025 IEEE Photonics Technology Letters work **“Phase-coded FMCW Laser Headlamp for Integrated Sensing, Communication, and Illumination.”** That work demonstrates an optical laser-headlamp ISCAI architecture in which DPSK data are embedded in an FMCW phase term, the reflected optical signal supports sensing, and the headlamp also supports adaptive illumination. Its reported system-level objectives include gigabit-per-second communication, centimeter-level ranging, adaptive driving beam illumination, and multidimensional-Hough-transform track-before-detect processing.

The present project does **not** claim novelty for the general idea of phase-coded FMCW joint sensing and communication, DPSK embedding in FMCW, range-Doppler processing, or integrated vehicular sensing/communication by themselves.

Instead, this work moves the research question from **functional integration / feasibility** to **reliable adaptive operation under high-mobility PHY uncertainty**.

### Prior question

> Can a PC-FMCW platform simultaneously provide sensing and communication (and, in the optical headlamp implementation, illumination)?

### Question addressed here

> Given a high-mobility vehicular operating state and imperfect knowledge of that state, which physically feasible PC-FMCW PHY configuration should be selected so that communication reliability and sensing accuracy are jointly satisfied with a declared probability while resource cost is controlled?

This distinction is central to every paper claim, experiment, figure, and baseline.

## Independent scientific identity

This repository studies an **RF/mmWave 77-GHz vehicular PC-FMCW ISAC PHY**. It is deliberately separated from the optical laser-headlamp/illumination architecture.

The project therefore excludes:

- adaptive driving beam (ADB) illumination;
- optical headlamp control;
- trajectory forecasting;
- ego-motion planning;
- packet/user scheduling;
- beam-management policies;
- multidimensional Hough tracking as a proposed contribution.

The unit of adaptation is the **physical-layer PC-FMCW configuration**, not the vehicle trajectory, packet queue, beam direction, or illumination pattern.

## Core hypothesis

A PC-FMCW configuration that appears attractive from an average BER, sensing-RMSE, or resource perspective may be unusable because of fundamental FMCW range/velocity/sampling limits or may violate QoS once PHY-state uncertainty is considered.

Therefore, robust adaptation should be decomposed into two ordered decisions:

1. **physics feasibility gate:** remove configurations that cannot physically support the requested operating state;
2. **reliability-constrained selection:** optimize only over the remaining configurations while accounting for uncertain channel and impairment state.

## Proposed contributions

### C1 — Physics-gated PC-FMCW adaptation

We introduce a feasibility layer based on declared waveform and receiver physics before policy optimization. Candidate configurations are screened using quantities including bandwidth, chirp slope, IF sampling support, range resolution, maximum supported range, chirp repetition interval, Doppler support and maximum unambiguous radial velocity.

This prevents an optimizer from selecting a numerically inexpensive configuration that cannot represent the required range or velocity even in the absence of noise.

### C2 — Joint reliability constraints under imperfect PHY knowledge

Let `a` denote a candidate PC-FMCW configuration and `S` the uncertain physical/link state. The proposed controller targets constraints of the form

```text
P[BER(a,S) <= epsilon_comm]                >= 1 - alpha
P[RMSE_range(a,S) <= delta_range]          >= 1 - beta_range
P[RMSE_velocity(a,S) <= delta_velocity]    >= 1 - beta_velocity
P[joint communication+sensing QoS]         >= 1 - eta
```

with effective-rate and resource constraints where appropriate.

The state may include SNR/EbN0, Doppler or residual frequency error, interference, phase noise and estimation uncertainty. The robust controller therefore differs from deterministic adaptation that treats an estimated state as exact.

### C3 — Joint feasible operating-region characterization

The principal result is not intended to be only a percentage improvement over a fixed baseline. The study characterizes where the joint QoS problem is physically and statistically feasible.

Examples include:

- SNR × radial-velocity feasibility;
- interference × residual-CFO feasibility;
- uncertainty × reliability-target feasibility;
- range × velocity profile feasibility;
- minimum resource cost conditional on satisfying joint QoS.

These maps expose boundaries where no available PC-FMCW configuration can meet the declared sensing and communication requirements.

### C4 — Communication–sensing–resource trade-off

Among feasible configurations, the framework evaluates the Pareto structure between communication reliability/effective rate, sensing accuracy and PHY resource cost. This provides a reproducible answer to when additional power, coding/chips, chirps, repetitions or a different operating profile are justified.

### C5 — Reproducible high-mobility impairment evaluation

The final evaluation explicitly separates one-way vehicular communication from the monostatic two-way sensing echo and studies high-mobility impairments including Doppler/residual synchronization error, interference, phase noise and state-estimation error. Literature-derived constants, analytical quantities, controlled simulation variables, simulation outputs and external measurements remain separately labelled.

## Optimization statement

A representative finite-action formulation is

```text
minimize_a   C_resource(a)

subject to   a in A_physics(state)
             P[BER(a,S) <= epsilon_comm] >= 1 - alpha
             P[RMSE_range(a,S) <= delta_r] >= 1 - beta_r
             P[RMSE_velocity(a,S) <= delta_v] >= 1 - beta_v
             P[joint QoS(a,S)] >= 1 - eta
             R_eff(a,S) >= R_min, when required.
```

`A_physics(state)` is the configuration set remaining after the physical feasibility gate.

## Baselines required for a defensible contribution

- **B0 Fixed PHY** — one frozen configuration for all states.
- **B1 Communication-only adaptive** — communication QoS only.
- **B2 Sensing-only adaptive** — sensing QoS only.
- **B3 Deterministic joint ISAC** — joint QoS using the estimated state as if exact.
- **B4 Robust joint ISAC (proposed)** — physics gate plus uncertainty-aware joint reliability constraints.
- **Oracle** — true instantaneous state; non-deployable evaluation bound.

All policies must use the same candidate action set, scenario support and evaluation seeds where paired comparison is possible.

## What would *not* constitute sufficient novelty

The following claims must not be used as the main contribution because they are already established concepts or are too generic:

- “we use PC-FMCW for sensing and communication”;
- “we embed DPSK/phase-coded data into an FMCW waveform”;
- “we adapt an ISAC waveform” without a specific robust problem;
- “we optimize sensing and communication jointly” without high-mobility uncertainty and feasibility analysis;
- “we include Doppler/interference/synchronization” only as extra simulation curves;
- “we use chance constraints” without demonstrating why the PC-FMCW/high-mobility physical structure changes the operating region;
- optical ADB or trajectory tracking reused as the new contribution.

## Claim hierarchy

The final manuscript should make claims in the following order:

1. **validated physical model**;
2. **physical feasibility boundaries**;
3. **validated communication and sensing receiver behavior**;
4. **measured simulation reliability under declared uncertainty models**;
5. **policy comparison on identical support**;
6. **feasible-region and Pareto conclusions**;
7. only then, broader implications for high-mobility vehicular PC-FMCW ISAC.

## Claim boundary

This repository currently represents a model-based and Monte-Carlo research study. Source-derived automotive parameters and external measured values are not new measurements by this project. Diagnostic pilot outputs are not publication results until the frozen large-seed protocol, uncertainty/mismatch study, statistical analysis and reproduction bundle are complete.

## One-sentence contribution statement

> **We extend PC-FMCW ISAC from fixed-configuration functional feasibility to physics-gated, reliability-constrained PHY adaptation under high-mobility uncertainty, and characterize the operating region in which vehicular communication and sensing QoS can be jointly guaranteed.**
