# Supplemental Publication v2.1 — Reviewer-Grade Results

Evidence class: `SUPPLEMENTAL_PUBLICATION_V2_1_SIMULATION_NOT_HARDWARE_MEASUREMENT`.

This package summarizes the successful supplemental reviewer-evidence workflow run `33975266575` at source commit `ef0e135b88c7c9647d72195f80884e380bc33cf6`. It does not replace or modify the frozen publication-v2.1 benchmark, thresholds, policy logic, or primary 1000-seed evidence.

## Main interpretation

The supplemental experiments reinforce an availability–reliability interpretation of the robust policy rather than an unconditional-superiority claim. As uncertainty increases, B3 continues selecting a broader set of operating states but its conditional joint-QoS probability degrades markedly. B4 contracts its operating region and preserves substantially higher conditional joint reliability until the uncertainty becomes severe.

At uncertainty scale 0, B3 and B4 are identical in this sweep: both select 16.67% of states and achieve 100% conditional joint QoS. At scale 1, B3 selects 18.50% with 87.39% conditional joint QoS, whereas B4 selects 12.50% with 100% conditional joint QoS. At scale 2, B3 selects 20.33% with 68.03% conditional joint QoS, while B4 selects 9.75% and retains 100% conditional joint QoS. At scale 3, B3 reaches only 62.04% conditional joint QoS; B4 selects 5.92% of states and achieves 98.59% conditional joint QoS. The corresponding B4 Wilson lower 95% bound at scale 3 is 93.93%, so this most severe point does not confidence-qualify the declared 95% target.

## Ablation evidence

The four-way ablation distinguishes the contributions of the physics gate, state-uncertainty model, and joint constraint. FULL_B4 selects 12.50% of states with 100% observed conditional joint QoS and a Wilson lower 95% bound of 98.23%. Removing state uncertainty increases selection to 20.00% but reduces conditional joint QoS to 80.83%. Removing the joint constraint expands selection to 67.25% but reduces conditional joint QoS to 85.50%. Removing the physics gate selects 31.67% of the ablation bank but achieves 0% joint QoS in this frozen supplemental design. This result should be interpreted as evidence that physically impossible candidate actions must not be admitted by the controller, not as a claim that every ungated controller necessarily fails in every scenario.

## Model mismatch

B4 is more resilient than B3 under several moderate mismatch families. Under CFO under-modeling from 500 Hz assumed to 1–5 kHz actual, B3 achieves 87–88% joint QoS while B4 achieves 100% in the evaluated 100-seed banks. Under Doppler mismatch from 20 m/s assumed to 25–40 m/s actual, B3 achieves 86% while B4 achieves 100%. Under interference under-modeling from -10 dB assumed to 0 dB actual, B3 drops to 18% while B4 achieves 86%.

The robustness is not unlimited. For actual INR of 10 or 20 dB, both policies fail in the tested mismatch bank. For assumed SNR of 12 dB with actual SNR 8 dB, B4 achieves only 17%; at 6 dB both policies fail. These negative results define useful failure boundaries and must be retained.

## Physics gate

The physics-only range–velocity map uses the source-grounded profile limits already defined in the repository. The short-range parking profile supports approximately 22.36 m positive-IF range and 8.41 m/s unambiguous radial velocity. The high-mobility capability profile supports approximately 56.21 m and 48.67 m/s. The map therefore separates three regions: no feasible profile, high-mobility-only feasibility, and overlap where both profiles are physically admissible.

## Physical-resource Pareto reporting

The supplemental Pareto output reports physical decision variables directly: transmit-power fraction, repetition factor, chips per chirp, profile ADC samples per frame, effective rate, and sensing RMSE. The synthetic normalized resource cost used elsewhere is intentionally not called physical energy. The selected B4 actions in this bank all achieved observed joint QoS 1.0, but the point counts differ substantially, so the rare one-sample configurations should not be overinterpreted as statistically established Pareto optima.

## Runtime and decision complexity

The current unoptimized Python implementation shows approximately linear B4 scaling with the number of robust uncertainty draws. Median B4 latency is 30.71 ms at 64 draws, 61.03 ms at 128, 121.36 ms at 256, and 240.44 ms at 512. By comparison, B3 median latency remains about 0.44 ms. Therefore this evidence does not support a claim that the 512-draw B4 implementation is real-time for high-mobility vehicular deployment. The result should be presented as an implementation limitation and motivation for vectorization, candidate pruning, parallel uncertainty evaluation, or lower-draw approximations.

## Claim boundary

The supplemental evidence supports the statement that robust physics-gated adaptation can exchange operating-region availability for substantially higher conditional joint reliability under uncertainty and several forms of model mismatch. It does not support a claim that B4 maximizes unconditional joint QoS, works under arbitrary mismatch, or is already real-time at 512 robust draws. All outputs are simulation/analytical evidence and are not hardware measurements.
