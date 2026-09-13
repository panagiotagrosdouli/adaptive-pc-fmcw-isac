# Evidence Map

Frozen baseline: `3904c4c2a69c4af96751d64614f7228ddea24b56`.

## Primary frozen benchmark

- Source: `configs/paper_protocol_v2_1.json`, `artifacts/publication/v2_1/FINAL_RESULTS.json`, publication workflow outputs.
- Status: frozen primary publication evidence.
- Scale: 12 scenarios/seed, 1000 final seeds, 12000 state/seed units per policy, six policies, 72000 receiver-level records.
- Statistical procedure: paired policy evaluation; 95% paired bootstrap with 10000 resamples; one-sided 95% Wilson lower bounds for reliability statements.
- Provenance: controlled simulation input + simulation output + statistical derivation.
- Claim boundary: simulation/analytical evidence, not RF hardware measurement.

## Main frozen policy results

- B0_FIXED: selection 0.9235833; unconditional joint QoS 0.5904167; conditional joint QoS 0.6392673.
- B1_COMM_ONLY: selection 0.7531667; unconditional 0.5259167; conditional 0.6982740.
- B2_SENSING_ONLY: selection 0.3225833; unconditional 0.16175; conditional 0.5014208.
- B3_DETERMINISTIC_JOINT: selection 0.1906667; unconditional 0.16175; conditional 0.8483392.
- B4_ROBUST_JOINT: selection 0.1223333; unconditional 0.1223333; conditional 1.0; 1468/1468 selected successes; one-sided 95% Wilson lower bound 0.9981604.
- ORACLE: selection 0.6666667; unconditional 0.6666667; conditional 1.0. Oracle is a non-deployable hindsight reference.

## Paired B4-B3 result

- Metric: unconditional joint-QoS indicator difference.
- n: 12000 paired units.
- Mean B4-B3: -0.0394167.
- 95% paired-bootstrap interval: [-0.0429167, -0.0360000].
- Bootstrap resamples: 10000.
- Supported wording: B4 identifies a smaller operating subset with stronger conditional reliability.
- Unsupported wording: B4 is universally or unconditionally superior to B3.

## Frozen QoS/statistical protocol

- BER <= 1e-3.
- Effective rate >= 100000 bit/s.
- Range RMSE <= 1 m.
- Velocity RMSE <= 1 m/s.
- Joint reliability target 0.95.
- B4 internal draws 512.
- Reliability confidence 0.95.
- Acceptance rule: one-sided Wilson lower bound >= target.
- No post-hoc threshold tuning.

## Supplemental evidence families

The supplemental publication suite contains uncertainty scaling, uncertainty-source ablation, reliability calibration, reliability-target sensitivity, QoS sensitivity, distribution shift, model mismatch, physics-gate/joint-constraint ablation, action-space sensitivity, runtime scaling, empirical Pareto analysis and confidence maps. These are reviewer-grade supplemental simulation experiments and do not replace the frozen primary benchmark.

## Important claim boundaries

- High-draw Monte Carlo reference is not physical ground truth.
- Host runtime is not embedded ECU certification.
- The composite high-mobility profile is a capability reference, not a commercial preset.
- PER is not independently estimated without a declared packet model.
- Empirical Pareto structure does not prove global Pareto optimality.
- Robustness claims are limited to evaluated uncertainty/mismatch families.
