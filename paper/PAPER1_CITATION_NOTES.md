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
- Temiz et al., ICC 2026 radar-centric ISAC with dynamic chirp-duration, bandwidth, and phase-coding reconfiguration, DOI 10.1109/ICC59461.2026.11586917.

## Adaptive / cognitive radar prior art checked during the novelty pass

- Jin et al., “Adaptive waveform selection for maneuvering target tracking in cognitive radar,” Digital Signal Processing, 2018, DOI 10.1016/j.dsp.2018.01.012. This establishes adaptive selection from a waveform library, but it is not a PC-FMCW finite-action ISAC physical-admissibility formulation.
- Zhu et al., “Waveform Selection Method of Cognitive Radar Target Tracking Based on Reinforcement Learning,” Radar Science and Technology, 2023, DOI 10.12000/JR22239. This establishes state-dependent cognitive waveform selection, but not the Paper 1 PC-FMCW hard range/velocity admissibility layer and gate-removal ablation.
- Tholeti et al., “Online waveform selection for cognitive radar,” arXiv:2410.10591 (2024). This provides additional adaptive waveform-selection prior art and reinforces that adaptation itself is not claimed as novel.

## Novelty boundary

The literature pass did not identify a verified publication that combines the exact Paper 1 formulation of a finite 54-action PC-FMCW ISAC configuration space, state-dependent deterministic range/velocity admissibility filtering before QoS/resource ranking, and a controlled removal of that filter to quantify recoverable physically invalid selections. This is a scoped literature conclusion, not a claim of universal priority.

Paper 1 therefore does not claim novelty for FMCW capability equations, PC-FMCW, adaptive waveform selection, or physical range/velocity limits individually. Its contribution is the explicit admissibility-first decision architecture and the controlled evidence isolating the selection failure when that layer is omitted.

All DOI strings for the Paper 1 bibliography are retained in `paper1_references.bib` for reproducible bibliographic checking.
