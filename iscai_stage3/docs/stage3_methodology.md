# Stage 3 methodology: uncertainty-aware data association

## 1. Status and scope

This document specifies a research hypothesis and its evaluation protocol. It
does not claim experimental superiority or novelty prior to a complete
literature review and empirical validation.

Stage 3 consumes the truth-free Stage-2 detection frames and produces causal
tracklet distributions in the common anchor frame `H0`. WOMD identities,
classes, future states, and Stage-2 truth sidecars are evaluator-only.

## 2. Scientific question

Can PC-FMCW measurement uncertainty be used to activate multiple association
hypotheses only when ambiguity is both statistically significant and relevant
to downstream trajectory-to-beam/ADB decisions?

The primary hypothesis is that adaptive branching can approach fixed-depth MHT
robustness under ambiguous detections with lower average hypothesis count and
runtime. A secondary hypothesis is that downstream-aware pruning improves beam
and ADB risk without necessarily improving conventional tracking error.

## 3. Inputs and coordinate contract

At causal time `t`, Stage 2 provides an unlabeled detection set

\[
Z_t = \{z_{i,t}, R_{i,t}\}_{i=1}^{m_t},
\quad
z_{i,t}=[r,\dot r,\phi,\theta]^\top.
\]

`R_i,t` is measurement covariance, not predictive covariance. Each spherical
position and its covariance are transformed from the time-varying `Ht` frame to
the common `H0` frame before temporal association. Range, azimuth, and elevation
covariance is propagated with the full first-order Jacobian.

## 4. Association model

For predicted track `j` and detection `i`, define innovation and covariance

\[
\nu_{ji,t}=y_{i,t}-\hat y_{j,t|t-1},
\qquad
S_{ji,t}=H P_{j,t|t-1}H^\top+R^{H0}_{i,t}.
\]

The squared Mahalanobis distance is

\[
d^2_{ji,t}=\nu_{ji,t}^\top S_{ji,t}^{-1}\nu_{ji,t}.
\]

Associations outside a declared chi-square gate are infeasible. Feasible
association log-scores include the normalized Gaussian likelihood, detection
probability, and clutter density. All terms and thresholds must be versioned in
configuration; none may be fitted on the evaluation split.

## 5. Association ambiguity

Normalize the feasible association scores, including the missed-detection
hypothesis, into probabilities `p_j,i,t`. Define normalized entropy

\[
\bar H_{j,t}=
-\frac{\sum_i p_{ji,t}\log p_{ji,t}}
{\log |\mathcal A_{j,t}|},
\]

with entropy zero when only one hypothesis is feasible. Branching is activated
when entropy exceeds `tau_entropy`; otherwise the GNN assignment is retained.
The threshold is selected on validation data only.

## 6. Proposed DASH-Track hypothesis

**DASH-Track** is a working name for Downstream-Aware Sensing-Hypothesis
Tracking. It consists of:

1. CRLB/covariance-conditioned gating and likelihoods.
2. Entropy-triggered association branching.
3. Fixed `K_max` and `N_scan` controls for bounded computation.
4. Hypothesis merging when state distributions and downstream actions are
   equivalent within declared tolerances.
5. Propagation of association mixtures rather than only the MAP identity.

The first two components are the core Stage-3 proposal. Downstream-aware
merging is evaluated as a separate extension so its contribution is measurable.

## 7. Downstream relevance

For hypothesis `h`, let the later frozen Stage-4/5/6 stack produce a predicted
beam-coverage distribution and ADB risk vector `q_h`. Two tracking hypotheses
may be merged only if both conditions hold:

\[
D_{state}(h_a,h_b) < \epsilon_{state},
\qquad
D_{down}(q_{h_a},q_{h_b}) < \epsilon_{down}.
\]

The first implementation must use a deterministic analytical distance. Learned
or RL pruning is outside the Stage-3 primary experiment. To avoid circular
evaluation, downstream pruning parameters are tuned on validation scenarios and
the final downstream evaluator remains frozen on the test split.

## 8. Required baselines

1. Oracle association, evaluator-only upper bound.
2. Euclidean GNN.
3. Mahalanobis/CRLB-aware GNN.
4. Soft probabilistic association (JPDA/BP-family baseline).
5. Fixed-depth MHT with identical motion and measurement models.
6. Entropy-triggered branching without downstream pruning.
7. DASH-Track with downstream-aware merging.

All non-association components must be held constant when comparing methods.

## 9. Ablation matrix

| Experiment | CRLB covariance | Entropy trigger | Multiple hypotheses | Downstream merging |
|---|---:|---:|---:|---:|
| GNN-E | No | No | No | No |
| GNN-C | Yes | No | No | No |
| Fixed MHT | Yes | No | Yes | No |
| Adaptive | Yes | Yes | Yes | No |
| DASH-Track | Yes | Yes | Yes | Yes |

Additional ablations vary entropy threshold, `K_max`, `N_scan`, covariance
scaling, false-alarm density, detection probability, and SNR.

## 10. Metrics

Tracking metrics include GOSPA, association accuracy, ID switches,
fragmentation, track recall/precision, state RMSE, NLL, NEES/coverage, runtime,
peak memory, and active-hypothesis count.

Downstream metrics include trajectory ADE/FDE/NLL, beam hit and outage
probability, angular coverage calibration, ADB unsafe-illumination rate, and
end-to-end runtime.

Results must be paired by scenario and random seed. Report confidence intervals
and paired effect sizes; do not infer improvement from means alone. Clean and
degraded conditions use identical scenario splits.

## 11. Failure and falsification criteria

The primary hypothesis is rejected if adaptive branching does not improve the
robustness-runtime Pareto frontier over CRLB-aware GNN and fixed MHT. The
downstream extension is rejected if it reduces tracking cost but worsens beam or
ADB safety, or if gains disappear under held-out seeds/SNR levels.

Boundary cases include crossing targets, close range/angle separation, long
missed-detection runs, high clutter, covariance miscalibration, and coordinate
transform perturbations.

## 12. Implementation order

1. Freeze common tracking contracts and scenario/seed splits.
2. Complete covariance-aware GNN baseline.
3. Implement fixed-depth MHT using the same likelihood.
4. Add entropy measurement and adaptive branching.
5. Validate tracking-only experiments.
6. Freeze downstream utility interface.
7. Add downstream-aware merging and perform the final ablation.
