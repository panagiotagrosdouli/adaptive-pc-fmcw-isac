# From Motion Forecasting to Predictive Connectivity

## Communication-Aware Trajectory Prediction and Predictive PC-FMCW/DPSK Vehicular Scheduling on WOMD

This repository is the research and reproducibility workspace for an end-to-end vehicular integrated sensing and communication study built around one central question:

> Can future vehicle motion, predicted causally from observed WOMD history, be converted into useful future PC-FMCW/DPSK link information and used to improve packet scheduling, timely delivered goodput, outage, PDR, latency and fairness?

The project is intentionally **not** a beam-selection/ADB paper anymore. The primary decision variable is now **which connected vehicle / packet is served, when it is served, and with what priority**. Beam-management and ADB code from the earlier research line is preserved only as legacy/reference material and must not be used as the main novelty claim of this paper.

---

## Scientific thesis

The paper tests whether geometric trajectory accuracy is sufficient for communication-aware decision making. The working thesis is:

> The value of motion prediction for vehicular optical scheduling is determined not only by ADE/FDE, but by how well predicted motion preserves communication-relevant quantities such as future SNR, BER/PER, goodput, outage and usable-link lifetime, and by the operating regime in which the scheduler acts.

The desired scientific result is **not** “prediction always wins”. Positive and negative operating regimes are both valid evidence. A publishable outcome may show that a communication-aware predictor improves link-state fidelity while scheduler-level gains depend on prediction horizon, number of connected vehicles, offered load, deadline pressure and scenario type.

---

## End-to-end causal pipeline

```text
Official WOMD motion
    |
    v
History-only trajectory predictor
    |
    v
Future relative geometry
(range, bearing, relative motion)
    |
    v
PC-FMCW / DPSK link model
    |
    v
Future SNR / BER / PER / goodput / outage
    |
    v
Predicted usable-link lifetime
    |
    +-------------------------+
    |                         |
    v                         v
Queues + deadlines       Communication-aware loss
    |                         |
    v                         |
Predictive scheduler <--------+
    |
    v
Ground-truth future link realization
    |
    v
Packet-level outcomes
Goodput / PDR / outage / deadline misses / P95 latency / Jain fairness
```

Only observed history is available to deployable predictors. Ground-truth future is used only for supervised targets, final evaluation and the information-oracle baseline.

---

## Research questions

**RQ1 — When does prediction help scheduling?**  Compare predictive schedulers against current-state/reactive scheduling across controlled operating regimes.

**RQ2 — Is the lowest-ADE/FDE predictor also the best communication predictor?**  Join geometric metrics with SNR/goodput/outage/link-lifetime fidelity and realized scheduler outcomes.

**RQ3 — Can communication-aware training improve downstream scheduling?**  Compare four learned objectives under the same architecture and training protocol.

**RQ4 — Optional extension: does predictive RL add value beyond a strong heuristic scheduler?**  RL is explicitly secondary and must not delay the core paper.

---

## Data protocol and scientific boundaries

The core mobility source is official Waymo Open Motion Dataset data. The paper protocol separates:

- **training**: deterministic scenario-level subset of official WOMD training data used for gradient updates;
- **development**: disjoint deterministic scenario-level subset of official WOMD training data used for early stopping, lambda selection, model selection and uncertainty calibration;
- **paper held-out**: untouched **official WOMD validation** used only after the protocol is frozen;
- **official hidden test**: optional leaderboard/challenge evaluation only.

The repository must maintain a zero-overlap scenario audit between train, development and official validation.

Important scientific wording: WOMD provides real vehicle motion. PC-FMCW/DPSK communication quantities in this repository are physics/model based unless explicitly backed by external physical measurements. Do not describe them as real PC-FMCW communication measurements.

---

## Canonical stage organization

The paper workflow is organized in `stages/`. Each stage is a research gate with its own scope, inputs, outputs, execution plan and acceptance criteria. Scientific implementation remains reusable rather than duplicated across stage folders.

| Stage | Folder | Purpose | Gate |
|---|---|---|---|
| 00 | `stages/00_freeze_and_provenance/` | Freeze code, datasets, split protocol, experiment contract | immutable manifests + zero overlap |
| 01 | `stages/01_womd_data_pipeline/` | Build/audit official training and validation mobility corpora | true-SDC, valid states, deterministic samples |
| 02 | `stages/02_pc_fmcw_dpsk_link/` | Freeze Part-A receiver-derived BER mapping and geometry-dependent link model | canonical LUT + config/hash |
| 03 | `stages/03_classical_baselines/` | Evaluate kinematic/classical predictors and non-learned schedulers | reproducible baseline tables |
| 04 | `stages/04_communication_aware_gru/` | Lambda sweep + four GRU objectives × five seeds | 20 verified checkpoints |
| 05 | `stages/05_official_predictor_evaluation/` | Untouched official-validation predictor/link evaluation | scenario-level held-out metrics |
| 06 | `stages/06_packet_scheduling/` | Reactive, classical predictive, learned and oracle packet scheduling | paired scheduler matrix + sweeps |
| 07 | `stages/07_statistics_and_figures/` | Scenario-clustered inference, joined ADE-vs-goodput analysis, figures/tables | CIs + multiplicity-controlled statistics |
| 08 | `stages/08_final_paper/` | Final claims, manuscript, supplement and reproduction bundle | submission gate |

Legacy `iscai_stage0`–`iscai_stage7` directories remain available for historical code and prior beam/ADB experiments. New paper work must follow the `stages/` plan above.

---

## Learned experiment matrix

The canonical learned architecture is evaluated with exactly four objectives under the same train/development protocol:

```text
GRU-Traj  : L_traj
GRU-Link  : L_traj + lambda_link * L_link
GRU-Out   : L_traj + lambda_out  * L_outage
GRU-Full  : L_traj + lambda_link * L_link + lambda_out * L_outage
```

Paper-scale evidence requires **5 paired seeds per objective**. Checkpoints are reusable only when their dataset hashes, normalization, architecture, selected lambdas and seed metadata match the frozen protocol exactly.

Every final checkpoint archive must record at least:

- dataset and split manifest hashes;
- seed;
- model architecture/configuration;
- normalization statistics;
- objective and lambda values;
- best epoch / stopping criterion;
- training/development metrics;
- code commit SHA.

---

## Predictor evaluation

Final official-validation evaluation must be scenario level and include both geometry and communication fidelity.

**Trajectory:** ADE, FDE.

**Geometry/link:** range MAE, bearing MAE, SNR error, predicted-goodput error, outage classification metrics, usable-link-lifetime error.

**Probabilistic/calibration:** NLL plus nominal-vs-empirical coverage (at minimum 50%, 90%, 95%) where the selected uncertainty method supports them.

A key artifact is the joined table:

```text
ADE/FDE
  <-> link-state fidelity
  <-> realized scheduler goodput / PDR / deadlines / latency
```

This enables the central test of whether predictor ranking changes when the downstream communication objective is considered.

---

## Scheduling evaluation

The final scheduler matrix should include, where implemented and scientifically compatible:

- Random / Round Robin;
- Reactive Greedy;
- proportional-fair or equivalent current-state baseline;
- classical predictive scheduling using CV/Kalman/IMM forecasts;
- GRU-Traj predictive scheduling;
- GRU-Link predictive scheduling;
- GRU-Out predictive scheduling;
- GRU-Full predictive scheduling;
- link-lifetime / predictive-utility heuristic;
- **information oracle** under the same heuristic family.

The oracle is an **information oracle**, not a proof of global optimality.

Main controlled sweeps:

- prediction horizon: `0.3 / 0.5 / 1.0 / 2.0 s`;
- connected vehicles: `3 / 5 / 10`;
- offered load: `0.35 / 0.55 / 0.75 / 0.90`;
- scenario slices: straight, approaching/receding, lane-change/merge, turn/intersection, FoV-edge and dense multi-user scenes.

Primary network KPIs: timely delivered goodput, PDR, outage, deadline misses, latency (including P95) and Jain fairness.

---

## Statistics policy

The final paper must not treat individual trajectory samples as independent evidence when scenarios are the experimental unit.

Required analysis:

- paired per-scenario comparisons;
- scenario-cluster bootstrap confidence intervals (10k resamples for final artifacts);
- paired Wilcoxon tests;
- paired t-test as sensitivity analysis where appropriate;
- effect sizes and win fractions;
- predeclared confirmatory families;
- Holm multiplicity correction;
- raw and adjusted p-values exported together.

The manuscript must remain consistent with both positive and negative results.

---

## Required publication artifacts

Final publication readiness requires all of the following:

```text
artifacts/paper_final/
├── manifests/          frozen code/data/split/config provenance
├── data_audit/         split overlap and integrity reports
├── ber/                final Part-A receiver-derived BER LUT
├── lambda_sweep/       raw sweep + frozen selection record
├── checkpoints/        4 objectives x 5 seeds
├── predictor_eval/     official-validation scenario metrics
├── scheduler_eval/     raw per-scenario x seed x policy results
├── statistics/         bootstrap, tests, effects, Holm outputs
├── joined_analysis/    ADE/link fidelity vs realized communication
├── figures/            publication SVG/PDF + preview PNG
├── tables/             CSV + LaTeX tables
├── complexity/         predictor/scheduler runtime evidence
└── reproduction/       immutable reproduction manifest/bundle
```

Large WOMD files and model checkpoints do not need to be committed to Git. Their manifests and hashes do.

---

## Submission gate

The paper is **not submission-ready** until all core items below are complete:

- [ ] final dataset manifests are frozen;
- [ ] train/dev/official-validation scenario overlap is exactly zero;
- [ ] canonical Part-A BER LUT and physical-layer config are hashed;
- [ ] lambda selection is completed without official-validation access;
- [ ] four learned objectives × five seeds are archived;
- [ ] untouched official-WOMD validation evaluation is complete;
- [ ] learned predictor uncertainty/NLL evaluation is complete;
- [ ] main scheduler matrix is complete;
- [ ] horizon / N / load / scenario-slice sweeps are complete;
- [ ] joined ADE/link-fidelity/realized-goodput analysis is complete;
- [ ] scenario-cluster bootstrap CIs are complete;
- [ ] Holm-adjusted confirmatory statistics are complete;
- [ ] final figures/tables are generated only from frozen final artifacts;
- [ ] claims are aligned with the evidence, including negative operating regimes;
- [ ] clean one-command reproduction path is documented;
- [ ] final manuscript and supplement compile successfully.

RL is optional and is explicitly outside this core submission gate.

---

## Current evidence status

The repository contains substantial historical implementation and preliminary evidence, but those results must not be confused with the final held-out paper evidence. In particular, the existing top-level README previously described the earlier uncertainty-aware trajectory-to-beam/ADB research direction; that is now treated as legacy context rather than the active paper scope.

Current learned results should be labeled **internal-development / preliminary** unless they were produced under the final frozen official-validation protocol.

---

## Reproducibility principles

1. Never use future states as predictor inputs.
2. Split by scenario, never by trajectory row when leakage is possible.
3. Never tune lambdas, thresholds or hyperparameters on official validation.
4. Freeze normalization from training data only.
5. Use the same architecture/schedule when comparing learned objectives.
6. Archive raw scenario-level results before aggregation.
7. Keep real mobility and simulated/model-based communication claims clearly separated.
8. Preserve failed/negative regimes; do not cherry-pick only improvements.
9. Generate manuscript numbers from frozen artifacts rather than manually typing them.
10. Record commit SHA, config hashes and dataset hashes for every final experiment.

---

## Quick start

For legacy code/tests, follow the existing package requirements. For the new paper workflow, begin with Stage 00 and do not advance past a gate until its acceptance criteria are met.

```bash
# inspect the research plan
find stages -maxdepth 2 -type f | sort

# run repository tests appropriate to the checked-out environment
pytest -q
```

Dataset-dependent stages require locally licensed WOMD data. The repository must not redistribute Waymo raw data.

---

## Paper title candidates

Primary:

**From Motion Forecasting to Predictive Connectivity: Trajectory-Aware Link Scheduling for PC-FMCW Vehicular Integrated Sensing and Communication**

Technical alternative:

**Communication-Aware Trajectory Prediction and Predictive Link Scheduling for PC-FMCW Vehicular ISAC**

---

## Status vocabulary

Use only these labels in stage reports:

- `DONE` — code, execution, artifacts and acceptance criteria all complete;
- `PARTIAL` — implementation exists but required final evidence is incomplete;
- `BLOCKED` — a required external dependency or dataset is unavailable;
- `NOT_STARTED` — no final implementation/evidence yet.

A script existing in the repository does **not** make a stage DONE. Final status requires real execution on the specified data and successful acceptance-gate checks.
