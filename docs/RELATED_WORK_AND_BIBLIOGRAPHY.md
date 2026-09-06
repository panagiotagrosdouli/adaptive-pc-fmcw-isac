# Related Work and Bibliography for Adaptive PC-FMCW ISAC

## Purpose

This note records the closest prior work for the paper idea **Physics-Gated Reliability-Constrained Adaptive Phase-Coded FMCW ISAC for High-Mobility Vehicular Links**. The aim is to distinguish which parts are already established in the literature from the narrower combination proposed in this repository.

The current evidence does **not** support a broad claim such as "adaptive ISAC is new", "robust ISAC waveform design is new", or "phase-coded FMCW joint sensing and communication is new". Those areas already have clear prior work.

The more defensible positioning is that the project combines:

```text
phase-coded FMCW vehicular ISAC
        +
PC-FMCW/FMCW-specific physical feasibility limits
        +
high-mobility Doppler / synchronization / interference uncertainty
        +
probabilistic joint sensing-and-communication QoS constraints
        +
finite online PHY configuration selection
        +
feasible-region and resource-cost characterization
```

The proposed contribution should therefore be framed around this **specific system formulation and experimental question**, not around any one of those ingredients in isolation.

---

## Closest prior work

### 1. Phase-coded FMCW for joint sensing and communications

**U. Kumbul, N. Petrov, F. van der Zwan, C. S. Vaucher, and A. Yarovoy, "Experimental Investigation of Phase Coded FMCW for Sensing and Communications," EuCAP 2021.**

This is foundational PC-FMCW work. It experimentally studies phase-coded FMCW as a joint sensing-and-communications waveform and compares receiver structures while retaining automotive-radar relevance.

**Relation to this project:** establishes that PC-FMCW can support both sensing and communications. It does not formulate uncertainty-aware online selection of PHY configurations under joint reliability constraints and explicit operating-state feasibility gates.

---

### 2. PC-FMCW sensing/communication performance trade-offs

**U. Kumbul, N. Petrov, C. S. Vaucher, and A. Yarovoy, "Performance Analysis of Phase-Coded FMCW for Joint Sensing and Communication," International Radar Symposium (IRS), 2023.** DOI: `10.23919/IRS57608.2023.10172426`.

This work compares PC-FMCW processing strategies and explicitly exposes sensing/communication trade-offs, including BER degradation associated with communication bandwidth.

**Relation to this project:** highly relevant to the PHY basis and trade-off motivation. The present project moves from receiver/performance analysis to **state-dependent robust configuration selection**.

---

### 3. FMCW-based vehicular ISAC with dynamically adjustable waveform parameters

**M. Temiz, C. Horne, M. A. Ritchie, and C. Masouros, "FMCW-Based Integrated Sensing and Communication System: Design, Implementation, and Experimental Measurements," IEEE Transactions on Communications, 2026.** DOI: `10.1109/TCOMM.2026.3706482`.

This recent work is especially important. It proposes an FMCW-based vehicular ISAC architecture using phase modulation and index modulation, evaluates Doppler effects, reports simulation and proof-of-concept measurements, and studies the trade-off among communication throughput, sensing accuracy, and out-of-band emission. The authors also show that waveform parameters can be adjusted to meet different operational requirements.

**Relation to this project:** this is a close counterexample to any claim that adaptive/dynamic FMCW-ISAC parameter choice is unexplored. However, the present repository focuses on a different control problem: a **physics-gated finite-action policy that rejects configurations violating FMCW range/velocity/sampling capability and then enforces probabilistic joint sensing/communication QoS under uncertain high-mobility state**.

---

### 4. Robust ISAC waveform design under channel uncertainty

**S. Wang, W. Dai, H. Wang, and G. Y. Li, "Robust Waveform Design for Integrated Sensing and Communication," IEEE Transactions on Signal Processing, vol. 72, pp. 3122-3138, 2024.** DOI: `10.1109/TSP.2024.3410142`.

This is one of the most important robustness references. It studies ISAC waveform design when the true communication channel is uncertain and characterizes robust sensing-communication Pareto frontiers via worst-case design.

**Relation to this project:** establishes that robust ISAC waveform design under uncertainty is not new. The distinction here is the combination of **PC-FMCW-specific feasibility limits, vehicular high-mobility impairments, probabilistic reliability constraints, and online discrete profile/configuration selection**, rather than generic robust waveform design over uncertain channels.

---

### 5. Robust monostatic ISAC with outage constraints and channel uncertainty

**R. Zhang, Y. Gong, C. Chen, A. Nallanathan, K.-K. Wong, and C. Yuen, "Joint MMSE and CRB-Based Robust Beamforming Design for Monostatic ISAC Systems With Channel Uncertainty," IEEE Transactions on Communications, 2026.** DOI: `10.1109/TCOMM.2025.3650390`.

This paper considers imperfect communication-channel knowledge, clutter, sensing objectives based on MMSE/CRB, and communication SINR outage-probability constraints.

**Relation to this project:** directly relevant evidence that probabilistic/outage-constrained robust ISAC optimization already exists. The proposed paper should therefore not claim chance/reliability constraints as a standalone novelty. The novelty must come from the **PC-FMCW/high-mobility physical structure and the physics-gated adaptation problem**.

---

### 6. Joint threshold-constrained sensing and communication waveform optimization

**Z. Ni, A. J. Zhang, R.-P. Liu, and K. Yang, "Doubly Constrained Waveform Optimization for Integrated Sensing and Communications," Sensors, vol. 23, no. 13, 5988, 2023.** DOI: `10.3390/s23135988`.

This work simultaneously imposes sensing and communication performance thresholds, using sensing mutual information and communication sum rate.

**Relation to this project:** demonstrates that simultaneous sensing/communication QoS constraints are already established. Our paper should focus instead on **reliability under uncertain state plus PC-FMCW physical feasibility and vehicular operating-region mapping**.

---

### 7. Ultra-reliable ISAC waveform design

**R. Zhang et al., "Integrated Sensing and Communication Waveform Design With Sparse Vector Coding: Low Sidelobes and Ultra Reliability," IEEE Transactions on Vehicular Technology, vol. 71, no. 4, pp. 4489-4494, 2022.** DOI: `10.1109/TVT.2022.3146280`.

This paper designs a waveform targeting both low radar sidelobes and ultra-reliable communication.

**Relation to this project:** reliability as an ISAC design goal is not new. Our distinct question is whether a **PC-FMCW configuration can be selected online so that declared sensing and communication reliability targets remain satisfied as range, velocity, Doppler/CFO, interference and state uncertainty change**.

---

### 8. Doppler-resilient ISAC waveform design

**J. Wang, P. Fan, Q. Shi, and Z. Zhou, "Doppler Resilient Integrated Sensing and Communication Waveforms Design," Journal of Radars, vol. 12, no. 2, pp. 275-286, 2023.** DOI: `10.12000/jr22155`.

This work explicitly designs ISAC waveforms for Doppler resilience and shows improved moving-target detection and communication error performance.

**Relation to this project:** Doppler-aware/resilient ISAC is therefore not itself novel. Here, Doppler and residual synchronization error are treated as **state/uncertainty variables that affect which PC-FMCW profile is feasible and reliable**, rather than only as a waveform-shaping objective.

---

### 9. Vehicular ISAC waveform optimization

**Z. Li, Z. Ma, and Y. Liang, "Integrated sensing and communication waveform design in the Internet of Vehicles," Vehicular Communications, vol. 44, 100664, 2023.** DOI: `10.1016/j.vehcom.2023.100664`.

This work optimizes an ISAC waveform for an Internet-of-Vehicles setting using sensing and communication objectives with total-power, waveform-similarity and PAPR constraints.

**Relation to this project:** vehicular ISAC waveform optimization is established. The proposed contribution must remain narrower: **high-mobility PC-FMCW profile adaptation with physical feasibility gating and joint reliability constraints under uncertainty**.

---

### 10. Adaptive waveform selection for ISAC

**A. Yazar, Y. I. Demir, A. Naeem, and S. Karatepe, "A Multi-Objective Learning Approach for Adaptive Waveform Selection in Integrated Sensing and Communications Systems," arXiv:2603.14017, 2026.**

This preprint formulates adaptive waveform selection as a multi-objective decision problem and learns Pareto-optimal waveform choices from scenario/network conditions.

**Relation to this project:** this is the closest explicit evidence that **adaptive waveform selection** is already being studied directly. The key distinction is that our action set is tied to **PC-FMCW physical capability**, with hard range/velocity/sampling rejection before optimization and reliability guarantees under high-mobility uncertainty. This reference is a preprint and should be cited as such unless a peer-reviewed version appears.

---

## What appears to be genuinely less explored

Based on the literature above, the individual ingredients already exist:

- PC-FMCW joint sensing and communications;
- FMCW-based vehicular ISAC;
- adaptive waveform selection;
- robust ISAC waveform design;
- outage/chance constraints;
- joint sensing/communication QoS constraints;
- Doppler-resilient ISAC;
- vehicular ISAC optimization.

What appears substantially less explored is the **specific ordered adaptation architecture** used here:

```text
uncertain vehicular operating state
        |
        v
PC-FMCW physical feasibility gate
(range / IF sampling / unambiguous velocity / profile capability)
        |
        v
feasible finite candidate set
        |
        v
joint probabilistic communication + sensing reliability constraints
        |
        v
minimum-cost PHY configuration selection
        |
        v
feasible operating-region / resource-cost characterization
```

A conservative paper statement is therefore:

> **Prior work has established phase-coded/FMCW ISAC, adaptive and robust ISAC waveform design, Doppler-resilient signaling, and sensing-communication QoS optimization. Comparatively less attention has been given to online PC-FMCW configuration selection in which candidate profiles are first screened by waveform/receiver physics and then selected according to joint probabilistic sensing-and-communication reliability under uncertain high-mobility vehicular conditions.**

This should be presented as a **comparatively underexplored intersection**, not as a categorical "first" claim unless a final systematic database search supports stronger language.

---

## Recommended paper research question

> **When the vehicular PHY state is uncertain, does physics-gated reliability-constrained adaptation provide materially better joint sensing/communication reliability than deterministic or single-objective PC-FMCW adaptation, and what resource cost is required to maintain that reliability across the physically feasible operating region?**

The strongest baseline comparison is expected to be:

```text
B3 deterministic joint adaptation
              vs.
B4 physics-gated robust joint adaptation
```

The strongest scientific outputs should be:

1. joint-QoS violation probability versus uncertainty/high mobility;
2. SNR x velocity and range x velocity feasible-region maps;
3. deterministic-vs-robust reliability gap;
4. resource cost required for reliability;
5. probability that no candidate profile is physically feasible;
6. distance from the non-deployable Oracle policy.

---

## Claim language to avoid

Do not use the following as standalone novelty claims:

- "first adaptive ISAC waveform";
- "first robust ISAC waveform design";
- "first reliability-constrained ISAC";
- "first Doppler-aware ISAC";
- "first vehicular ISAC waveform optimization";
- "first phase-coded FMCW sensing-and-communication system".

A safer formulation is:

> **To the best of our current literature review, the combination of PC-FMCW-specific feasibility screening and uncertainty-aware joint reliability-constrained PHY profile selection for high-mobility vehicular operation remains comparatively underexplored.**

---

## Bibliography shortlist

1. U. Kumbul, N. Petrov, F. van der Zwan, C. S. Vaucher, and A. Yarovoy, "Experimental Investigation of Phase Coded FMCW for Sensing and Communications," EuCAP, 2021.
2. U. Kumbul, N. Petrov, C. S. Vaucher, and A. Yarovoy, "Performance Analysis of Phase-Coded FMCW for Joint Sensing and Communication," IRS, 2023, DOI: `10.23919/IRS57608.2023.10172426`.
3. M. Temiz, C. Horne, M. A. Ritchie, and C. Masouros, "FMCW-Based Integrated Sensing and Communication System: Design, Implementation, and Experimental Measurements," IEEE Transactions on Communications, 2026, DOI: `10.1109/TCOMM.2026.3706482`.
4. S. Wang, W. Dai, H. Wang, and G. Y. Li, "Robust Waveform Design for Integrated Sensing and Communication," IEEE Transactions on Signal Processing, 2024, DOI: `10.1109/TSP.2024.3410142`.
5. R. Zhang et al., "Joint MMSE and CRB-Based Robust Beamforming Design for Monostatic ISAC Systems With Channel Uncertainty," IEEE Transactions on Communications, 2026, DOI: `10.1109/TCOMM.2025.3650390`.
6. Z. Ni, A. J. Zhang, R.-P. Liu, and K. Yang, "Doubly Constrained Waveform Optimization for Integrated Sensing and Communications," Sensors, 2023, DOI: `10.3390/s23135988`.
7. R. Zhang et al., "Integrated Sensing and Communication Waveform Design With Sparse Vector Coding: Low Sidelobes and Ultra Reliability," IEEE Transactions on Vehicular Technology, 2022, DOI: `10.1109/TVT.2022.3146280`.
8. J. Wang, P. Fan, Q. Shi, and Z. Zhou, "Doppler Resilient Integrated Sensing and Communication Waveforms Design," Journal of Radars, 2023, DOI: `10.12000/jr22155`.
9. Z. Li, Z. Ma, and Y. Liang, "Integrated sensing and communication waveform design in the Internet of Vehicles," Vehicular Communications, 2023, DOI: `10.1016/j.vehcom.2023.100664`.
10. A. Yazar, Y. I. Demir, A. Naeem, and S. Karatepe, "A Multi-Objective Learning Approach for Adaptive Waveform Selection in Integrated Sensing and Communications Systems," arXiv:2603.14017, 2026.

## Search status

This is a working literature map based on current web/database-accessible records. Before manuscript submission, the bibliography should be cross-checked against IEEE Xplore, Scopus/Web of Science where available, Google Scholar and arXiv, especially for papers published or accepted during 2026. Priority language such as "first" should only be used after that final search.
