# Part B Scientific Research Audit

## Scope

This audit evaluates the repository against the university Part B requirement: **propose a technique, method, or scheme that improves system performance**, with scientific-paper-level rigor and reproducibility.

The proposed method remains **Physics-Gated Reliability-Constrained Adaptive PC-FMCW ISAC**. The repository studies a model-based 77-GHz RF/mmWave vehicular PC-FMCW ISAC PHY. It does not provide new RF measurements and must not describe simulation outputs as measured hardware performance.

The relationship to the Part A optical PC-FMCW laser-headlamp work is conceptual and PHY-level: this repository extends the PC-FMCW ISAC idea into robust high-mobility RF/mmWave PHY adaptation. It is not an experimentally measured improvement on the original optical hardware.

## Repository-wide implementation status

### Implemented and scientifically usable

- PC-FMCW waveform and dechirped-IF sensing model.
- One-way DBPSK communication reference model separated from the two-way monostatic radar echo.
- Literature-grounded short-range and high-mobility capability profiles with analytical range/velocity limits.
- Physics feasibility gate.
- Finite frozen PHY action codebook.
- B0 fixed, B1 communication-only, B2 sensing-only, B3 deterministic joint, B4 robust joint, and hindsight Oracle policies.
- Reliability-aware B4 selector using finite uncertainty draws and a one-sided Wilson lower confidence bound.
- Frozen QoS thresholds, seeds, action space, protocol semantics, and no-post-hoc-tuning rule.
- Large paired primary Monte-Carlo benchmark: 12,000 states per policy / 72,000 receiver-level policy evaluations.
- Paired bootstrap confidence intervals for key B4-vs-baseline joint-QoS differences.
- DBPSK AWGN sanity validation and residual-frequency-error stress evidence.
- FMCW analytical/range-velocity validation infrastructure.
- SNR/range and SNR/velocity/CFO/INR operating-region analyses.
- Extended uncertainty sweep.
- Physics-gate, state-uncertainty, and joint-objective ablations.
- Model-mismatch experiments.
- Physical-resource Pareto reporting.
- Runtime/complexity measurements.
- CI, tests, manuscript compilation audit, provenance hashes, deterministic packaging, and machine-readable summary artifacts.
- IEEE-style manuscript with explicit simulation-versus-measurement claim boundary.

### Implemented but limited / diagnostic

- Stage-7 waveform/receiver pilot validation is diagnostic rather than part of the immutable final policy benchmark.
- Phase-noise is treated as a controlled stochastic sensitivity parameter; it is not calibrated to a specific hardware oscillator mask.
- E9 primary frozen feasibility-cell flags use empirical means rather than confidence-qualified lower bounds. They should not be called 95% reliability guarantees.
- The main frozen E11 ablation bank is small; stronger component ablations are supplied by the later supplemental workflow.
- Runtime is Python/GitHub-Actions runtime, not embedded automotive real-time performance.
- The high-mobility waveform profile is a composite capability reference, not a claimed commercial preset.

### Still scientifically incomplete for a strong archival publication

- The primary frozen benchmark does not report a full metric table containing BER, PER, effective rate, range RMSE, velocity RMSE, reliability-constraint violation rate, infeasible-state probability, profile-selection frequency, and runtime for every B0--B4/Oracle policy in one publication artifact.
- PER is not established as a headline primary benchmark metric in the committed final summary.
- Reliability-target sweeps are not presented as a dedicated final experiment family, despite being requested by the project-level research question.
- A full communication--sensing--resource Pareto **frontier** is not established by the primary final artifact; the frozen primary artifact contains only one B4 Pareto point, while the supplemental analysis improves reporting but remains a finite selected-action sample rather than a comprehensive action/QoS frontier.
- The interference × synchronization-error map needs confidence-qualified feasibility labeling to support reliability-guarantee language.
- Statistical testing is strongest for unconditional joint-QoS paired differences. Comparable paired effect estimates / confidence intervals for resource cost, outage/selection, BER/rate, and sensing errors would strengthen publication claims.
- Individual uncertainty-source ablations are incomplete as a full factorial scientific decomposition. CFO and interference ablations exist, and extended component ablations exist, but SNR-estimation, IF-SNR/sensing-state, velocity-state, synchronization, and combined interactions are not all isolated with matched statistical power.
- The literature/venue audit is still a publication blocker distinct from code correctness.
- No hardware or over-the-air validation exists; this is acceptable for Part B if represented accurately, but it prevents claims of real-world validation.

## Scientifically supported primary finding

The strongest supported finding is not unconditional superiority. The frozen primary benchmark shows that B4 is substantially more conservative than B3: it selects fewer states but achieves markedly higher conditional joint sensing/communication reliability on the selected set. In the primary frozen benchmark, B4 reaches 100% observed conditional joint QoS over 1,468 selected states, with a one-sided 95% Wilson lower bound of approximately 0.9982. However, its unconditional joint-QoS probability is lower than B3 because it abstains much more often.

This is best described as a **reliability--availability trade-off**: the robust uncertainty-aware controller contracts the operating region to maintain reliability rather than maximizing unconditional success probability.

## Negative and null results that must remain visible

- B4 does **not** improve unconditional joint QoS over B3 in the frozen benchmark; the paired B4-minus-B3 difference is negative with a confidence interval excluding zero.
- B4 also does not outperform B0 in unconditional joint QoS.
- Severe model mismatch defeats the robust policy: high actual interference and sufficiently poor actual SNR produce collapse/failure in the tested banks.
- At the most severe uncertainty sweep point, B4's observed conditional reliability remains high but its Wilson lower bound no longer confidence-qualifies the declared 0.95 target.
- Removing CFO or interference in the small frozen E11 bank does not change aggregate selection rate; these are null aggregate ablation results for that state bank.
- The unoptimized 512-draw B4 Python implementation is far slower than B3 and is not demonstrated to satisfy real-time vehicular latency.

## Part B suitability

**Yes.** The repository already exceeds the minimum Part B requirement. It proposes a precise method, provides a mathematically defined controller, uses fair named baselines and an Oracle, validates physical and receiver models, executes large paired Monte-Carlo studies, retains negative results, and documents reproducibility and limitations.

The appropriate Part B claim is not "B4 always improves performance." Instead:

> Physics-gated uncertainty-aware joint adaptation can improve **conditional reliability and robustness of selected PC-FMCW operating states** relative to deterministic adaptation, while introducing a measurable loss in availability and a substantial computational cost. The benefit is strongest in moderate uncertainty/mismatch regimes and disappears under severe mismatch.

That is a legitimate and scientifically stronger answer to the Part B requirement because the method improves a defined performance dimension while explicitly quantifying its costs and failure region.

## Publication readiness

**Near publication-grade as a reproducible simulation study, but not fully archival-publication-ready.** The repository has a strong paper structure and substantial evidence, but a genuinely complete submission should add the missing primary-metric/statistics consolidation, dedicated reliability-target sweep, confidence-qualified feasibility maps, fuller Pareto frontier, and broader individual uncertainty-source ablations. Venue-specific bibliography and PDF/source compliance remain external submission tasks.

## Recommended final completion gate

Before calling the work fully publication-ready, require all of the following:

1. one frozen machine-readable policy-level table for every requested metric;
2. PER and profile-selection-frequency reporting;
3. reliability-target sweep with paired B3/B4 evaluation;
4. confidence-qualified SNR×velocity and INR×synchronization maps;
5. full physical-resource Pareto frontier rather than a single primary point;
6. matched individual uncertainty-source ablations;
7. paired CIs/effect sizes for resource, outage/selection, communication, and sensing metrics;
8. immutable raw artifacts and manifest for the added experiments;
9. manuscript sections explicitly named Metrics, Statistical Analysis, Ablation Studies, Robustness Analysis, and Reproducibility Statement or clear equivalent subsections;
10. venue-level scholarly and PDF compliance audit.
