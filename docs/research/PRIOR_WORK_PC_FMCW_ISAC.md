# Prior Work Map — Adaptive PC-FMCW ISAC

**Repository:** `panagiotagrosdouli/adaptive-pc-fmcw-isac`  
**Literature check date:** 2026-09-30  
**Scope:** PC-FMCW automotive/vehicular sensing and communications, adaptive waveform selection, robust ISAC under uncertainty, and closely related recent PC-FMCW applications.

> This is a targeted prior-art map for manuscript positioning, not a claim of exhaustive coverage of IEEE Xplore, Scopus, Web of Science, or all preprint servers.

## 1. Paper viability

Yes — the repository already contains enough structure and evidence for a defensible simulation-based paper.

The strongest paper is **not** "PC-FMCW for sensing and communication" by itself, because that is established prior art. The most defensible contribution is the intersection of:

1. **PC-FMCW-specific physical admissibility screening** before optimization;
2. a **finite, interpretable PHY action space**;
3. **joint communication + sensing QoS**;
4. **uncertain high-mobility PHY state**;
5. **finite-sample reliability qualification**;
6. explicit **abstention / availability** when the reliability target cannot be supported;
7. reproducible characterization of the **reliability–availability–resource/computation trade-off**.

A suitable contribution statement is:

> We study physics-gated, reliability-constrained adaptation of a finite PC-FMCW vehicular PHY action space under high-mobility uncertainty, and characterize the operating region in which joint communication and sensing QoS can be supported with confidence-qualified reliability.

Avoid a universal-superiority claim for the robust policy. The repository's frozen results instead support a reliability-versus-availability trade-off.

---

## 2. Closest PC-FMCW foundations

### 2.1 Faruk Uysal, 2020 — system design and interference mitigation

**F. Uysal**, "Phase-Coded FMCW Automotive Radar: System Design and Interference Mitigation," *IEEE Transactions on Vehicular Technology*, vol. 69, no. 1, pp. 270–281, 2020.  
DOI: https://doi.org/10.1109/TVT.2019.2953305

**Why it matters:** A foundational automotive PC-FMCW paper. It addresses phase coding, low-sampling processing via group-delay filtering, and interference mitigation.

**Overlap with this repo:** automotive PC-FMCW waveform/receiver physics and interference motivation.

**Difference:** it does not formulate the repo's admissibility-first finite-action robust joint-QoS controller.

### 2.2 Faruk Uysal and Simone Orru, 2020 — application and challenges

**F. Uysal and S. Orru**, "Phase-Coded FMCW Automotive Radar: Application and Challenges," *2020 IEEE International Radar Conference*, pp. 478–482, 2020.  
DOI: https://doi.org/10.1109/RADAR42522.2020.9114798

**Why it matters:** Shows multi-bit coding per chirp and explicitly discusses sensing challenges caused by phase discontinuities.

**Overlap:** waveform implementation limitations and automotive sensing.

**Difference:** not a robust adaptation / joint reliability framework.

---

## 3. Core PC-FMCW sensing-and-communication literature

### 3.1 Experimental PC-FMCW sensing and communications

**U. Kumbul, N. Petrov, F. van der Zwan, C. S. Vaucher, and A. Yarovoy**, "Experimental Investigation of Phase Coded FMCW for Sensing and Communications," *EuCAP 2021*, pp. 1–5.  
DOI: https://doi.org/10.23919/EuCAP51087.2021.9411464

**Importance:** Experimental evidence that PC-FMCW can combine communication capability with FMCW sensing using realizable automotive-radar-style processing.

### 3.2 Receiver structures

**U. Kumbul, N. Petrov, C. S. Vaucher, and A. Yarovoy**, "Receiver Structures for Phase Modulated FMCW Radars," *EuCAP 2022*, pp. 1–5.  
DOI: https://doi.org/10.23919/EuCAP53622.2022.9769268

**Importance:** Receiver architecture and low-sampling processing are directly relevant to the sensing/communication model assumptions.

### 3.3 Smoothed PC-FMCW

**U. Kumbul, N. Petrov, A. Yarovoy, and C. S. Vaucher**, "Smoothed Phase-Coded FMCW: Waveform Properties and Transceiver Architecture," *IEEE Transactions on Aerospace and Electronic Systems*, vol. 59, no. 2, pp. 1720–1737.  
DOI: https://doi.org/10.1109/TAES.2022.3206173

**Importance:** Develops PC-FMCW waveform/transceiver properties and addresses phase-transition behavior.

### 3.4 Code-dependent sensing performance

**U. Kumbul, N. Petrov, C. S. Vaucher, and A. Yarovoy**, "Sensing Performance of Different Codes for Phase-Coded FMCW Radars," *EuRAD 2022*, pp. 393–396.  
DOI: https://doi.org/10.23919/EuRAD54643.2022.9924751

**Importance:** Shows that phase-code choice changes ambiguity/range-sidelobe behavior; useful when motivating interpretable action dimensions.

### 3.5 Coherent MIMO PC-FMCW

**U. Kumbul, N. Petrov, C. S. Vaucher, and A. Yarovoy**, "Phase-Coded FMCW for Coherent MIMO Radar," *IEEE Transactions on Microwave Theory and Techniques*, vol. 71, no. 6, pp. 2721–2733, 2023.  
DOI: https://doi.org/10.1109/TMTT.2022.3228950

**Importance:** Extends PC-FMCW to coherent MIMO while retaining low-sampling FMCW advantages.

### 3.6 Direct joint sensing/communication performance analysis

**U. Kumbul, N. Petrov, C. S. Vaucher, and A. Yarovoy**, "Performance Analysis of Phase-Coded FMCW for Joint Sensing and Communication," *24th International Radar Symposium (IRS)*, 2023.  
DOI: https://doi.org/10.23919/IRS57608.2023.10172426

**Importance:** One of the closest papers to the waveform-level sensing/communications trade-off. It compares receiver approaches and joint sensing/communication performance.

**Key novelty boundary for this repo:** this prior work already establishes that PC-FMCW can be analyzed jointly for sensing and communications. Therefore the new paper must center adaptation, hard physical admissibility, uncertain state, and confidence-qualified reliability.

### 3.7 Automotive interference mitigation

**U. Kumbul, N. Petrov, C. S. Vaucher, and A. Yarovoy**, "Automotive Radar Interference Mitigation using Phase-Coded FMCW Waveform," *IEEE Joint Communications and Sensing (JC&S)*, 2024.  
DOI: https://doi.org/10.1109/JCS61227.2024.10646233

**Importance:** Establishes interference resilience as an important PC-FMCW automotive axis.

**Implication:** The repo should not claim "including interference" as novelty by itself. The novelty must come from how interference uncertainty affects admissible/reliable action selection.

---

## 4. Recent PC-FMCW ISAC application papers

### 4.1 Vital-sign sensing with PC-FMCW ISAC

**C. Zhang, Y. Zhang, D. Xing, and M. Temiz**, "Waveform Design for Vital Signs Detection in Integrated Sensing and Communication System," *2025 IEEE/CIC International Conference on Communications in China Workshops*, 2025.  
DOI: https://doi.org/10.1109/ICCCWorkshops67136.2025.11148186

**What it does:** Compares OFDM, FMCW, and several PC-FMCW code families for vital-sign / micro-Doppler sensing while retaining communication functionality.

**Difference:** application-specific waveform comparison, not high-mobility vehicular reliability-constrained adaptation.

### 4.2 Maritime search-and-rescue PC-FMCW ISAC

**D. Xing, C. Zhang, and Y. Zhang**, "A Phase-Coded FMCW-Based Integrated Sensing and Communication System Design for Maritime Search and Rescue," *Sensors*, vol. 25, no. 17, 5403, 2025.  
DOI: https://doi.org/10.3390/s25175403

**What it does:** MIMO PC-FMCW ISAC under compound sea clutter, multiple code families, multitarget sensing, Monte-Carlo evaluation, and communication comparison with OFDM.

**Why it is important for this repo:** It is a recent simulation-based PC-FMCW ISAC paper and is therefore directly relevant when defending publication value without hardware experiments.

**Difference:** maritime clutter/code/MIMO performance rather than finite-action vehicular PHY adaptation with physics gating and uncertainty-aware reliability.

### 4.3 Phase-coded FMCW laser headlamp / ISCAI

**S. Liu, T. Sun, X. Shu, J. Song, and Y. Dong**, "Phase-Coded FMCW Laser Headlamp for Integrated Sensing, Communication, and Illumination," *IEEE Photonics Technology Letters*, vol. 38, no. 14, pp. 1032–1035, 2026.  
DOI: https://doi.org/10.1109/LPT.2025.3649597

**What it does:** Optical PC-FMCW for sensing, communication, and adaptive illumination, including track-before-detect processing.

**Difference:** optical/illumination architecture. The present repo is RF/mmWave 77-GHz PHY adaptation and should explicitly keep that separation.

### 4.4 Optical PC-FMCW interference-resistant ISAC

**T. Zhang et al.**, "Phase-coded FMCW for mutual-interference-free optical integrated sensing and communication," *Chinese Physics B*, 2026.  
DOI: https://doi.org/10.1088/1674-1056/ae5170

**Importance:** Further evidence that PC-FMCW ISAC is active beyond RF automotive radar.

**Difference:** optical O-ISAC and mutual-interference suppression, not vehicular RF reliability control.

---

## 5. Adaptive / cognitive waveform-selection prior art

### 5.1 Adaptive waveform-library selection

**B. Jin et al.**, "Adaptive waveform selection for maneuvering target tracking in cognitive radar," *Digital Signal Processing*, vol. 75, pp. 210–221, 2018.  
DOI: https://doi.org/10.1016/j.dsp.2018.01.012

**What it establishes:** Selecting from a waveform library as a function of target/environment state is established cognitive-radar methodology.

**Consequence:** The paper should not claim waveform adaptation itself as novel.

### 5.2 Online learning for waveform selection

**T. Tholeti, A. Rangarajan, and S. Kalyani**, "Online waveform selection for cognitive radar," arXiv:2410.10591, 2024.  
URL: https://arxiv.org/abs/2410.10591

**What it establishes:** Online/RL-based adaptive waveform parameter selection.

**Difference:** target tracking / radar-only objective rather than PC-FMCW joint communication+sensing QoS with hard admissibility.

---

## 6. Robust communications / robust ISAC prior art

### 6.1 Robust V2X resource allocation with imperfect CSI

**W. Wu, R. Liu, Q. Yang, and T. Q. S. Quek**, "Robust Resource Allocation for Vehicular Communications With Imperfect CSI," *IEEE Transactions on Wireless Communications*, vol. 20, no. 9, pp. 5883–5897, 2021.  
DOI: https://doi.org/10.1109/TWC.2021.3070894

**Importance:** Robust/chance-constrained vehicular resource allocation under uncertainty is established.

**Difference:** communication resource allocation rather than PC-FMCW waveform admissibility and joint sensing/communication reliability.

### 6.2 Robust ISAC under two uncertainty sources

**W. Lyu et al.**, "Dual-Robust Integrated Sensing and Communication: Beamforming Under CSI Imperfection and Location Uncertainty," *IEEE Wireless Communications Letters*, vol. 13, no. 11, pp. 3124–3128, 2024.  
DOI: https://doi.org/10.1109/LWC.2024.3454728

**Importance:** Robust ISAC under imperfect CSI and sensing-location uncertainty already exists.

**Difference:** continuous beamforming / worst-case optimization rather than discrete PC-FMCW PHY action selection with deterministic range/velocity admissibility and confidence-qualified abstention.

---

## 7. Radar-centric ISAC modulation work relevant to adaptation

### 7.1 ICC 2026 radar-centric ISAC

**M. Temiz, C. Horne, M. A. Ritchie, and C. Masouros**, "Improved Data Rates for Radar-centric ISAC with Index and Phase Modulations," *IEEE ICC 2026*, pp. 1–6, 2026.  
DOI: https://doi.org/10.1109/ICC59461.2026.11586917

**Importance:** Recent radar-centric ISAC with phase/index modulation and a flexible design perspective.

**Bibliography note:** The repository's `paper/PAPER1_CITATION_NOTES.md` currently describes this DOI as a paper on "dynamic chirp-duration, bandwidth, and phase-coding reconfiguration." The DOI resolves to the title above. That citation note should be corrected before submission.

---

## 8. Vehicular ISAC context

### 8.1 2026 vehicular ISAC survey

**Z. Ma, Z. Li, and A. Fan**, "Integrated sensing and communications for vehicular networks: a survey," *Journal on Advances in Signal Processing*, 2026, Article 54.  
DOI: https://doi.org/10.1186/s13634-026-01332-0

**Why it matters:** Identifies high mobility, robustness to imperfect modeling/hardware non-idealities, scalable control, and prototype/field validation as important deployment challenges.

**Use in the manuscript:** Context and motivation, not proof of novelty.

---

## 9. Closest-work comparison

| Prior work | PC-FMCW | Automotive / vehicular | Joint sensing + comm | Adaptive selection | Explicit uncertainty robustness | Hard physical admissibility gate | Reliability/abstention trade-off |
|---|---:|---:|---:|---:|---:|---:|---:|
| Uysal, TVT 2020 | yes | yes | enabling motivation | no | no | waveform constraints, not controller gate | no |
| Kumbul et al., EuCAP 2021 | yes | automotive-oriented | yes | no | no | no | no |
| Kumbul et al., IRS 2023 | yes | automotive-oriented | yes | no | limited performance analysis | no | no |
| Kumbul et al., JC&S 2024 | yes | yes | adjacent | no | interference-focused | no | no |
| Xing et al., Sensors 2025 | yes | no, maritime | yes | code comparison | clutter simulation | no | no |
| Liu et al., PTL 2026 | yes | intelligent vehicles, optical | yes + illumination | system-level functions | limited | no | no |
| Jin et al., DSP 2018 | no | no | radar only | yes | state-aware | no | no |
| Lyu et al., WCL 2024 | no / generic ISAC | generic | yes | optimization | yes | no PC-FMCW gate | no |
| **This repo** | **yes** | **yes, 77 GHz RF/mmWave** | **yes** | **yes, finite PHY action set** | **yes** | **yes: range/velocity/sampling first** | **yes** |

The strongest differentiator is the **ordered decision architecture**:

```text
estimated operating state
        |
        v
PC-FMCW physical admissibility gate
(range / IF sampling / unambiguous velocity)
        |
        v
finite set of physically valid actions
        |
        v
uncertainty-aware joint QoS qualification
        |
        v
confidence-qualified selection OR abstention
```

---

## 10. Defensible novelty statement

A conservative novelty statement is:

> Prior work separately establishes PC-FMCW sensing/communication, adaptive waveform selection, robust vehicular resource allocation, and robust ISAC optimization. The comparatively underexplored intersection addressed here is an admissibility-first PC-FMCW control architecture in which deterministic waveform limits are enforced before a finite-action, uncertainty-aware joint sensing/communication reliability decision, with explicit abstention and operating-region characterization.

Do **not** claim that no prior paper has ever combined these ideas unless a formal systematic search across IEEE Xplore, Scopus/Web of Science, Google Scholar, arXiv, and relevant conference proceedings is completed and documented.

---

## 11. Claims to avoid

- "We introduce PC-FMCW for joint sensing and communication."
- "We are the first to adapt radar waveforms."
- "We are the first robust ISAC design."
- "We are the first to consider interference/Doppler/CFO in PC-FMCW."
- "B4 is universally better than deterministic adaptation."
- "The simulation proves field reliability."
- "The normalized cost is physical energy."
- "Host Python runtime proves embedded real-time feasibility."

---

## 12. Recommended additions to the main manuscript bibliography

The current bibliography already covers much of the Kumbul PC-FMCW chain and robust-ISAC context. At minimum, consider adding the following directly to the manuscript's main related-work discussion:

1. Uysal, *IEEE TVT*, 2020 — foundational automotive PC-FMCW system design/interference mitigation.
2. Uysal & Orru, *IEEE Radar Conference*, 2020 — PC-FMCW automotive applications/challenges.
3. Zhang et al., ICCC Workshops 2025 — PC-FMCW waveform comparison for vital-sign ISAC.
4. Xing et al., *Sensors*, 2025 — recent PC-FMCW ISAC simulation study under maritime clutter.
5. Jin et al., *Digital Signal Processing*, 2018 — adaptive waveform-library selection.
6. Tholeti et al., arXiv 2024 — online waveform selection.
7. Temiz et al., ICC 2026 — radar-centric ISAC with index/phase modulation, with the title corrected in internal notes.

These references strengthen the manuscript because they make the novelty claim **narrower and more credible**, not weaker.

---

## 13. Bottom line

The repository can support a paper, and in fact already contains a manuscript-grade evidence chain. The publication argument is strongest when framed as a **reliability–availability–resource operating-region paper for adaptive PC-FMCW ISAC**, rather than as a generic new PC-FMCW waveform paper.

The reviewer-facing message should be:

> Existing literature shows that PC-FMCW works, that phase coding affects sensing/communication performance, that adaptive waveform selection is possible, and that robust ISAC optimization is established. This work asks a narrower operational question: under high-mobility uncertainty, which PC-FMCW configurations are physically admissible at all, and among those, which can be selected with confidence-qualified joint sensing/communication reliability — including the decision to abstain when no action is sufficiently supported?
