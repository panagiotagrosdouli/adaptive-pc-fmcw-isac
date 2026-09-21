# Publication Experiment Matrix

The paper is evaluated as a controlled, reproducible PC-FMCW ISAC study. No dataset, trajectory predictor, beam manager, ADB controller, path planner, or packet scheduler is part of the contribution.

## E0 — Provenance and capability sanity

Before any algorithm comparison, freeze the literature-grounded profile table and derived physical limits. Use at least two regimes:

- **P-SR:** short-range TI automated-parking-style 77-GHz profile (858 MHz, 25.6 us active chirp, 115.8 us PRI, 10 MSPS IF ADC, 64 chirps);
- **P-HM:** high-mobility 77-GHz capability profile (1 GHz / 20 us sweep target, 37.5 MSPS ADC capability, short PRI).

Cross-check the 20.28 m / 5.1 kHz one-way Doppler / 15 dBsm published 77-GHz JCRS example as an external scale reference. Do not claim waveform parity because that source uses PMCW-CDMA.

## E1 — Waveform and IF sanity

Validate phase-code generation, dechirped-IF sampling, power/noise normalization, timing and dimensions. Explicitly reject the physically invalid shortcut of sampling an 858-MHz transmit sweep at a 10-MSPS radar ADC. Verify analytical range/velocity limits against code-derived values.

## E2 — Communication validation

Use multi-chip DBPSK after chirp removal at the remote receiver. Compare Monte-Carlo BER versus Eb/N0 with the analytical DBPSK reference where assumptions coincide. Sweep 16/32/64 phase-code chips per chirp and report raw/effective rate separately.

## E3 — Sensing validation

Single-target range/Doppler recovery, resolution checks and error versus IF SNR. Use known injected delay/Doppler; report FFT-grid bias separately from noise variance. Run both P-SR and P-HM.

## E4 — Mobility and residual synchronization stress

Sweep physical radial velocity and residual post-synchronization frequency error. Keep one-way communication Doppler and two-way monostatic sensing Doppler distinct. Include the published 5.1-kHz one-way Doppler scale as a cross-check. Quantify BER, sensing bias and infeasible operating regions.

## E5 — Phase-noise/synchronization stress

Sweep phase-noise innovation and timing error only after declaring the mapping from hardware phase-noise specifications to the stochastic model. Until that mapping is validated, label phase-noise variance as a controlled sensitivity parameter, not a measured hardware value.

## E6 — Mutual interference

Sweep INR and number/type of interfering PC-FMCW emitters. Report degradation rather than claiming a novel interference canceller. Include coherent/non-coherent interference cases where the model supports them.

## E7 — Fixed and nominal adaptation baselines

B0 fixed PHY; B1 communication-only adaptation; B2 sensing-only adaptation; B3 deterministic joint adaptation. Freeze the finite action codebook before the final run.

## E8 — Proposed robust adaptation

B4 chance-constrained joint sensing/communication adaptation under uncertain SNR/Doppler/residual synchronization/interference state. Reliability is evaluated empirically on held-out Monte-Carlo draws, not only on the policy's internal predictor.

## E9 — Reliability region

Map feasible/infeasible operating regions under communication BER/rate and sensing RMSE constraints. Produce profile-specific maps for P-SR and P-HM and a profile-selection map where both are allowed.

## E10 — Pareto analysis

Communication reliability versus sensing accuracy versus resource cost. Show the full Pareto set and do not compress all tradeoffs into one scalar score only.

## E11 — Ablations and mismatch

Remove uncertainty modelling; remove individual impairments; perturb state-estimation error distributions; perturb RCS/link-budget assumptions; test profile mismatch and unmodelled residual frequency error.

## E12 — Statistics, complexity and reproducibility

Use fixed seed families, paired policy comparisons, bootstrap 95% confidence intervals, violation probability, action-selection complexity and measured runtime. Archive machine-readable configuration, source commit, environment and results.

## Freeze rules

All action codebooks, thresholds, grids, source-derived constants and seeds are frozen before the final run. Pilot Stage-7 results are diagnostic only. Negative outcomes are retained. Paper claims must distinguish analytical reference, literature-grounded constants, waveform/IF simulation, controlled simulation variables and any external measured values.
