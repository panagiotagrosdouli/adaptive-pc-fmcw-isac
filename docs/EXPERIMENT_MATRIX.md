# Publication Experiment Matrix

The paper is evaluated as a controlled, reproducible PC-FMCW ISAC study. No dataset, trajectory predictor, beam manager, ADB controller, path planner, or packet scheduler is part of the contribution.

## E1 — Waveform sanity
Noiseless PC-FMCW generation, phase-code recovery, power normalization, sampling and dimensional checks.

## E2 — Communication validation
DBPSK BER versus SNR under AWGN; compare waveform Monte Carlo with the analytical DBPSK reference where model assumptions coincide.

## E3 — Sensing validation
Single-target range/Doppler recovery, resolution checks and error versus SNR. Use known injected delay/Doppler; report FFT/grid bias separately from noise variance.

## E4 — Doppler/CFO stress
Sweep vehicle radial velocity and residual CFO. Quantify communication BER and sensing bias.

## E5 — Phase-noise/synchronization stress
Sweep phase-noise innovation and timing offset. Identify failure boundaries.

## E6 — Mutual interference
Sweep INR and number/type of interfering PC-FMCW emitters. Report degradation rather than claiming a novel interference canceller.

## E7 — Fixed and nominal adaptation baselines
B0 fixed PHY; B1 communication-only adaptation; B2 sensing-only adaptation; B3 deterministic joint adaptation.

## E8 — Proposed robust adaptation
B4 chance-constrained joint sensing/communication adaptation under uncertain SNR/Doppler/CFO/interference state.

## E9 — Reliability region
Map feasible/infeasible operating regions under communication BER/rate and sensing RMSE constraints.

## E10 — Pareto analysis
Communication reliability versus sensing accuracy versus resource cost. Do not compress all tradeoffs into one scalar score only.

## E11 — Ablations and mismatch
Remove uncertainty modelling; remove individual impairments; perturb channel-estimation error distribution; test model mismatch.

## E12 — Statistics and complexity
Fixed seed set, paired policy comparisons, bootstrap 95% confidence intervals, violation probability, action-selection complexity and measured runtime.

## Freeze rules
All action codebooks, thresholds, grids and seeds are frozen before the final run. Negative outcomes are retained. Paper claims must distinguish analytical reference, waveform simulation and system-level abstractions.
