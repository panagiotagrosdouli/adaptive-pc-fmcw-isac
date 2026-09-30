# Deep Literature and Novelty Audit — 2026-09-30

## Executive verdict

**PASS — the paper has a defensible research gap, but only with narrow novelty positioning.**

The literature reviewed through 2026-09-30 establishes all of the following separately:

1. PC-FMCW / phase-modulated FMCW radar and RadCom;
2. experimental PC-FMCW sensing and communication;
3. synchronization and Doppler compensation for PC-FMCW links;
4. adaptive and dynamically reconfigurable FMCW/ISAC waveforms;
5. robust ISAC waveform and beamforming optimization under uncertainty;
6. adaptive/cognitive radar waveform selection;
7. vehicular ISAC as a high-mobility application domain.

Accordingly, the manuscript must **not** claim novelty for any of those ingredients in isolation.

The defensible gap is their specific operational composition:

> **An admissibility-first PC-FMCW vehicular PHY in which deterministic range, IF-sampling, and unambiguous-velocity limits remove physically unsupported actions before a finite-action, uncertainty-aware joint sensing/communication reliability decision, with confidence-qualified acceptance, explicit abstention, and reliability–availability–computation operating-region characterization.**

The literature pass did not identify a verified publication that combines all of those dimensions in the same PC-FMCW control architecture. This is a scoped literature conclusion, not a universal first-of-kind claim.

---

## Search scope and method

Search date: **2026-09-30**.

The audit used targeted scholarly web searches across publisher pages, IEEE-indexed metadata, university research portals, DOI records, arXiv, DBLP, and open-access full-text/metadata where available.

Search families included combinations of:

- "phase-coded FMCW" + ISAC / RadCom / vehicular / adaptive / synchronization;
- "phase-modulated FMCW" + sensing + communication;
- "FMCW ISAC" + adaptive waveform / dynamic reconfiguration / vehicular;
- robust ISAC waveform design + uncertainty;
- chance-constrained ISAC;
- cognitive radar + adaptive waveform selection;
- high-mobility ISAC + adaptive waveform;
- unambiguous velocity + waveform selection / FMCW adaptation;
- reliability / abstention / selective operation in ISAC.

This is a strong targeted literature audit, but it is **not equivalent to a formal systematic review over subscription databases such as Scopus and Web of Science**. The manuscript should therefore avoid categorical wording such as "the first ever".

---

## Closest prior-work families

### 1. Automotive PC-FMCW foundation

**Uysal, 2020 — IEEE Transactions on Vehicular Technology**  
"Phase-Coded FMCW Automotive Radar: System Design and Interference Mitigation"  
DOI: 10.1109/TVT.2019.2953305

Establishes automotive PC-FMCW system design and interference mitigation. This directly prevents any claim that automotive PC-FMCW itself is novel.

**Uysal and Orru, 2020 — IEEE Radar Conference**  
"Phase-Coded FMCW Automotive Radar: Application and Challenges"  
DOI: 10.1109/RADAR42522.2020.9114798

Addresses multi-bit phase coding within chirps and practical sensing challenges.

**Novelty impact:** foundational, but not adaptive uncertainty-aware joint-QoS control.

---

### 2. PC-FMCW synchronization and practical RadCom

**Lampel et al., 2020 — EuCAP**  
"System Level Synchronization of Phase-Coded FMCW Automotive Radars for RadCom"  
DOI: 10.23919/EuCAP48036.2020.9135417

Demonstrates synchronization of automotive PC-FMCW RadCom units using automotive-grade mmWave radar hardware.

**Alami El Dine et al., 2024 — ICMIM**  
"A Joint Radar and Communication Approach Based on Phase-Coded FMCW Chirp Sequences"  
IEEE Xplore document: 10654233

Uses phase-coded FMCW chirp sequences, correlation-based synchronization, Doppler phase-error compensation, and 25-GHz measurements.

**Alami El Dine et al., 2026 — GeMiC**  
"Synchronization Method for High-Data-Rate Communication Using Phase-Coded FMCW in Incoherent Joint Sensing and Communication Systems"  
DOI: 10.1109/GeMiC71240.2026.11516397

Provides Costas-loop-based synchronization for high-data-rate PC-FMCW communication and validates it with simulation and 25-GHz measurements.

**Novelty impact:** synchronization/CFO/Doppler handling cannot be presented as a new ingredient. Our distinction is that residual synchronization uncertainty is one state dimension inside a reliability-qualified adaptive controller.

---

### 3. Kumbul PC-FMCW sensing/communication line

The Kumbul et al. sequence establishes much of the waveform-specific prior art:

- Experimental Investigation of Phase Coded FMCW for Sensing and Communications, EuCAP 2021, DOI 10.23919/EuCAP51087.2021.9411464.
- Receiver Structures for Phase Modulated FMCW Radars, EuCAP 2022, DOI 10.23919/EuCAP53622.2022.9769268.
- Sensing Performance of Different Codes for Phase-Coded FMCW Radars, EuRAD 2022, DOI 10.23919/EuRAD54643.2022.9924751.
- Smoothed Phase-Coded FMCW: Waveform Properties and Transceiver Architecture, IEEE TAES 2023, DOI 10.1109/TAES.2022.3206173.
- Phase-Coded FMCW for Coherent MIMO Radar, IEEE TMTT 2023, DOI 10.1109/TMTT.2022.3228950.
- Performance Analysis of Phase-Coded FMCW for Joint Sensing and Communication, IRS 2023, DOI 10.23919/IRS57608.2023.10172426.
- Automotive Radar Interference Mitigation using Phase-Coded FMCW Waveform, JC&S 2024, DOI 10.1109/JCS61227.2024.10646233.

**Novelty impact:** waveform feasibility, receivers, phase-code effects, MIMO, and interference are prior art. The paper must be positioned as an adaptive operating-region/control study, not a waveform invention.

---

### 4. Recent phase-/index-modulated FMCW ISAC

**Bönsch et al., 2025 — IEEE JC&S**  
"Evaluating Communication and Sensing Quality in Phase-Modulated FMCW Radar"  
DOI: 10.1109/JCS64661.2025.10880648

Directly relevant to practical sensing/communication quality in phase-modulated FMCW.

**Bönsch et al., 2026 — MIKON**  
"Enabling Integrated Sensing and Communication with Index-Modulated FMCW Radar"  
DOI: 10.23919/MIKON66970.2026.11577911

Extends FMCW-based communication embedding through index modulation.

**Novelty impact:** reinforces that phase/index-modulated FMCW ISAC performance evaluation is established. It does not, based on the verified metadata reviewed here, provide the manuscript's admissibility-first reliability/abstention architecture.

---

### 5. Temiz et al. — the closest FMCW-ISAC threat

**Temiz et al., 2026 — IEEE ICC**  
"Improved Data Rates for Radar-centric ISAC with Index and Phase Modulations"  
DOI: 10.1109/ICC59461.2026.11586917

Uses index and phase modulation and explicitly supports dynamic reconfiguration of chirp duration, bandwidth, and phase coding to trade communication throughput against sensing performance.

**Temiz et al., 2026 — IEEE Transactions on Communications**  
"FMCW-Based Integrated Sensing and Communication System: Design, Implementation, and Experimental Measurements"  
DOI: 10.1109/TCOMM.2026.3706482

This is the strongest recent overlap. It presents a radar-centric vehicular FMCW ISAC system using phase and index modulation, develops radar/communication receiver processing, evaluates Doppler effects, dynamically adjusts waveform parameters, and includes proof-of-concept hardware measurements.

### Why it does not eliminate the present gap

The verified description is centered on waveform architecture, communication throughput, sensing accuracy, out-of-band emission, receiver processing, and flexible parameter reconfiguration.

The present paper instead asks a control/reliability question:

- Is an action physically capable of representing the requested range and radial velocity?
- If physically admissible, is its **joint** communication+sensing QoS supported under state uncertainty?
- Is the finite-sample evidence strong enough to meet a declared reliability threshold?
- If not, should the controller explicitly abstain?

The manuscript should treat Temiz 2026 TCOM as a **closest prior work**, not as a peripheral citation.

Threat level: **HIGH, but distinguishable.**

---

### 6. Adaptive waveform selection is established

**Jin et al., 2018 — Digital Signal Processing**  
"Adaptive waveform selection for maneuvering target tracking in cognitive radar"  
DOI: 10.1016/j.dsp.2018.01.012

Builds a waveform library and selects a waveform adaptively according to target tracking criteria.

**Tholeti et al., 2024 — arXiv**  
"Online waveform selection for cognitive radar"  
DOI: 10.48550/arXiv.2410.10591

Uses online learning to select radar waveform bandwidth according to target/trajectory feedback.

**Novelty impact:** the word "adaptive" cannot carry the novelty claim. The contribution must be the structure and reliability semantics of the PC-FMCW decision process.

---

### 7. Robust ISAC waveform design is established

**Wang et al., 2024 — IEEE Transactions on Signal Processing**  
"Robust Waveform Design for Integrated Sensing and Communication"  
DOI: 10.1109/TSP.2024.3410142

A particularly important conceptual neighbor. It shows that under communication-channel uncertainty, the nominal sensing/communication Pareto frontier is not the true operating frontier and develops robust waveform design to characterize a conservative lower frontier.

### Difference from the present work

Wang et al. is continuous robust waveform design under channel uncertainty. The present work is a discrete PC-FMCW PHY controller with:

- waveform-specific hard capability filtering before ranking;
- finite interpretable actions;
- communication and sensing QoS thresholds;
- finite-sample confidence qualification;
- explicit abstention;
- separate reporting of physical infeasibility, statistical abstention, and selected-action failure.

Threat level: **HIGH conceptually, low waveform-specific overlap.**

---

### 8. Robust beamforming / V2X uncertainty

Representative references include:

- Lyu et al., "Dual-Robust Integrated Sensing and Communication: Beamforming Under CSI Imperfection and Location Uncertainty," IEEE WCL 2024, DOI 10.1109/LWC.2024.3454728.
- Xu et al., "Robust Beamforming Design for Integrated Sensing and Communication Systems," IEEE JSAS 2024, DOI 10.1109/JSAS.2024.3421391.
- Wu et al., "Robust Resource Allocation for Vehicular Communications With Imperfect CSI," IEEE TWC 2021, DOI 10.1109/TWC.2021.3070894.

**Novelty impact:** robust optimization, uncertainty sets, and QoS protection are established. The manuscript's novelty is not "we use robustness"; it is the PC-FMCW admissibility-first decision architecture and its operating-region consequences.

---

### 9. Application-specific PC-FMCW / FMCW ISAC

**Xing et al., 2025 — Sensors**  
"A Phase-Coded FMCW-Based Integrated Sensing and Communication System Design for Maritime Search and Rescue"  
DOI: 10.3390/s25175403

Shows PC-FMCW dual functionality under sea clutter and life-sign sensing requirements.

**Zhang et al., 2025 — ICCC Workshops**  
"Waveform Design for Vital Signs Detection in Integrated Sensing and Communication System"  
DOI: 10.1109/ICCCWorkshops67136.2025.11148186

Studies code/waveform choices for sensing/communication.

**Liu et al., 2026 — IEEE Photonics Technology Letters**  
"Phase-Coded FMCW Laser Headlamp for Integrated Sensing, Communication, and Illumination"  
DOI: 10.1109/LPT.2025.3649597

Optical rather than 77-GHz RF, but confirms that PC-FMCW integration extends beyond conventional automotive RF radar.

---

## 2026 broader high-mobility context

The 2026 vehicular ISAC survey by Ma, Li, and Fan explicitly identifies robustness to imperfect models and hardware impairments, scalable real-time control, and high-mobility operation as practical open issues:

DOI: 10.1186/s13634-026-01332-0.

A 2026 IEEE Wireless Communications article on AFDM-ISAC also emphasizes adaptive ISAC for severe delay/Doppler high-mobility scenarios:

"From OFDM to AFDM: Enabling Adaptive Integrated Sensing and Communication in High-Mobility Scenarios," DOI 10.1109/MWC.2026.3725193.

These works support the relevance of the problem, but they do not establish PC-FMCW-specific priority.

A July 2026 preprint on unified evaluation methodology for AI-native ISAC (Lemic et al., arXiv:2607.14806) is also conceptually relevant because it treats online adaptation under uncertainty and explicitly connects technical KPIs to availability, latency, overhead, and deployment validation stages. It strengthens the case that availability and computational cost should be reported alongside reliability, but it is a general evaluation methodology rather than a PC-FMCW physical-admissibility controller.

---

## Closest-work comparison

| Work/family | PC-/phase-FMCW | Adaptive/reconfigurable | High mobility / vehicular | Explicit uncertainty | Hard physical admissibility before selection | Confidence-qualified joint QoS | Explicit abstention |
|---|---:|---:|---:|---:|---:|---:|---:|
| Uysal/Lampel 2020 | Yes | Limited | Yes | No | No | No | No |
| Kumbul 2021–2024 | Yes | No | Automotive relevant | Mostly impairment evaluation | No | No | No |
| Alami El Dine 2024/2026 | Yes | Synchronization adaptation | Doppler relevant | Impairment-focused | No | No | No |
| Bönsch 2025/2026 | Phase/index FMCW | Limited | Application relevant | Quality evaluation | No | No | No |
| Temiz ICC/TCOM 2026 | FMCW + PM/IM | **Yes** | **Yes** | Doppler/evaluation | No verified equivalent | No verified equivalent | No verified equivalent |
| Cognitive radar waveform selection | Not PC-FMCW | **Yes** | Dynamic targets | State feedback | No PC-FMCW gate | No | No |
| Wang TSP 2024 robust waveform | No | Optimization | Generic | **Yes** | No | Robust frontier, not this rule | No |
| Robust ISAC beamforming | No | Beamforming | Some vehicular relevance | **Yes** | No | Robust constraints | No |
| **This work** | **Yes** | **Yes** | **Yes** | **Yes** | **Yes** | **Yes** | **Yes** |

The final row should not be interpreted as proof of universal priority. It documents the manuscript's intended combination of dimensions.

---

## Claim-safe novelty statement

Recommended manuscript language:

> Prior work separately establishes PC-FMCW sensing and communication, practical synchronization and receiver processing, adaptive FMCW/ISAC parameterization, cognitive waveform selection, and robust ISAC optimization under uncertainty. We study a narrower operational problem: a finite PC-FMCW vehicular PHY in which hard range, IF-sampling, and unambiguous-velocity constraints are enforced before uncertainty-aware joint sensing/communication reliability qualification. The controller may abstain when no admissible action has sufficient finite-sample support, allowing physical infeasibility, statistical unreliability, and service availability to be characterized separately.

Short version:

> **The contribution is not adaptive PC-FMCW by itself; it is admissibility-first, confidence-qualified PC-FMCW adaptation with explicit abstention under high-mobility uncertainty.**

---

## Claims that should not appear

Avoid:

- "We introduce PC-FMCW for joint sensing and communication."
- "We are the first adaptive FMCW/PC-FMCW ISAC system."
- "We are the first robust ISAC design."
- "Doppler/CFO/synchronization handling is novel."
- "B4 is superior to B3."
- "B4 guarantees 100% reliability."
- "The simulation proves automotive deployment reliability."
- "The normalized cost is physical energy."
- "The current Python runtime is real-time."
- "No prior work has ever combined these ideas."

Use instead:

- "In the literature reviewed for this work, we did not identify..."
- "The present study focuses on the comparatively underexplored intersection..."
- "The result is a reliability–availability–computation trade-off."
- "Reliability is conditional on the declared uncertainty model and finite action set."

---

## Reviewer attack test

### Attack 1: "Temiz 2026 already adapts FMCW waveform parameters."

**Response:** Correct; therefore waveform reconfiguration is not claimed as new. The distinction is the ordering and semantics of the control problem: hard PC-FMCW capability constraints first, then uncertainty-aware joint QoS qualification with a finite-sample confidence rule and explicit abstention.

### Attack 2: "Robust waveform design under uncertainty already exists."

**Response:** Correct; Wang et al. 2024 is now cited explicitly. The manuscript does not claim robust optimization itself. It studies a finite discrete PC-FMCW action set and separates deterministic physical infeasibility from statistical reliability.

### Attack 3: "Synchronization/Doppler compensation in PC-FMCW already exists."

**Response:** Correct; Lampel 2020 and Alami El Dine 2024/2026 are now explicit prior art. Residual synchronization error is treated as uncertain state, not as a new synchronization algorithm.

### Attack 4: "The robust policy has worse unconditional QoS than simpler policies."

**Response:** This is a result, not a defect hidden by the paper. B4 is interpreted as a conservative selective controller. The paper reports conditional reliability, selection rate, unconditional QoS, and abstention together.

### Attack 5: "Why should an automotive paper accept no hardware validation?"

**Response:** The manuscript is explicitly simulation-based and does not claim deployment readiness. Hardware PC-FMCW feasibility already exists in the literature; this study focuses on the adaptation/reliability question. A journal reviewer may still request hardware-in-the-loop validation, but the scientific claim is bounded to simulation evidence.

### Attack 6: "The high-mobility profile is synthetic."

**Response:** The manuscript already labels it a composite capability reference, not a commercial preset. This limitation must remain prominent.

---

## What is genuinely strong in the current evidence package

1. **Negative result retained:** B4 is not presented as universally better.
2. **Paired evaluation:** policies see common state/seed units.
3. **Hard-gate ablation:** isolates the role of physical admissibility.
4. **Uncertainty ablation:** separates deterministic from robust selection.
5. **Confidence calibration:** shows why low draw counts can be structurally incapable of certifying the target.
6. **Mismatch experiments:** show both moderate robustness and explicit failure boundaries.
7. **Runtime study:** exposes computational cost rather than hiding it.
8. **Reproducibility:** action set, seeds, protocol, outputs, and manuscript build are frozen.

These features make the work stronger as an operating-region study than as a conventional "new optimizer beats baselines" paper.

---

## Remaining scientific risks before submission

### High priority

- Keep Temiz TCOM 2026 and Wang TSP 2024 visible in Related Work.
- Do not use "first" language without a formal database-level systematic review.
- Verify every bibliography entry against final publisher metadata during venue packaging.
- Keep the distinction between **observed 100% success** and a statistical reliability guarantee.
- Keep all hardware/deployment claims out of the Results and Conclusion.

### Medium priority

- A reviewer may ask why the 54-action space is the right discretization.
- A reviewer may ask whether Wilson qualification is preferable to sequential or exact binomial alternatives.
- A reviewer may ask for hardware-in-the-loop or higher-fidelity channel/oscillator models.
- The host runtime is too slow for a real-time automotive claim and should remain framed as a limitation.

---

## Submission-readiness verdict

### Scientifically

**Yes: the work is now coherent enough to constitute a real paper.**

The research question, gap, method, baselines, negative result, uncertainty analysis, ablations, and claim boundaries are all present.

### As a final submission package

**Not yet fully final.**

The remaining blockers are mostly packaging and venue decisions:

1. choose the target venue;
2. apply venue-specific page/template/reference rules;
3. finalize author/affiliation metadata according to blind-review requirements;
4. complete final LaTeX/PDF compliance checks;
5. perform one final line-by-line bibliography verification;
6. decide whether to submit as a simulation/algorithm paper now or add hardware/HIL evidence for a stronger journal version.

---

## Bottom line

The deep literature pass changes the wording of the novelty claim but **does not eliminate the paper**.

The paper should be sold as:

> **A reliability-aware operating-region study for adaptive vehicular PC-FMCW ISAC, where physically impossible actions are removed before uncertainty-aware joint QoS qualification and the controller can abstain when the declared reliability is unsupported.**

That is narrower than "adaptive PC-FMCW ISAC," but it is also substantially more defensible under expert review.
