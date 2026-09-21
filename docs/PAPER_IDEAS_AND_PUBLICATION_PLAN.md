# Paper Ideas and Publication Plan

## Purpose

This document turns the current `adaptive-pc-fmcw-isac` repository into a publication roadmap. It records the paper ideas that can reasonably emerge from the project, identifies which idea is strongest, separates one publishable story from possible follow-up work, and states what experimental evidence is required before making each claim.

The repository currently studies a 77-GHz vehicular phase-coded FMCW integrated sensing and communication (PC-FMCW ISAC) PHY. The proposed research layer is **adaptive PHY configuration under physical feasibility limits, high mobility, and imperfect PHY-state knowledge**. It is not a new claim for PC-FMCW itself, ISAC itself, generic adaptive waveform design, generic robust optimization, or generic reliability constraints.

---

# Executive answer: which paper should we write first?

## Recommended main paper

**Physics-Gated Reliability-Constrained Adaptive Phase-Coded FMCW ISAC for High-Mobility Vehicular Links**

This is the strongest and most coherent paper idea in the repository.

### Central research question

> **When the vehicular PHY state is uncertain, does physics-gated reliability-constrained PC-FMCW adaptation maintain joint sensing and communication QoS more reliably than fixed, single-objective, or deterministic joint adaptation, and what resource cost is required to maintain that reliability across the physically feasible operating region?**

### Main scientific comparison

The most important controlled comparison is:

```text
B3 — deterministic joint ISAC adaptation
                 versus
B4 — physics-gated robust joint ISAC adaptation
```

B3 uses the estimated state as if it were exact. B4 explicitly accounts for uncertainty and only optimizes over configurations that satisfy the physical FMCW feasibility gate.

If B4 substantially reduces joint-QoS violations under uncertainty while incurring a measurable and interpretable resource cost, the paper has a clear result.

### One-sentence paper idea

> **We study whether a high-mobility PC-FMCW ISAC transceiver should first eliminate physically incapable PHY profiles and then adapt only among the remaining profiles using probabilistic joint sensing/communication reliability constraints.**

---

# Why this can be a paper

The individual ingredients are not new by themselves. Prior literature already contains:

- phase-coded FMCW sensing and communication;
- FMCW-based vehicular ISAC;
- adaptive ISAC waveform/profile selection;
- robust ISAC waveform design;
- Doppler-resilient ISAC;
- sensing/communication threshold constraints;
- outage/chance-constrained robust ISAC;
- vehicular ISAC optimization.

The narrower intersection investigated here is:

```text
PC-FMCW-specific physical capability
        +
high-mobility uncertain operating state
        +
finite online PHY profile selection
        +
joint probabilistic communication/sensing QoS
        +
resource-aware adaptation
        +
feasible operating-region characterization
```

The novelty should be argued at the level of this **ordered architecture and research question**, not by claiming any one ingredient as new.

A conservative positioning statement is:

> **Prior work has established phase-coded/FMCW ISAC, adaptive and robust ISAC waveform design, Doppler-resilient signaling, and sensing-communication QoS optimization. Comparatively less attention has been given to online PC-FMCW configuration selection in which candidate profiles are first screened by waveform/receiver physics and then selected according to joint probabilistic sensing-and-communication reliability under uncertain high-mobility vehicular conditions.**

---

# The proposed architecture

```text
True high-mobility operating state
(range, velocity, SNR, interference, synchronization, etc.)
                    |
                    v
        imperfect PHY-state estimate
                    |
                    v
       +---------------------------+
       | PC-FMCW physics gate      |
       |                           |
       | range support             |
       | IF / sampling support     |
       | unambiguous velocity      |
       | profile capability        |
       +-------------+-------------+
                     |
              feasible profiles
                     |
                     v
       +---------------------------+
       | reliability-constrained   |
       | joint ISAC selection      |
       +-------------+-------------+
                     |
            selected PHY action
                     |
          +----------+----------+
          |                     |
          v                     v
 communication QoS        sensing QoS
 BER / PER / rate      range / velocity RMSE
```

The ordering is important. Reliability optimization cannot rescue a configuration that is physically incapable of representing the requested range/velocity state.

---

# Paper Idea 1 — Main recommended paper

## Physics-Gated Reliability-Constrained Adaptive PC-FMCW ISAC

### Hypothesis

A deterministic adaptive controller can select configurations that appear satisfactory at the estimated state but violate joint QoS when the true state differs from the estimate. Furthermore, an optimizer that ignores PC-FMCW physical limits may evaluate or select configurations that are fundamentally unsuitable for the current range/velocity state.

A physics-gated uncertainty-aware controller should therefore reduce joint-QoS violations, at the cost of additional PHY resources or more conservative profile selection.

### Proposed controller

```text
minimize_a     C_resource(a)

subject to     a in A_physics(state)
               P[BER(a,S) <= epsilon_comm] >= 1-alpha
               P[RMSE_range(a,S) <= delta_r] >= 1-beta_r
               P[RMSE_velocity(a,S) <= delta_v] >= 1-beta_v
               P[joint QoS(a,S)] >= 1-eta
               R_eff(a,S) >= R_min, when required
```

### Required baselines

- **B0 Fixed PHY** — one configuration for all operating states.
- **B1 Communication-only adaptive** — optimize communication QoS/cost without sensing requirement.
- **B2 Sensing-only adaptive** — optimize sensing QoS/cost without communication requirement.
- **B3 Deterministic joint ISAC** — joint sensing/communication adaptation, estimated state treated as exact.
- **B4 Robust joint ISAC (proposed)** — physics gate plus uncertainty-aware joint reliability constraints.
- **Oracle** — true state available to the selector; evaluation bound only.

### Figures that should carry the paper

1. **Joint QoS violation probability vs. state uncertainty.**
2. **SNR × radial-velocity feasibility map.**
3. **Range × radial-velocity physical-profile feasibility map.**
4. **Interference × residual-CFO/synchronization feasibility map.**
5. **Reliability target vs. required resource cost.**
6. **B0–B4 + Oracle joint reliability comparison.**
7. **Profile-selection frequency over the operating region.**
8. **Communication–sensing–resource Pareto frontier.**
9. **Runtime / decision complexity.**

### What result would make the paper convincing?

The ideal result is not simply “B4 has lower BER.” A stronger result is:

> **B3 satisfies nominal QoS at the estimated state but increasingly violates joint QoS as uncertainty/high mobility grows, whereas B4 maintains the declared reliability target over a substantially larger physically feasible operating region, with a quantifiable resource premium.**

That establishes both a benefit and its cost.

### Publication gate

This paper should not be submitted until:

- the communication receiver matches analytical DBPSK behavior in the appropriate reference case;
- the FMCW range/Doppler simulator passes analytical sanity checks;
- physical feasibility calculations are independently verified;
- B0–B4 use exactly the same candidate action set and scenario support;
- final experiments use independent large-seed Monte Carlo evaluation;
- confidence intervals and paired statistical comparisons are reported where appropriate;
- uncertainty, interference, CFO/synchronization and model-mismatch ablations are complete;
- feasibility maps and Pareto curves are generated;
- runtime is measured;
- all final configurations and results are frozen in a reproducible release/tag.

### Verdict

**Best first paper.** It has one coherent question, clear baselines, a specific PC-FMCW/high-mobility identity, and results that can go beyond a simple percentage-improvement benchmark.

---

# Paper Idea 2 — Feasible-region / design-space paper

## Operating Limits of High-Mobility PC-FMCW ISAC

A second possible story is to focus less on the controller and more on **where PC-FMCW can and cannot simultaneously satisfy vehicular sensing and communication requirements**.

### Research question

> **How do FMCW physical limits, communication reliability, sensing accuracy, Doppler/synchronization impairment and resource constraints partition the operating space of a high-mobility PC-FMCW ISAC system into feasible and infeasible regions?**

### Core outputs

- range × velocity feasibility boundaries;
- SNR × velocity joint-QoS maps;
- interference × CFO maps;
- bandwidth/chirp/repetition/chip-budget sensitivity;
- minimum resource cost required at each operating state;
- causes of infeasibility: physics-limited vs. reliability-limited vs. resource-limited.

### Why it is interesting

A major design insight is that good nominal range resolution does not imply high-mobility suitability. For example, a profile can have excellent range resolution while its chirp repetition interval makes its maximum unambiguous radial velocity unsuitable for the operating state.

### Risk

By itself this can become a parameter-sweep paper rather than an algorithmic contribution. It is strongest as a major section/result of Paper Idea 1. It should become a separate paper only if the analytical feasibility theory and design rules become deep enough to stand independently.

### Verdict

**Do not split this out yet.** Use it to strengthen the main paper first.

---

# Paper Idea 3 — Uncertainty / reliability paper

## The Cost of Reliability in Adaptive PC-FMCW ISAC

This possible follow-up would focus on the relationship between reliability target, uncertainty and resource cost.

### Research question

> **What additional power, coding/chip budget, repetitions or profile capability must a PC-FMCW ISAC system spend to guarantee increasingly stringent joint sensing/communication reliability under imperfect state knowledge?**

### Main concept

Define a reliability premium such as

```text
Reliability premium
    = resource cost of robust reliable policy
      - resource cost of nominal deterministic policy
```

and characterize it over uncertainty and mobility.

### Potential results

- resource cost vs. target reliability;
- reliability premium vs. state-estimation error;
- reliability premium vs. radial velocity;
- regions where increasing resources helps;
- regions where resources cannot help because the waveform/profile is physically infeasible;
- gap to Oracle.

### Verdict

**Potential follow-up paper**, but probably not enough reason to split from Paper Idea 1 until the first results reveal a strong standalone law/trade-off.

---

# Paper Idea 4 — Model mismatch / robust deployment study

## Robust PC-FMCW Adaptation Beyond the Assumed Uncertainty Model

A more mature follow-up could ask whether the robust selector remains reliable when the assumed state/noise model is wrong.

### Research question

> **How sensitive is reliability-constrained PC-FMCW adaptation to mismatch between the uncertainty distribution used by the controller and the true operating distribution?**

Possible mismatches:

- heavier-tailed SNR errors;
- biased Doppler estimates;
- residual CFO outside the assumed distribution;
- burst/intermittent interference;
- phase-noise mismatch;
- correlated state errors.

### Verdict

Scientifically useful, but **not the first paper**. First establish that the base B4 method works under a controlled declared model.

---

# Paper Idea 5 — Hardware / SDR validation extension

## Experimental Adaptive PC-FMCW ISAC

The strongest long-term extension would validate the adaptation framework on an RF/SDR or radar-capable platform.

### Possible contribution

Move from:

```text
model-based Monte Carlo reliability
```

to:

```text
measured PHY state
 -> physics gate
 -> adaptive profile selection
 -> measured communication/sensing outcome
```

### Why this would be stronger

The current repository is explicitly a model-based simulation study. Hardware validation would answer whether model-based feasibility and reliability boundaries predict measured behavior.

### Verdict

**High-value future paper**, but it requires a separate experimental campaign and should not be implied by current simulation results.

---

# Which ideas should be one paper and which should not?

## Main paper should combine

Paper Idea 1 should include the strongest parts of Ideas 2 and 3:

```text
physics-gated robust adaptation
        +
feasible operating-region characterization
        +
resource cost of reliability
```

These belong together because they answer one scientific question:

> **When is reliable joint operation possible, how should the PHY adapt when it is possible, and what does that reliability cost?**

Trying to publish three thin papers from these components would weaken the contribution.

## Keep for follow-up

- severe model-mismatch/distribution-shift study;
- hardware/SDR validation;
- substantially more advanced adaptive/learning controller if later justified.

---

# Proposed paper narrative

## Introduction story

1. PC-FMCW can integrate sensing and communication.
2. Vehicular high mobility changes range, Doppler, synchronization and communication conditions rapidly.
3. A fixed configuration cannot be assumed to remain suitable over the full operating region.
4. Existing adaptive/robust ISAC literature means adaptation and robustness cannot be claimed as new in general.
5. PC-FMCW introduces concrete physical capability limits: sampling/IF support, range support and unambiguous velocity.
6. Therefore, adaptation should not start by optimizing every candidate. It should first identify what is physically possible.
7. Even among physically feasible profiles, estimated state is imperfect, so nominal joint optimization may not provide the requested reliability.
8. This motivates **physics-gated reliability-constrained PC-FMCW adaptation**.

## Central experiment

```text
Fixed             B0
Comm-only         B1
Sensing-only      B2
Deterministic     B3
Robust proposed   B4
Perfect-state     Oracle
```

The paper should demonstrate not only average performance, but **constraint satisfaction, feasible-region expansion/contraction, resource cost and failure modes**.

---

# Candidate contribution statements

A future manuscript can tentatively use contributions along the following lines, subject to final results and literature verification.

1. **Physics-gated PC-FMCW adaptation.** We formulate adaptive profile selection in which configurations that violate FMCW range, IF/sampling or unambiguous-velocity capability are removed before joint ISAC optimization.

2. **Joint reliability under high-mobility PHY uncertainty.** We formulate uncertainty-aware sensing and communication reliability constraints for finite PC-FMCW configuration selection under varying SNR, Doppler/residual CFO, interference, synchronization and state-estimation uncertainty.

3. **Operating-region characterization.** We characterize where joint communication/sensing QoS is physically and statistically feasible and identify whether failure is caused by waveform capability, uncertainty/reliability, or resource limits.

4. **Cost-of-reliability analysis.** We quantify the additional PHY resource cost required to maintain joint reliability relative to deterministic adaptation and compare the deployable policy with a perfect-state Oracle bound.

Do not freeze these claims until the final experiments support them.

---

# Claims we must NOT make

Do not claim:

- first PC-FMCW sensing and communication system;
- first adaptive ISAC system;
- first adaptive FMCW ISAC waveform;
- first robust ISAC design;
- first chance-constrained/reliability-constrained ISAC;
- first Doppler-aware ISAC;
- first vehicular ISAC optimization;
- real 77-GHz measured performance from simulation;
- guaranteed real-world reliability from Monte Carlo results.

The safe novelty is the **specific PC-FMCW/high-mobility physics-gated robust adaptation formulation and the resulting operating-region analysis**.

---

# Closest literature and how it affects the paper

The detailed bibliography is maintained in `docs/RELATED_WORK_AND_BIBLIOGRAPHY.md`. Particularly important neighbors include:

- Kumbul et al. — experimental PC-FMCW sensing and communications;
- Kumbul et al. — PC-FMCW sensing/communication performance trade-offs;
- Temiz et al. — FMCW-based vehicular ISAC with dynamically adjustable waveform parameters;
- Wang et al. — robust ISAC waveform design under uncertainty;
- Zhang et al. — robust monostatic ISAC with outage constraints;
- Ni et al. — simultaneous sensing/communication threshold constraints;
- Wang et al. — Doppler-resilient ISAC waveform design;
- Li et al. — vehicular ISAC waveform optimization;
- Yazar et al. — adaptive waveform selection for ISAC.

These papers mean that the manuscript must explicitly distinguish **generic adaptation/robustness** from the proposed **PC-FMCW-specific physics-gated reliability architecture**.

---

# Experiments needed before deciding that the paper is ready

## Phase A — physical validation

- verify chirp slope, beat-frequency and IF sampling relationships;
- verify maximum range calculations;
- verify range resolution;
- verify unambiguous radial velocity;
- verify velocity resolution;
- test edge cases around the feasibility boundaries.

## Phase B — communication validation

- DBPSK AWGN BER vs. analytical result;
- BER vs. residual CFO/Doppler;
- interference sensitivity;
- synchronization sensitivity;
- effective-rate accounting.

## Phase C — sensing validation

- single-target range estimation;
- velocity estimation;
- RMSE vs. SNR;
- RMSE vs. Doppler/profile;
- failure near physical ambiguity limits.

## Phase D — policy study

- B0–B4 + Oracle on common support;
- uncertainty sweep;
- high-mobility sweep;
- reliability-target sweep;
- interference/CFO sweep;
- profile-selection statistics;
- no-feasible-action probability;
- resource-cost comparison.

## Phase E — robustness

- model mismatch;
- biased state estimates;
- heavy-tailed errors where appropriate;
- parameter sensitivity;
- action-space ablations;
- remove-physics-gate ablation;
- remove-uncertainty-awareness ablation.

## Phase F — publication statistics

- frozen independent seeds;
- sufficiently large Monte Carlo sample;
- confidence intervals;
- paired tests where comparisons are paired;
- effect sizes, not only p-values;
- multiplicity control where many formal comparisons are tested;
- runtime/complexity reporting.

---

# Critical ablations

Two ablations are especially important because they directly test the claimed novelty.

## Ablation A — remove the physics gate

Compare B4 with an otherwise identical robust selector that does not perform PC-FMCW physical feasibility screening.

Question:

> Does explicit physical gating prevent invalid profile selections or change the feasible operating region in a meaningful way?

If the answer is no, the “physics-gated” contribution is weak and the paper should be reframed.

## Ablation B — remove uncertainty awareness

This is essentially B3 vs. B4.

Question:

> Does uncertainty-aware reliability control materially reduce joint-QoS violations compared with nominal deterministic adaptation?

If the answer is no, the robust-reliability contribution is weak.

These two experiments are publication-critical.

---

# What outcomes would change the paper story?

## Strong outcome

- physics gate removes meaningful invalid/unsuitable actions;
- B4 maintains target joint reliability under uncertainty;
- B3 increasingly violates QoS as uncertainty grows;
- B4 has an interpretable resource premium;
- Oracle shows remaining room but B4 is reasonably close;
- feasibility maps expose clear physical and statistical boundaries.

**Result:** strong main paper story.

## Mixed outcome 1 — physics gate matters, robustness does not

Then reposition toward **PC-FMCW operating-region / feasibility-aware adaptation** rather than robust reliability.

## Mixed outcome 2 — robustness matters, physics gate rarely activates

Then the main story becomes **reliability-constrained adaptive PC-FMCW under high-mobility uncertainty**, while physics gating becomes implementation discipline rather than headline novelty.

## Mixed outcome 3 — B4 is extremely conservative

If B4 meets reliability only by spending excessive resources or declaring infeasibility too often, the interesting paper may become a **reliability–resource trade-off** study rather than a superiority claim.

## Negative outcome

If B3 and B4 behave nearly identically over realistic uncertainty ranges and the physics gate almost never changes the candidate set, the current novelty claim is not supported. Do not force a positive paper claim; revise the action space, uncertainty model, operating regime, or research question based on the evidence.

---

# Recommended paper structure

```text
I.   Introduction
II.  Related Work
III. PC-FMCW System and High-Mobility PHY Model
IV.  Physical Feasibility Region
V.   Reliability-Constrained Adaptive PHY Selection
VI.  Experimental Methodology and Baselines
VII. Results
     A. Receiver/model validation
     B. Physical feasibility maps
     C. B0-B4 + Oracle
     D. Uncertainty and mobility
     E. Cost of reliability / Pareto analysis
     F. Ablations and model mismatch
     G. Runtime
VIII. Discussion and Limitations
IX.  Conclusion
```

---

# Suggested figures for a manuscript

```text
Fig. 1  System architecture and physics-gated adaptation loop
Fig. 2  PC-FMCW candidate profiles and physical capability boundaries
Fig. 3  Communication/sensing receiver validation
Fig. 4  Range × velocity feasibility map
Fig. 5  SNR × velocity joint-QoS map
Fig. 6  Joint-QoS violation vs. uncertainty: B0-B4 + Oracle
Fig. 7  Reliability target vs. resource cost
Fig. 8  Interference × residual-CFO robustness map
Fig. 9  Pareto frontier
Fig. 10 Ablations: no physics gate / no uncertainty awareness
```

---

# Venue direction

The exact venue should be chosen only after the final results reveal whether the strongest contribution is waveform/PHY, vehicular communications, signal processing, or an ISAC systems study. The manuscript should be written first around the scientific question rather than tailored prematurely to a venue.

A simulation-only study needs especially strong model validation, baselines, ablations, operating-region insight and reproducibility. Hardware validation would materially broaden the venue options and strengthen the claims.

---

# Relationship to the separate robotics-planning project

This repository should remain scientifically distinct from `pc-fmcw-robotics-planning`.

```text
adaptive-pc-fmcw-isac
    PHY state -> PC-FMCW configuration

pc-fmcw-robotics-planning
    predicted link state -> ego vehicle motion
```

The first paper asks **how the PC-FMCW PHY should adapt**.

The robotics paper asks **how the vehicle should move when future connectivity is predicted**.

They can later motivate a larger cross-layer system, but combining both into the first manuscript would make attribution of gains and novelty harder.

---

# Final recommendation

## Paper to pursue now

**Physics-Gated Reliability-Constrained Adaptive Phase-Coded FMCW ISAC for High-Mobility Vehicular Links**

## Core claim to test

> **Physics-gated uncertainty-aware adaptation can maintain declared joint sensing/communication reliability over a larger useful high-mobility operating region than nominal deterministic adaptation, while exposing the resource cost and the states in which reliable operation is physically impossible.**

This is a hypothesis until the frozen final experiments confirm it.

## Main comparison

```text
B3 deterministic joint adaptation
              vs.
B4 physics-gated robust adaptation
```

## Main outputs

```text
joint reliability
+ physical feasibility region
+ resource cost
+ uncertainty/high-mobility robustness
+ Oracle gap
```

## Follow-up possibilities

1. deeper reliability-premium / model-mismatch analysis if the results reveal a strong standalone phenomenon;
2. RF/SDR or radar-platform experimental validation;
3. eventual cross-layer coupling to the separate predictive robotics-planning project.

The goal is **one strong, coherent first paper rather than several weakly separated papers**.
