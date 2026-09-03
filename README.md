# From Motion Forecasting to Predictive Connectivity

## Communication-Aware Trajectory Prediction and Predictive PC-FMCW/DPSK Vehicular Scheduling on WOMD

This repository is the research and reproducibility workspace for an end-to-end vehicular integrated sensing and communication study built around one central question:

> Can future vehicle motion, predicted causally from observed WOMD history, be converted into useful future PC-FMCW/DPSK link information and used to improve packet scheduling, timely delivered goodput, outage, PDR, latency and fairness?

The active paper is **not** a beam-selection/ADB paper. The main decision variable is which connected vehicle or packet is served, when it is served, and with what priority. Earlier beam-management and ADB code is preserved only as legacy/reference material.

## Research pipeline

```text
Official WOMD motion
        |
        v
Causal history construction
        |
        v
Trajectory prediction
(classical + learned communication-aware GRU)
        |
        v
Future actor-SDC relative geometry
(range, bearing, relative motion)
        |
        v
PC-FMCW / DPSK link prediction
(SNR, BER/PER, goodput, outage, link lifetime)
        |
        v
Queues + deadlines + offered load
        |
        v
Reactive / predictive / oracle scheduling
        |
        v
Packet-level communication outcomes
(goodput, PDR, outage, deadline misses, latency, fairness)
        |
        v
Scenario-clustered statistics + paper artifacts
```

Only observed history is available to deployable predictors. Ground-truth future states are used only as supervised targets, held-out evaluation truth, and for the explicitly labelled information-oracle baseline.

## Repository structure

The top level is organized to make the paper workflow visible immediately, following a staged research layout while keeping one canonical implementation per scientific component.

| Directory | Purpose |
| --- | --- |
| `predictive_data_prep/` | Entry point for dataset manifests, split ownership, data-preparation and corpus-audit workflow. |
| `predictive_stage0/` | Freeze code, datasets, experiment protocol, hashes and zero-overlap provenance. |
| `predictive_stage1/` | WOMD causal data construction, true-SDC future geometry and canonical mobility corpus audits. |
| `predictive_stage2/` | Part-A-derived DPSK BER calibration, frozen link configuration and geometry-dependent PC-FMCW/DPSK link model. |
| `predictive_stage3/` | Classical trajectory predictors and non-learned scheduling baselines. |
| `predictive_stage4/` | Communication-aware GRU objectives, lambda selection, five-seed training, calibration and learned evaluation. |
| `predictive_stage5/` | Untouched official-WOMD predictor and link-fidelity evaluation. |
| `predictive_stage6/` | Packet traffic, queues, deadlines, reactive/predictive schedulers and controlled operating-regime sweeps. |
| `predictive_stage7/` | Scenario-clustered statistics, ADE-vs-link-vs-scheduler joins, figures and tables. |
| `predictive_stage8/` | Final manuscript, supplement, runtime evidence and one-command reproduction bundle. |
| `stages/` | Canonical active implementations and machine-readable `stage.json` contracts for Stages 00-08. |
| `part_a_reference/` | Frozen reference material from the PC-FMCW/DPSK Part-A implementation used only for continuity and calibration provenance. |
| `artifacts/` | Publication artifact workspace; final evidence belongs under `artifacts/paper_final/`. |
| `audits/` | Human- and machine-readable audit entry point. |
| `manifests/` | Provenance and experiment-manifest entry point. |
| `iscai_stage0/`-`iscai_stage7/` | Historical beam/ADB research code retained as legacy/reference material; not the active paper workflow. |

The `predictive_stage*` directories are navigation entry points. Scientific code remains canonical inside `stages/` so that the repository does not silently maintain two implementations of the same method.

## Stage overview

### Stage 0 — Freeze and provenance

Stage 0 freezes the exact code revision, dataset identities, split protocol, experiment configuration and overlap audits before final evidence is generated. A stage is not complete because a script exists; the required manifests must be produced by a real run and pass their acceptance checks.

### Stage 1 — WOMD mobility corpus

Stage 1 constructs the causal trajectory corpus from WOMD. The canonical geometry distinguishes actor future position in the SDC-at-anchor coordinate frame from communication-relative future geometry. For communication evaluation,

```text
future_relative_xy(t) = actor_future_xy(t) - true_sdc_future_xy(t)
```

in the common anchor orientation. The SDC itself is not a communication target. Train/development ownership is scenario-level, while official WOMD validation remains an untouched held-out split.

### Stage 2 — PC-FMCW / DPSK link model

Stage 2 freezes the Part-A receiver-derived DPSK BER mapping and the paper's explicit geometry-to-link extension. WOMD supplies real motion; SNR, BER/PER, goodput, outage and link lifetime are model-based communication quantities unless separately supported by physical measurements.

### Stage 3 — Classical baselines

Stage 3 provides causal kinematic predictors and non-learned scheduler baselines. Predictor evaluation uses the same true-SDC relative geometry as the learned pipeline. The information oracle is an information-access upper-reference baseline, not a proof of globally optimal scheduling.

### Stage 4 — Communication-aware GRU

Stage 4 uses one shared architecture for four objectives:

```text
GRU-Traj : L_traj
GRU-Link : L_traj + lambda_link * L_link
GRU-Out  : L_traj + lambda_out * L_outage
GRU-Full : L_traj + lambda_link * L_link + lambda_out * L_outage
```

The final archive requires five paired seeds per objective, exactly 20 accepted checkpoints, training-only normalization, development-only hyperparameter selection and development-fitted uncertainty calibration. Official validation cannot be used for selection.

### Stage 5 — Official predictor evaluation

Stage 5 evaluates frozen predictors on untouched official WOMD validation. Required scenario-level outputs include ADE/FDE, range and bearing errors, SNR and goodput fidelity, outage metrics, usable-link-lifetime error, and NLL plus 50/90/95% coverage where the selected uncertainty method supports them.

### Stage 6 — Packet scheduling

Stage 6 evaluates reactive, proportional-fair, classical predictive, learned predictive, link-lifetime/predictive-utility and information-oracle schedulers under identical traffic and link realizations. Main controlled sweeps cover prediction horizon, connected-vehicle count, offered load and scenario type.

### Stage 7 — Statistics and figures

Stage 7 treats scenario as the experimental unit. Final analyses use paired per-scenario comparisons, 10k scenario-cluster bootstrap confidence intervals, paired Wilcoxon tests, t-test sensitivity analyses where appropriate, effect sizes, win fractions and Holm multiplicity correction. It also joins trajectory error, link-state fidelity and realized scheduler performance.

### Stage 8 — Final paper

Stage 8 freezes final claims, manuscript source, supplement, vector figures, LaTeX tables, runtime evidence and the reproduction bundle. Positive and negative operating regimes must both remain visible in the final paper.

## Scientific thesis

The paper tests whether geometric trajectory accuracy is sufficient for communication-aware decision making. The working thesis is:

> The value of motion prediction for vehicular optical scheduling is determined not only by ADE/FDE, but by how well predicted motion preserves communication-relevant quantities such as future SNR, BER/PER, goodput, outage and usable-link lifetime, and by the operating regime in which the scheduler acts.

The desired scientific result is not “prediction always wins”. A valid result may show that communication-aware prediction improves link-state fidelity while network-level benefit depends on prediction horizon, user count, offered load, deadline pressure and scenario geometry.

## Research questions

**RQ1 — When does prediction help scheduling?** Compare predictive schedulers against current-state/reactive scheduling across controlled operating regimes.

**RQ2 — Is the lowest-ADE/FDE predictor also the best communication predictor?** Join geometric metrics with SNR/goodput/outage/link-lifetime fidelity and realized scheduler outcomes.

**RQ3 — Can communication-aware training improve downstream scheduling?** Compare the four learned objectives under the same architecture and training protocol.

**RQ4 — Optional extension: does predictive RL add value beyond a strong heuristic scheduler?** RL is secondary and must not delay the core paper.

## Data protocol and scientific boundaries

The core mobility source is official Waymo Open Motion Dataset data. The paper protocol separates training, development, untouched official WOMD validation, and optional hidden-test evaluation. The repository must preserve scenario-level zero overlap between training, development and official validation.

WOMD provides real vehicle motion. PC-FMCW/DPSK communication quantities in this repository are physics/model based unless explicitly backed by external physical measurements. They must not be described as real WOMD communication measurements.

## Learned experiment matrix

Paper-scale learned evidence requires five paired seeds for each of the four objectives. A checkpoint is reusable only when dataset hashes, normalization, architecture, objective, selected lambdas, seed metadata and code revision match the frozen protocol.

Every final checkpoint archive must record dataset/split hashes, seed, architecture, normalization, objective and lambda values, best epoch/stopping criterion, training/development metrics and code commit SHA.

## Predictor evaluation

Final official-validation evaluation is scenario-level and combines trajectory accuracy, communication-link fidelity and uncertainty calibration. A central analysis artifact is the joined relationship

```text
ADE/FDE
  <-> future link-state fidelity
  <-> realized scheduler goodput / PDR / deadlines / latency
```

which tests whether predictor ranking changes when the downstream communication objective is considered.

## Scheduling evaluation

The main scheduler family includes Random/Round Robin, Reactive Greedy, proportional-fair/current-state scheduling, classical predictive schedulers using CV/Kalman/IMM forecasts, the four learned GRU variants, predictive-utility/link-lifetime scheduling, and the information oracle where scientifically compatible.

The main controlled grid is prediction horizon `0.3 / 0.5 / 1.0 / 2.0 s`, connected vehicles `3 / 5 / 10`, offered load `0.35 / 0.55 / 0.75 / 0.90`, plus motion/FoV-edge/density scenario slices. Primary network KPIs are timely delivered goodput, PDR, outage, deadline misses, latency including P95, and Jain fairness.

## Publication artifacts

```text
artifacts/paper_final/
├── manifests/          frozen code/data/split/config provenance
├── data_audit/         split overlap and integrity reports
├── ber/                final Part-A receiver-derived BER LUT
├── lambda_sweep/       raw sweep + frozen selection record
├── checkpoints/        four objectives x five seeds
├── predictor_eval/     official-validation scenario metrics
├── scheduler_eval/     raw per-scenario x seed x policy results
├── statistics/         bootstrap, tests, effects, Holm outputs
├── joined_analysis/    ADE/link fidelity vs realized communication
├── figures/            publication SVG/PDF + preview PNG
├── tables/             CSV + LaTeX tables
├── complexity/         predictor/scheduler runtime evidence
└── reproduction/       immutable reproduction manifest/bundle
```

Large WOMD files and model checkpoints do not need to be committed to Git; their manifests and hashes do.

## Reproducibility philosophy

The repository uses a staged freeze-and-audit workflow. Future states are never predictor inputs; splits are scenario-level; official validation is never used for model selection; normalization is fitted on training only; learned objective comparisons share architecture and schedule; raw scenario-level outputs are archived before aggregation; real mobility and model-based communication claims remain separate; negative regimes are retained; final manuscript numbers must be generated from frozen artifacts; and every final experiment records code/config/data provenance.

## Quick start

```bash
# inspect the active paper workflow
find stages -maxdepth 2 -type f | sort

# run repository tests appropriate to the checked-out environment
pytest -q
```

Dataset-dependent stages require locally licensed WOMD data. The repository does not redistribute Waymo raw data.

## Paper title candidates

Primary:

**From Motion Forecasting to Predictive Connectivity: Trajectory-Aware Link Scheduling for PC-FMCW Vehicular Integrated Sensing and Communication**

Technical alternative:

**Communication-Aware Trajectory Prediction and Predictive Link Scheduling for PC-FMCW Vehicular ISAC**

## Status vocabulary

Use only these labels in stage reports:

- `DONE` — implementation, execution, artifacts and acceptance criteria are complete;
- `PARTIAL` — implementation/evidence exists but required final evidence is incomplete;
- `BLOCKED` — a required external dependency or dataset is unavailable;
- `NOT_STARTED` — final implementation/evidence has not begun.

A script existing in the repository does not make a stage `DONE`. Final status requires real execution on the specified data and successful acceptance-gate checks.
