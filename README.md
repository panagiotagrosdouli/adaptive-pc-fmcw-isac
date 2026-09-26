# Physics-Gated Reliability-Constrained Adaptive PC-FMCW ISAC

A reproducible research framework for **high-mobility vehicular phase-coded FMCW integrated sensing and communication (PC-FMCW ISAC)**.

## Paper status

The repository contains an IEEEtran manuscript supported by a frozen, provenance-linked publication-v2.1 simulation study. The evidence is **model-based, analytical, statistical, and host-runtime evidence**; it is not a new RF hardware or field-measurement campaign. The paper does not claim standards compliance, production deployment, universal robustness, or embedded real-time operation.

The primary scientific result is a **reliability--availability--computation trade-off** under the declared finite action set and evaluated uncertainty models. In particular, the robust B4 policy provides stronger selected-case reliability evidence while selecting fewer operating states than the deterministic B3 policy; the frozen paired benchmark does not support unconditional B4 superiority.

![Project overview](docs/project_overview.jpg)

> **Research question:** Which PC-FMCW PHY configuration is physically feasible, and which feasible configuration should be selected when communication reliability and radar sensing quality must be maintained simultaneously under mobility and imperfect PHY knowledge?

The central idea is **physics-gated robust adaptation**. A candidate waveform/profile is first rejected if its FMCW sampling, range, or unambiguous-velocity limits cannot support the operating state. The remaining configurations are evaluated under joint communication and sensing QoS constraints with uncertainty in SNR, Doppler/residual synchronization, interference, and state knowledge.

## Scientific positioning

This work builds on the established PC-FMCW sensing-and-communication literature; it does **not** claim phase coding, FMCW sensing, DBPSK, range--Doppler processing, or generic ISAC as new. The contribution is to move from fixed-configuration functional feasibility toward **physics-gated, reliability-constrained adaptive operation under high-mobility PHY uncertainty**.

The project studies an **RF/mmWave 77-GHz vehicular PC-FMCW ISAC PHY**, not the optical laser-headlamp/ADB system discussed in related work. Trajectory forecasting, ego-motion planning, packet/user scheduling, beam management, adaptive driving-beam illumination, and Hough tracking are outside the claimed contribution.

> **Contribution in one sentence:** We extend PC-FMCW ISAC from fixed-configuration functional feasibility to physics-gated, reliability-constrained PHY adaptation under high-mobility uncertainty, and characterize the evaluated operating region in which vehicular communication and sensing QoS can be jointly supported under the declared simulation and uncertainty model.

See [`docs/CONTRIBUTION_POSITIONING.md`](docs/CONTRIBUTION_POSITIONING.md), [`docs/EVIDENCE_MAP.md`](docs/EVIDENCE_MAP.md), and [`paper/CLAIM_AUDIT.md`](paper/CLAIM_AUDIT.md).

## Frozen scientific baseline

The publication-v2.1 scientific baseline is frozen at commit:

```text
3904c4c2a69c4af96751d64614f7228ddea24b56
```

Submission-readiness work originally developed on `paper/submission-ready` was merged into `main` by PR #57. Frozen evidence under `artifacts/publication/v2_1/` remains preserved. Later audit/repair work must not rewrite that historical evidence family; post-freeze changes are recorded in [`docs/SUBMISSION_CHANGELOG.md`](docs/SUBMISSION_CHANGELOG.md).

## System model

```text
                    physical operating state
        SNR / range / velocity / Doppler / interference
                 / synchronization uncertainty
                              |
                              v
                +---------------------------+
                |   PHY state estimation    |
                +-------------+-------------+
                              |
                              v
                +---------------------------+
                |   Physics feasibility     |
                |          gate             |
                +-------------+-------------+
                              |
                    feasible actions only
                              |
                              v
                +---------------------------+
                | Reliability-constrained   |
                |     PHY adaptation        |
                +-------------+-------------+
                              |
                  PC-FMCW configuration
                              |
                +-------------+-------------+
                |                           |
                v                           v
       communication receiver       radar sensing receiver
        DBPSK / BER / rate          dechirp / range-Doppler
```

The radar ADC samples the **dechirped IF/beat signal**, not the 77-GHz carrier. The communication path is modeled as a separate one-way link; the sensing echo is monostatic and two-way.

## 77-GHz capability profiles

### Source-grounded parking profile

- carrier: 77 GHz;
- valid sweep: 858 MHz;
- active chirp: 25.6 us;
- chirp repetition interval: 115.8 us;
- IF ADC: 10 MS/s;
- 256 samples/chirp;
- 64 chirps/frame.

Derived analytical scales:

- range resolution: approximately **0.175 m**;
- positive-IF range support: approximately **22.36 m**;
- radial-velocity resolution: approximately **0.263 m/s**;
- maximum unambiguous radial velocity: approximately **8.41 m/s**.

### Composite high-mobility capability profile

- carrier: 77 GHz;
- sweep: 1 GHz;
- active/repetition timing: 20 us;
- ADC capability: 37.5 MS/s;
- 750 samples/chirp;
- 128 chirps/frame.

Derived analytical scales:

- range resolution: approximately **0.150 m**;
- positive-IF range support: approximately **56.21 m**;
- radial-velocity resolution: approximately **0.760 m/s**;
- maximum unambiguous radial velocity: approximately **48.67 m/s**.

The high-mobility profile is a **composite capability reference**, not a claim that a commercial radar ships with this exact preset.

## Communication reference

The reference modem removes the known FMCW chirp and decodes a multi-chip DBPSK phase sequence. With 32 chips/chirp in the parking profile, the raw reference rate is approximately **276.3 kb/s**. The diagnostic implementation is checked against the analytical noncoherent DBPSK AWGN expression; these are simulation outputs, not RF measurements.

## Frozen 54-action PHY space

Each action contains:

- profile: 2 choices;
- chips/chirp: 16, 32, 64;
- transmit-power backoff: 0, 3, 6 dB;
- repetition factor: 1, 2, 4.

Therefore the frozen action set contains `2 x 3 x 3 x 3 = 54` configurations.

## Policies

- **B0 — Fixed PHY:** one frozen configuration when physically admissible.
- **B1 — Communication-only adaptive:** minimum declared resource cost subject to communication-side selector constraints.
- **B2 — Sensing-only adaptive:** minimum declared resource cost subject to sensing-side selector constraints.
- **B3 — Deterministic joint ISAC:** joint communication+sensing selector treating the estimated state as exact.
- **B4 — Robust joint ISAC:** physics gate plus uncertainty draws and one-sided Wilson confidence qualification.
- **Oracle:** hindsight true-state receiver-level minimum-resource successful action; non-deployable reference only.

Detailed semantics are in [`docs/POLICY_DEFINITIONS.md`](docs/POLICY_DEFINITIONS.md).

## Frozen v2.1 protocol

QoS thresholds:

- BER <= `1e-3`;
- effective rate >= `100000 bit/s`;
- range RMSE <= `1 m`;
- velocity RMSE <= `1 m/s`;
- joint reliability target = `0.95`.

Primary paired benchmark:

- seed start: `10000`;
- final seeds: `1000`;
- scenarios per seed: `12`;
- state/seed units per policy: `12000`;
- policies: `6`;
- receiver-level evaluations: `72000`;
- communication bits per final evaluation: `20000`;
- sensing trials per final evaluation: `3`;
- paired-bootstrap resamples: `10000`;
- B4 internal draws: `512`;
- B4 acceptance: one-sided 95% Wilson lower bound >= 0.95.

Thresholds were frozen before final v2.1 evaluation; no post-hoc threshold tuning is permitted.

## Frozen primary result

B4 is **not** unconditionally superior to B3.

- B3 selection: approximately `19.07%`;
- B3 conditional joint QoS: approximately `84.83%`;
- B3 unconditional joint QoS: approximately `16.18%`;
- B4 selection: approximately `12.23%`;
- B4 selected successes: `1468/1468`;
- B4 one-sided 95% Wilson lower conditional bound: approximately `99.816%`;
- B4 unconditional joint QoS: approximately `12.23%`;
- paired B4-B3 unconditional difference: approximately `-0.03942`;
- 95% paired-bootstrap interval: approximately `[-0.04292, -0.03600]`.

The supported interpretation is a **reliability--availability--computation trade-off**: under the frozen evaluated simulation protocol, B4 identifies a smaller confidence-qualified operating subset with stronger selected-case reliability evidence. This is not a field-reliability guarantee or a claim of universal B4 superiority.

## Experiment families

The repository implements and/or preserves evidence for:

- E1 analytical/waveform sanity checks;
- E2 communication BER validation;
- E3 FMCW range/velocity validation;
- E4 high-mobility Doppler/synchronization stress;
- E5 interference/phase-noise stress;
- E6 B0--B4 + Oracle comparison;
- E7 uncertainty sweeps;
- E8 reliability-target sweeps;
- E9 physical feasible-region mapping;
- E10 communication--sensing--resource Pareto analysis;
- E11 ablations and model mismatch;
- E12 large-seed paired statistics/runtime/reproduction evidence;
- finite-draw calibration;
- uncertainty-source ablations;
- distribution shift;
- action-space sensitivity;
- confidence maps.

Negative results are retained rather than hidden.

## Repository layout

```text
configs/                 frozen and literature-grounded experiment configurations
docs/                    positioning, provenance, evidence maps and reproducibility
src/pcfmcw_isac/         waveform, receiver, physics, policy and statistics code
scripts/                 reproducible validation and experiment entry points
tests/                   physical/statistical invariants and regression tests
artifacts/                diagnostic, frozen and supplemental machine-readable evidence
paper/                    IEEEtran manuscript, tables and bibliography
.github/workflows/        CI, publication and manuscript build/audit workflows
```

## Quick start

```bash
python -m pip install -e .[all]
make test
make repo-audit
```

Useful native targets include:

```bash
make test
make pilot
make experiments
make gate
make verdict
make figures
make tables
make paper-results
make research-smoke
make submission-artifacts
make repo-audit
make paper
make submission-check
```

See the `Makefile` before launching a full publication run; final and supplemental Monte-Carlo jobs are intentionally more expensive than smoke tests.

## Reproduce and audit the paper

1. Checkout the frozen baseline when verifying historical primary evidence:

```bash
git checkout 3904c4c2a69c4af96751d64614f7228ddea24b56
```

2. Install the full research/paper dependency set and run tests:

```bash
python -m pip install -e .[all]
pytest -q
```

3. For the current audited repository state, run:

```bash
make submission-artifacts
make repo-audit
make submission-check
```

4. Inspect the frozen primary sources:

```text
configs/paper_protocol_v2_1.json
artifacts/publication/v2_1/FINAL_RESULTS.json
artifacts/publication/v2_1/PROVENANCE.json
```

5. For reviewer-grade supplemental results, use the versioned supplemental scripts/workflows rather than silently replacing frozen primary evidence.

6. Build the manuscript from `paper/manuscript_v2_1.tex`. CI uses `latexmk` and fails on unresolved citations/references and multiply-defined labels.

Audit and reproducibility documents:

- [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md)
- [`docs/EVIDENCE_MAP.md`](docs/EVIDENCE_MAP.md)
- [`docs/EQUATION_TO_CODE_AUDIT.md`](docs/EQUATION_TO_CODE_AUDIT.md)
- [`paper/SOURCE_TO_CLAIM_TRACEABILITY.md`](paper/SOURCE_TO_CLAIM_TRACEABILITY.md)
- [`paper/CLAIM_AUDIT.md`](paper/CLAIM_AUDIT.md)
- [`paper/REVIEWER_DEFENSE.md`](paper/REVIEWER_DEFENSE.md)

## Scientific claim boundaries

This repository supports a **model-based Monte-Carlo and analytical study**, not a new RF hardware measurement campaign.

Every reported quantity should be classified as one of:

1. literature/source-derived parameter;
2. analytically derived quantity;
3. controlled simulation input;
4. simulation output;
5. statistical derivation;
6. host runtime measurement;
7. hardware measurement, only where explicitly sourced as such.

Do not describe simulation output as measured automotive-link performance. Do not describe the high-draw Monte-Carlo comparator as physical ground truth. Do not interpret the normalized resource cost as joules. Do not claim global Pareto optimality from the realized empirical partition. Do not claim embedded real-time operation from host/Python timing.

## Submission-readiness rule

The repository may be called submission-ready only after the complete test suite, repository-wide scientific consistency audit, publication smoke gate, evidence/provenance checks, bibliography audit, IEEE LaTeX build, unresolved-reference audit, and final PDF inspection all pass. If any mandatory gate is incomplete, the repository status remains **NOT YET SUBMISSION READY**.
