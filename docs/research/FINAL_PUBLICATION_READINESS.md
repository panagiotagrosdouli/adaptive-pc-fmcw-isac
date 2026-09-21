# Final Publication-Readiness Audit

Date: 2026-09-12

## Evidence state

The frozen publication-v2.1 benchmark remains the primary evidence base and is not modified by this audit. The reviewer-grade supplemental evidence is GitHub Actions run `34696063382` at source commit `37958fdca328e4434ca670cf667e33719edced44`. All required supplemental experiment artifacts and the aggregate submission gate completed successfully. The aggregate artifact digest is `sha256:0e9d21d5964e23bd5ed9eae25dfd58c8d8d557968ba7e6d7d2256e7e66055169`.

Evidence class: simulation/analytical evidence only; no new RF or hardware measurements are claimed.

## Submission-gate verdict

The aggregate fail-closed submission gate passed every required evidence family: uncertainty, stress, physics, Pareto, ablations, mismatch, distribution shift, runtime, full metrics, reliability targets, QoS sensitivity, confidence maps, uncertainty-source ablation, reliability calibration, and action-space sensitivity.

## Central statistical result

On the 1,200 paired supplemental full-metric units, B3 selects 20.0% of cases and achieves 80.83% conditional joint QoS. B4 selects 12.5% and achieves 100% observed conditional joint QoS, with a one-sided 95% Wilson lower bound of 98.23%.

B4 does **not** improve unconditional joint QoS. The paired B4-B3 difference is -0.03667 with a 95% paired-bootstrap interval [-0.04833, -0.02583] using 10,000 resamples. This supports unconditional inferiority on this metric, not superiority.

The correct claim is therefore a reliability-availability trade-off: B4 identifies a smaller selectable operating subset with high confidence-qualified conditional reliability.

## Distribution-shift boundary

The unconditional B4-B3 joint-QoS difference remains negative under every tested distribution-shift family: biased state estimate (-0.0100; 95% CI [-0.01729, -0.00313]), correlated SNR/interference (-0.02813; [-0.03438, -0.02208]), heavy-tailed t3 uncertainty (-0.03250; [-0.03833, -0.02687]), and nominal Gaussian uncertainty (-0.02979; [-0.03604, -0.02396]).

These experiments do not justify a universal distributional-robustness claim. They show that the reliability-availability interpretation survives the tested shifts while unconditional superiority remains unsupported.

## Finite-draw calibration

At the declared confidence treatment, 32 robust draws cannot attain the target. Relative to the 4096-draw reference, decision-disagreement rates are 0.583% at 64 draws, 0.333% at 128, 0.0833% at 256, and 0% at 512 in the tested calibration bank. The 256-draw setting is therefore empirically well calibrated in this experiment, but it is not a mathematical guarantee for arbitrary states or distributions.

## Runtime boundary

Latest supplemental runtime measurements for B4 are: median 36.29 ms at 64 draws, 70.47 ms at 128, 138.89 ms at 256, and 272.81 ms at 512. At 256 draws, p95 is 279.71 ms and mean is 168.96 ms. These are unoptimized Python timings on GitHub Actions infrastructure, not embedded-target measurements.

No hard-real-time, embedded-real-time, deployment-latency, or physical-energy claim is supported.

## Pareto boundary

The supplemental evidence contains eight realized B4-selected operating points, six non-dominated and two dominated. This is an empirical Pareto partition over realized selected receiver-level points only. It is not proof of global Pareto optimality over unselected actions or arbitrary operating states.

## Allowed claims

- Physics gating enforces declared modeled FMCW capability constraints before stochastic selection.
- B4 trades availability for high confidence-qualified conditional joint reliability under the declared simulation uncertainty model.
- The tested moderate uncertainty/mismatch studies expose both resilience regions and explicit failure boundaries.
- The contribution is feasible-operating-region and reliability-availability-complexity characterization for adaptive PC-FMCW ISAC.

## Forbidden or unsupported claims

- Universal B4 superiority.
- B4 superiority in unconditional joint QoS.
- Hardware/RF validation by this project.
- Global Pareto optimality.
- Arbitrary-mismatch robustness.
- Real-time embedded readiness.
- Physical-energy interpretation of normalized resource cost.
- Packet-level PER without a declared packet model.
- Confidence-qualified claims derived from raw empirical flags alone.

## Reproducibility record

Primary frozen results must remain frozen and separately identified from supplemental reviewer evidence. Supplemental claims should cite run `34696063382`, source commit `37958fdca328e4434ca670cf667e33719edced44`, the artifact digest above, experiment seed ranges, robust-draw counts, bootstrap resamples, and confidence-bound method. Any future rerun must be reported as a new evidence instance rather than silently replacing these values.

## Publication decision

**READY WITH CLAIM BOUNDARIES.** The computational evidence is internally coherent and the fail-closed gate passes. Submission is scientifically defensible provided the manuscript preserves the conditional-reliability versus availability distinction and explicitly states that the evidence is simulation/analytical rather than hardware validation.
