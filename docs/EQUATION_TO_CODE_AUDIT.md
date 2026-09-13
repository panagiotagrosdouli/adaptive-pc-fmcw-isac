# Equation-to-Code Audit

Frozen baseline: `3904c4c2a69c4af96751d64614f7228ddea24b56`.

## Confidence qualification

Source: `src/pcfmcw_isac/statistics.py`.

The implementation computes a one-sided Wilson lower confidence bound for a Bernoulli probability. It uses `NormalDist().inv_cdf(confidence)`, so confidence 0.95 corresponds to the one-sided normal quantile (approximately 1.64485), not the two-sided 1.96 quantile.

`reliability_target_satisfied` returns true only when the Wilson lower bound reaches the declared target.

## B4 ordering

Source: `src/pcfmcw_isac/policy_v2_1.py`.

`select_action_v2_1` enumerates the frozen action set, constructs the estimated state, applies `filter_physics_feasible_actions`, evaluates finite uncertainty draws for B4, computes the Wilson lower bound, rejects candidates below the reliability target, and selects the cheapest accepted action. If no candidate remains, it returns no action.

## Publication model warning

`src/pcfmcw_isac/physics.py` contains an older auditable surrogate model whose own docstring states that it is a protocol-development model rather than the publication-grade waveform receiver. Manuscript equations and claims must therefore be traced to the publication-v2.1 path (`policy_v2_1.py`, `policy_evaluation.py`, `publication_protocol.py`, receiver/profile modules) rather than treating the legacy surrogate as the publication receiver.

## Remaining equation mappings before final submission

- chirp slope and waveform phase law;
- one-way communication delay/Doppler;
- two-way sensing delay/Doppler;
- range resolution and positive-IF range support;
- unambiguous velocity and velocity resolution;
- effective rate;
- normalized resource cost;
- receiver-level range/velocity error definitions.
