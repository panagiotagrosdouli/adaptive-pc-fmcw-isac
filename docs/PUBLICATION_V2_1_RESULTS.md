# Frozen Publication V2.1 Results

This document records the immutable simulation evidence from GitHub Actions run `33967030983` at commit `1b2100c11b6d4a7b6213777fd2da85e22601154b`.

Evidence class: **simulation candidate, not hardware measurement**.

## Main benchmark

The frozen benchmark evaluates six policies over 12,000 states per policy (72,000 receiver-level evaluations total).

| Policy | Selection | Abstention | Joint QoS, unconditional | Joint QoS, conditional on selection | Mean normalized resource cost when selected |
|---|---:|---:|---:|---:|---:|
| B0 Fixed | 0.9236 | 0.0764 | 0.5904 | 0.6393 | 2.3200 |
| B1 Communication-only | 0.7532 | 0.2468 | 0.5259 | 0.6983 | 1.3245 |
| B2 Sensing-only | 0.3226 | 0.6774 | 0.1618 | 0.5014 | 1.0566 |
| B3 Deterministic joint | 0.1907 | 0.8093 | 0.1618 | 0.8483 | 1.1906 |
| B4 Robust joint | 0.1223 | 0.8777 | 0.1223 | 1.0000 | 1.2079 |
| Hindsight Oracle | 0.6667 | 0.3333 | 0.6667 | 1.0000 | 1.2870 |

The B4 robust policy succeeds in all 1,468 selected cases. Its one-sided 95% Wilson lower bound for conditional joint reliability is `0.9981603772`. This high conditional reliability is obtained with a selection rate of only `0.1223333333`, so the result is best interpreted as a reliability-availability trade-off rather than universal performance superiority.

## Paired statistics

For unconditional joint QoS, the paired B4-minus-B3 difference is `-0.0394167` with a 95% paired-bootstrap interval `[-0.0429167, -0.0360000]` over 12,000 paired observations and 10,000 bootstrap resamples. The frozen evidence therefore does **not** support the claim that B4 improves unconditional joint QoS over B3.

The paired B4-minus-B0 difference is `-0.4680833` with a 95% interval `[-0.4770021, -0.4591667]`.

The structural sanity gate passes: the hindsight Oracle is not below the best deployable policy, B1 and B3 are distinguishable, and the pipeline marks the structural paper-readiness gate as true. The B4-superiority flag is false and must remain reported as a negative result.

## E9 feasible operating-region slices

The frozen E9 implementation uses the raw empirical mean to set `empirically_meets_declared_target`; it does not use the Wilson lower confidence bound. Therefore these cells characterize the sampled operating region but must not be described as confidence-qualified 95% reliability guarantees.

- CFO × INR: `0/15` cells are flagged as meeting the declared target.
- Eb/N0 × radial velocity: `2/42` cells are flagged; they are `(12 dB, 0 m/s)` and `(16 dB, 0 m/s)`.
- IF-SNR × range: `24/42` cells are flagged. All six tested ranges from 5 to 50 m are flagged at IF-SNR values 5, 10, 15 and 20 dB; none are flagged at -10, -5 or 0 dB.

A post-processing confidence-qualified E9 analysis may be added later from stored successes/trials, but it must not modify the underlying frozen simulations.

## E11 ablations

Each ablation contains 240 paired state evaluations.

| Variant | Selection | Unconditional joint QoS | Conditional joint QoS |
|---|---:|---:|---:|
| Full B4 | 0.1250 | 0.1250 | 1.0000 |
| No state uncertainty | 0.1667 | 0.1667 | 1.0000 |
| No CFO | 0.1250 | 0.1250 | 1.0000 |
| No interference | 0.1250 | 0.1250 | 1.0000 |

Within this frozen E11 state set, removing state uncertainty expands the selected/feasible region by about 4.17 percentage points. Removing CFO or interference does not alter the aggregate E11 selection rate. This does not mean CFO or interference are physically irrelevant: the separate communication impairment validation shows sensitivity to residual CFO and interference. The ablation result only says they do not move the aggregate robust-decision boundary in this particular E11 slice.

## Pareto point

The frozen B4 Pareto output contains one reported point: 16 chips/chirp, repetition factor 1, transmit-power fraction `0.2511886432`, 96,000 ADC samples/frame, empirical conditional joint QoS `1.0` over 828 observations, and mean declared normalized resource cost `0.9410460060`.

The normalized resource cost is an experiment-defined dimensionless design metric. It must not be described as physical energy in joules.

## Claim boundary

The publication claim supported by the frozen evidence is:

> Robust PC-FMCW adaptation identifies a conservative operating region in which selected transmissions achieve very high conditional joint sensing-communication reliability under the declared uncertainty model, at the cost of substantially reduced availability. State uncertainty contracts this operating region.

The frozen evidence does **not** support a claim that B4 universally outperforms fixed or deterministic policies in unconditional joint QoS.

## Provenance

- GitHub Actions run: `33967030983`
- Frozen commit: `1b2100c11b6d4a7b6213777fd2da85e22601154b`
- Main final artifact SHA-256: `31daf1b571c84e4c38380cc8e7d03715eb06d03d7d9ff3e151c49184b5ebdd79`
- E9/E11 artifact SHA-256: `1aeabd05526bfda796cdebb0df45214c2a7c0f665044faa01dfbd7d8244bb722`
- Machine-readable summaries: `artifacts/publication/v2_1/FINAL_RESULTS.json` and `artifacts/publication/v2_1/E9_E11_RESULTS.json`

The full raw result bundles remain preserved as immutable GitHub Actions artifacts for the run above.
