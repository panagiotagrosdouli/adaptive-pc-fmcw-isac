# Paper 1 Citation Notes

The standalone Paper 1 bibliography contains only sources used by the manuscript. The current literature pass explicitly distinguishes three layers of prior art: (i) PC-FMCW waveform/receiver/sensing studies, (ii) adaptive/cognitive radar waveform selection, and (iii) recent adaptive radar-centric FMCW/ISAC reconfiguration.

## Verified PC-FMCW / ISAC sources

- Kumbul et al., EuCAP 2021, DOI 10.23919/EuCAP51087.2021.9411464.
- Kumbul et al., EuCAP 2022 receiver structures, DOI 10.23919/EuCAP53622.2022.9769268.
- Kumbul et al., IEEE TAES 2023 smoothed PC-FMCW, DOI 10.1109/TAES.2022.3206173.
- Kumbul et al., EuRAD 2022 sensing performance of codes, DOI 10.23919/EuRAD54643.2022.9924751.
- Kumbul et al., IEEE TMTT 2023 coherent MIMO PC-FMCW, DOI 10.1109/TMTT.2022.3228950.
- Kumbul et al., IRS 2023 performance analysis for joint sensing/communication, DOI 10.23919/IRS57608.2023.10172426.
- Kumbul et al., IEEE JC&S 2024 automotive PC-FMCW interference mitigation, DOI 10.1109/JCS61227.2024.10646233.
- Uysal, IEEE TVT 2020, “Phase-Coded FMCW Automotive Radar: System Design and Interference Mitigation,” DOI 10.1109/TVT.2019.2953305.
- Uysal and Orru, IEEE Radar Conference 2020, “Phase-Coded FMCW Automotive Radar: Application and Challenges,” DOI 10.1109/RADAR42522.2020.9114798.
- Zhang et al., ICCC Workshops 2025, “Waveform Design for Vital Signs Detection in Integrated Sensing and Communication System,” DOI 10.1109/ICCCWorkshops67136.2025.11148186.
- Xing et al., Sensors 2025, “A Phase-Coded FMCW-Based Integrated Sensing and Communication System Design for Maritime Search and Rescue,” DOI 10.3390/s25175403.
- Temiz et al., ICC 2026, “Improved Data Rates for Radar-centric ISAC with Index and Phase Modulations,” DOI 10.1109/ICC59461.2026.11586917. The paper also describes dynamic reconfiguration of chirp duration, bandwidth, and phase coding; the title above is the verified bibliographic title.

- Lampel et al., EuCAP 2020, “System Level Synchronization of Phase-Coded FMCW Automotive Radars for RadCom,” DOI 10.23919/EuCAP48036.2020.9135417.
- Alami El Dine et al., ICMIM 2024, “A Joint Radar and Communication Approach Based on Phase-Coded FMCW Chirp Sequences,” IEEE Xplore document 10654233.
- Bönsch et al., IEEE JC&S 2025, “Evaluating Communication and Sensing Quality in Phase-Modulated FMCW Radar,” DOI 10.1109/JCS64661.2025.10880648.
- Wang et al., IEEE TSP 2024, “Robust Waveform Design for Integrated Sensing and Communication,” DOI 10.1109/TSP.2024.3410142.
- Alami El Dine et al., GeMiC 2026, “Synchronization Method for High-Data-Rate Communication Using Phase-Coded FMCW in Incoherent Joint Sensing and Communication Systems,” DOI 10.1109/GeMiC71240.2026.11516397.
- Bönsch et al., MIKON 2026, “Enabling Integrated Sensing and Communication with Index-Modulated FMCW Radar,” DOI 10.23919/MIKON66970.2026.11577911.
- Temiz et al., IEEE TCOM 2026, “FMCW-Based Integrated Sensing and Communication System: Design, Implementation, and Experimental Measurements,” DOI 10.1109/TCOMM.2026.3706482.

## Adaptive / cognitive radar prior art checked during the novelty pass

- Jin et al., “Adaptive waveform selection for maneuvering target tracking in cognitive radar,” Digital Signal Processing, 2018, DOI 10.1016/j.dsp.2018.01.012. This establishes adaptive selection from a waveform library, but it is not a PC-FMCW finite-action ISAC physical-admissibility formulation.
- Zhu et al., “Waveform Selection Method of Cognitive Radar Target Tracking Based on Reinforcement Learning,” Radar Science and Technology, 2023, DOI 10.12000/JR22239. This establishes state-dependent cognitive waveform selection, but not the Paper 1 PC-FMCW hard range/velocity admissibility layer and gate-removal ablation.
- Tholeti et al., “Online waveform selection for cognitive radar,” arXiv:2410.10591 (2024). This provides additional adaptive waveform-selection prior art and reinforces that adaptation itself is not claimed as novel.

## Novelty boundary

The expanded literature pass through 2026-09-30 did not identify a verified publication that combines the Paper 1 architecture of state-dependent deterministic PC-FMCW range/IF/velocity admissibility filtering before finite-action joint sensing/communication reliability qualification, a confidence-qualified reject option, and operating-region analysis that separates physical infeasibility from statistical abstention and selected-action failure. Recent FMCW work already includes dynamic waveform reconfiguration, synchronization, hardware validation, and robust waveform design, so this conclusion is deliberately scoped and is not a claim of universal priority.

Paper 1 therefore does not claim novelty for FMCW capability equations, PC-FMCW, adaptive waveform selection, or physical range/velocity limits individually. Its contribution is the explicit admissibility-first decision architecture and the controlled evidence isolating the selection failure when that layer is omitted.

All DOI strings for the Paper 1 bibliography are retained in `paper1_references.bib` for reproducible bibliographic checking.
