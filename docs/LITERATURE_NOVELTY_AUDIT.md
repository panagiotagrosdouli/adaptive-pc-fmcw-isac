# Literature and Novelty Audit

## Purpose

This document defines what the paper may and may not claim. It is intentionally conservative: novelty is assigned only to the specific combination that the final experiments actually support.

## Prior art that constrains our claims

### PC-FMCW sensing and communication already exist

Kumbul, Petrov, van der Zwan, Vaucher and Yarovoy, *Experimental Investigation of Phase Coded FMCW for Sensing and Communications*, EuCAP 2021, experimentally studied PC-FMCW joint sensing/communication and compared receiver structures. Therefore this project must not claim that PC-FMCW JSC itself is new.

### PC-FMCW receiver trade-offs already exist

Kumbul, Petrov, Vaucher and Yarovoy, *Performance Analysis of Phase-Coded FMCW for Joint Sensing and Communication*, IRS 2023, compared phase-lag-compensated group-delay and filter-bank receivers and reported a sensing/communication trade-off involving BER degradation with communication-signal bandwidth. Therefore generic sensing-versus-communication trade-off analysis is not sufficient novelty.

### PC-FMCW code/sensing behavior already exists

Kumbul et al., *Sensing Performance of Different Codes for Phase-Coded FMCW Radars*, EuRAD 2022, studied code-dependent sensing properties and ambiguity/range-profile behavior. Code-family comparison by itself is not our contribution.

### Robust V2X resource allocation with uncertain CSI already exists

Wu, Liu, Yang and Quek, *Robust Resource Allocation for Vehicular Communications With Imperfect CSI*, IEEE TWC 2021, studies robust/chance-constrained V2X resource allocation under channel uncertainty caused by high mobility. Therefore chance constraints, imperfect CSI and robust V2X optimization are not independently novel.

### Optical laser-headlamp PC-FMCW ISCAI already exists

Liu et al., *Phase-coded FMCW Laser Headlamp for Integrated Sensing, Communication, and Illumination*, IEEE Photonics Technology Letters, accepted 2025, integrates optical PC-FMCW communication, sensing and illumination, with DPSK embedding, range-Doppler processing, ADB and MHT tracking. This project does not claim those functions or that architecture as new.

## Narrow novelty hypothesis to test

The defensible novelty hypothesis is the **specific PC-FMCW high-mobility reliability problem**:

> A finite PC-FMCW action set is first screened by waveform/receiver physics, then selected under uncertain high-mobility PHY state using joint communication-and-sensing reliability constraints; the resulting feasible operating region and resource cost are characterized empirically.

This hypothesis is stronger and narrower than “adaptive ISAC,” “robust ISAC,” “PC-FMCW JSC,” or “chance-constrained V2X.”

## Evidence required before making the claim

The final paper may make the above contribution claim only if all of the following are demonstrated:

1. the physics gate removes configurations for a physically meaningful reason and changes decisions in relevant high-mobility states;
2. B4 is evaluated against B0-B3 on exactly the same state/action support;
3. uncertainty is evaluated out-of-sample rather than only through the policy's assumed distribution;
4. feasible/infeasible operating boundaries are reported, including cases where no action satisfies QoS;
5. resource savings are conditioned on reliability rather than reported when reliability is violated;
6. negative cases and model mismatch are retained;
7. statistical uncertainty is reported using paired estimates and confidence intervals;
8. the final wording avoids hardware-validation claims unless new hardware measurements are actually performed.

## Prohibited headline claims

Do not write any of the following without a new, explicit literature audit demonstrating them:

- “the first PC-FMCW ISAC system”;
- “the first adaptive ISAC waveform”;
- “the first robust ISAC optimization”;
- “the first chance-constrained vehicular ISAC method”;
- “hardware-validated” or “experimentally validated” for results produced only by this simulator;
- “guarantees reliability” when reliability is estimated by finite Monte-Carlo sampling.

Prefer wording such as **empirically satisfies the declared reliability target under the evaluated uncertainty model**.

## Current source set

- U. Kumbul et al., EuCAP 2021, DOI: 10.23919/EuCAP51087.2021.9411464.
- U. Kumbul et al., EuRAD 2022, DOI: 10.23919/EuRAD54643.2022.9924751.
- U. Kumbul et al., IRS 2023, DOI: 10.23919/IRS57608.2023.10172426.
- W. Wu et al., IEEE Transactions on Wireless Communications 20(9), 2021, DOI: 10.1109/TWC.2021.3070894.
- S. Liu et al., *Phase-coded FMCW Laser Headlamp for Integrated Sensing, Communication, and Illumination*, IEEE Photonics Technology Letters, accepted version, DOI: 10.1109/LPT.2025.3649597.

This is a minimum audit set, not the final Related Work bibliography. The audit must be refreshed immediately before submission.
