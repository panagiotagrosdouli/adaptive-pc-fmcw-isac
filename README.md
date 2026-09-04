# Physics-Gated Reliability-Constrained Adaptive PC-FMCW ISAC

A reproducible, dataset-free research framework for **high-mobility vehicular phase-coded FMCW integrated sensing and communication (PC-FMCW ISAC)**.

The project studies a question that appears before higher-layer scheduling, planning or beam control:
![Uploading image.png…]()

> **Which PC-FMCW PHY configuration is physically feasible, and which feasible configuration should be selected when communication reliability and radar sensing quality must be maintained simultaneously under mobility and imperfect PHY knowledge?**

The central idea is **physics-gated robust adaptation**. A candidate waveform/profile is first rejected if its FMCW sampling, range or unambiguous-velocity limits cannot support the current operating state. The remaining configurations are then evaluated under communication and sensing QoS constraints with uncertainty in SNR, Doppler, interference and synchronization.

## Paper direction

**Working title:** *Physics-Gated Reliability-Constrained Adaptive Phase-Coded FMCW ISAC for High-Mobility Vehicular Links*

The intended contribution is not generic waveform adaptation. The paper combines:

1. **PC-FMCW physical feasibility** — bandwidth, chirp duration, IF sampling, range support, range resolution and unambiguous velocity;
2. **vehicular communications** — phase-coded / multi-chip DBPSK transmission, BER, effective rate and outage;
3. **radar sensing** — dechirped IF processing, range and radial-velocity estimation;
4. **high-mobility impairments** — Doppler, residual frequency/synchronization error, phase noise and interference;
5. **imperfect PHY-state knowledge** — estimated rather than oracle channel/impairment state;
6. **reliability-constrained adaptation** — joint communication/sensing QoS with robust or chance-constrained selection;
7. **feasible operating regions** — maps showing where joint sensing and communication requirements can and cannot be satisfied;
8. **resource trade-offs** — power, chirp/code/repetition cost and communication-sensing-resource Pareto frontiers.

This repository deliberately excludes trajectory forecasting, ego-motion planning, packet/user scheduling, beam management and adaptive-driving-beam control. The scientific identity is the **PC-FMCW physical/link layer**.

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
                    feasible profiles only
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

A configuration can include waveform/profile choice, transmit power, phase-code/chip budget and repetition/coding resources. The action space is finite and reproducible so that all baselines are evaluated on the same candidate set.

## Literature-grounded 77-GHz profiles

The current physical validation path uses traceable automotive 77-GHz scales rather than arbitrary parameter ranges.

### Short-range profile

The parking-oriented reference uses:

- carrier: **77 GHz**;
- valid FMCW sweep: **858 MHz**;
- active chirp: **25.6 us**;
- chirp repetition interval: **115.8 us**;
- IF ADC: **10 MSPS**;
- samples/chirp: **256**;
- chirps/frame: **64**.

The resulting analytical scales are approximately:

- range resolution: **0.175 m**;
- positive-IF range support: **22.36 m**;
- radial-velocity resolution: **0.263 m/s**;
- maximum unambiguous radial velocity: **8.41 m/s**.

This profile demonstrates an important design point: excellent short-range resolution does **not** imply suitability for high relative velocity.

### High-mobility capability profile

A second capability profile uses:

- carrier: **77 GHz**;
- sweep: **1 GHz**;
- active chirp / repetition: **20 us**;
- ADC capability: **37.5 MSPS**;
- samples/chirp: **750**;
- chirps/frame: **128**.

Its current analytical scales are approximately:

- range resolution: **0.150 m**;
- positive-IF range support: **56.21 m**;
- radial-velocity resolution: **0.760 m/s**;
- maximum unambiguous radial velocity: **48.67 m/s**.

This is a **composite capability reference**, not a claim that a commercial radar ships with this exact preset.

A published 77-GHz vehicular channel example at **20.28 m** and **5.1 kHz one-way Doppler** is retained only as an external channel-scale cross-check. Its source waveform is not used as evidence that the proposed PC-FMCW waveform has been experimentally validated.

See `docs/LITERATURE_GROUNDED_PARAMETERS.md` for provenance and claim boundaries.

## Correct FMCW signal path

The sensing ADC does not sample the 77-GHz carrier or the full 858-MHz/1-GHz RF sweep directly. The radar receiver mixes the delayed echo with the local chirp and samples the resulting **dechirped IF/beat signal**. The sensing simulator follows this IF-domain model and explicitly separates fast-time range information from slow-time Doppler information.

The communications path is a separate one-way vehicular link. The receiver removes the known chirp component and recovers the embedded phase-coded data. This avoids conflating the monostatic two-way radar equation with the one-way communications link budget.

## Communication validation

The current reference modem uses multi-chip DBPSK after chirp removal. With 32 chips/chirp in the short-range profile, the raw reference rate is approximately **276.3 kb/s**.

The implementation is checked against the analytical noncoherent DBPSK AWGN result. The committed diagnostic Monte-Carlo artifact gives, for example:

| Eb/N0 | simulated BER | analytical BER |
|---:|---:|---:|
| 0 dB | 1.836e-1 | 1.839e-1 |
| 4 dB | 4.106e-2 | 4.056e-2 |
| 8 dB | 9.20e-4 | 9.09e-4 |
| 10 dB | 2.00e-5 | 2.27e-5 |

Residual frequency error is then treated as a genuine high-mobility impairment rather than hidden inside an SNR penalty. At 8 dB Eb/N0, the diagnostic uncompensated BER rises from roughly **9e-4 at 0 Hz residual error** to roughly **3.2e-2 around 5.1 kHz**. This motivates explicit synchronization/Doppler compensation and uncertainty-aware adaptation.

These values are **simulation outputs**, not measured RF results. See `artifacts/stage7/pilot_validation.json`.

## Sensing validation

The sensing chain uses the dechirped IF-domain FMCW model and estimates range and radial velocity from the fast-time/slow-time structure. Diagnostic Monte-Carlo sweeps verify that the receiver approaches the expected resolution region as SNR increases and fails gracefully below the useful detection regime.

The short-range and high-mobility profiles are evaluated separately because their range and velocity feasibility regions are physically different. A controller is not allowed to select a profile that is incapable of representing the requested target range/velocity before noise or optimization is even considered.

## Proposed controller and baselines

- **B0 — Fixed PHY:** one static configuration for every operating state.
- **B1 — Communication-only adaptive:** minimizes resource cost subject to communication QoS.
- **B2 — Sensing-only adaptive:** minimizes resource cost subject to sensing QoS.
- **B3 — Deterministic joint ISAC:** satisfies both QoS constraints while treating the estimated state as exact.
- **B4 — Robust joint ISAC (proposed):** satisfies joint reliability/chance constraints under PHY-state uncertainty after physics gating.
- **Oracle:** uses the true instantaneous state and is reported only as a non-deployable reference bound.

A generic robust formulation is

```text
minimize_a     C_resource(a)

subject to     P[ BER(a,S) <= epsilon_comm ] >= 1 - alpha
               P[ RMSE_range(a,S) <= delta_r ] >= 1 - beta_r
               P[ RMSE_velocity(a,S) <= delta_v ] >= 1 - beta_v
               R_eff(a,S) >= R_min
               a is physically feasible for the operating state.
```

The random state `S` captures uncertainty in quantities such as SNR, Doppler/residual frequency, interference and other declared PHY impairments.

## Main evaluation axes

The publication protocol is designed around more than average BER or RMSE. The main outputs are:

- BER / PER / effective rate / outage;
- range and radial-velocity RMSE;
- probability of joint QoS satisfaction;
- reliability-constraint violation rate;
- selected PHY resource cost;
- profile-selection frequency;
- infeasible-state probability;
- SNR x velocity and interference x synchronization-error feasibility maps;
- sensing-communication-resource Pareto frontiers;
- robustness to state-estimation error and model mismatch;
- runtime / decision complexity.

## Experimental protocol

The planned frozen study contains twelve blocks:

- **E1:** analytical and waveform/receiver sanity checks;
- **E2:** communication BER validation;
- **E3:** FMCW range/velocity validation;
- **E4:** high-mobility Doppler and synchronization stress;
- **E5:** interference and phase-noise stress;
- **E6:** B0-B4 + Oracle comparison;
- **E7:** imperfect-state / uncertainty sweep;
- **E8:** reliability-target sweep;
- **E9:** physical feasibility-region mapping;
- **E10:** communication-sensing-resource Pareto analysis;
- **E11:** ablations and model mismatch;
- **E12:** large-seed paired statistics, runtime and frozen reproduction bundle.

Final comparisons use fixed independent seeds, paired evaluation where appropriate, bootstrap confidence intervals and predeclared configurations. Pilot runs are diagnostic and are not silently promoted to publication results.

## Repository layout

```text
configs/                 frozen and literature-grounded experiment configurations
docs/                    system model, parameter provenance, protocol and paper plan
src/pcfmcw_isac/         waveform, channel, link-budget, sensing and policy code
scripts/                 reproducible validation and experiment entry points
tests/                   physical invariants and regression tests
artifacts/                machine-readable diagnostic and final results
```

## Quick start

```bash
python -m pip install -e .[dev]
pytest -q

# Baseline/system-level experiment
python scripts/run_experiment.py \
  --config configs/baseline.json \
  --output artifacts/baseline.json

# Literature-grounded PHY validation
python scripts/run_stage7_validation.py \
  --output artifacts/stage7/literature_validation.json
```

## Scientific claim boundaries

This repository currently supports a **model-based Monte-Carlo study**. It does not contain a new RF hardware measurement campaign.

Every reported quantity should be classified as one of:

1. **source-derived parameter** — taken from a cited hardware/reference source;
2. **analytically derived quantity** — computed from declared equations and parameters;
3. **controlled simulation variable** — deliberately selected experimental condition;
4. **simulation output** — generated by the committed model and fixed seeds;
5. **external measured value** — a value reported by another experimental work and used only within its stated scope.

No simulation result should be described as a measured automotive link result. No external PMCW/other-waveform measurement should be presented as experimental validation of PC-FMCW.

## Publication gate

The work is considered paper-ready only after:

- waveform/receiver validation passes;
- physical feasibility checks pass;
- B0-B4 use the same action/state support;
- final parameter ranges and QoS targets are frozen before evaluation;
- large independent Monte-Carlo runs are complete;
- paired confidence intervals/statistical tests are reported;
- uncertainty, interference and synchronization ablations are complete;
- feasibility and Pareto maps are generated;
- runtime is measured;
- final artifacts are immutable and reproducible from a tagged commit.

Until then, committed Stage-7 results are explicitly **diagnostic simulation evidence**, not final paper claims.
