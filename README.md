# Physics-Gated Reliability-Constrained Adaptive PC-FMCW ISAC

A reproducible, dataset-free research framework for **high-mobility vehicular phase-coded FMCW integrated sensing and communication (PC-FMCW ISAC)**.

> **Research question:** Which PC-FMCW PHY configuration is physically feasible, and which feasible configuration should be selected when communication reliability and radar sensing quality must be maintained simultaneously under mobility and imperfect PHY knowledge?

The central idea is **physics-gated robust adaptation**. A candidate waveform/profile is first rejected if its FMCW sampling, range or unambiguous-velocity limits cannot support the operating state. The remaining configurations are then evaluated under joint communication and sensing QoS constraints with uncertainty in SNR, Doppler, interference and synchronization.

## Scientific positioning

This work builds on the established PC-FMCW ISAC concept but addresses a different research layer. Prior PC-FMCW laser-headlamp ISCAI work demonstrated that phase-coded FMCW can integrate communication, sensing and illumination, including DPSK communication, range-Doppler sensing, ADB illumination and target tracking.

**This repository does not claim those concepts as new.** Its contribution is to move from fixed-configuration functional feasibility to **reliable adaptive operation under high-mobility PHY uncertainty**.

The project studies an **RF/mmWave 77-GHz vehicular PC-FMCW ISAC PHY**, not an optical laser-headlamp/ADB system. It deliberately excludes trajectory forecasting, ego-motion planning, packet/user scheduling, beam management, ADB illumination and Hough tracking as proposed contributions.

The intended one-sentence contribution is:

> **We extend PC-FMCW ISAC from fixed-configuration functional feasibility to physics-gated, reliability-constrained PHY adaptation under high-mobility uncertainty, and characterize the operating region in which vehicular communication and sensing QoS can be jointly guaranteed.**

See [`docs/CONTRIBUTION_POSITIONING.md`](docs/CONTRIBUTION_POSITIONING.md) for the detailed novelty boundary, hypotheses, baselines and claim hierarchy.

## Working paper title

**Physics-Gated Reliability-Constrained Adaptive Phase-Coded FMCW ISAC for High-Mobility Vehicular Links**

## Proposed contributions

1. **Physics-gated PC-FMCW adaptation** — reject configurations that violate FMCW sampling, range or unambiguous-velocity limits before optimization.
2. **Joint reliability under imperfect PHY knowledge** — communication and sensing chance/reliability constraints under SNR, Doppler, interference, synchronization and state-estimation uncertainty.
3. **Feasible operating-region characterization** — determine where joint sensing/communication QoS is achievable and where no candidate configuration can satisfy it.
4. **Communication–sensing–resource Pareto analysis** — quantify the cost required to remain reliable rather than reporting only average gains.
5. **Reproducible high-mobility evaluation** — explicitly separate one-way vehicular communications from the monostatic two-way sensing echo and preserve provenance for every parameter/result class.

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

### Short-range profile

The parking-oriented reference uses 77 GHz carrier, 858 MHz valid sweep, 25.6 us active chirp, 115.8 us chirp repetition interval, 10 MSPS IF ADC, 256 samples/chirp and 64 chirps/frame.

Its current analytical scales are approximately:

- range resolution: **0.175 m**;
- positive-IF range support: **22.36 m**;
- radial-velocity resolution: **0.263 m/s**;
- maximum unambiguous radial velocity: **8.41 m/s**.

This is an important physical example: excellent range resolution does **not** imply suitability for high relative velocity.

### High-mobility capability profile

The high-mobility capability reference uses 77 GHz, 1 GHz sweep, 20 us active chirp/repetition, 37.5 MSPS ADC capability, 750 samples/chirp and 128 chirps/frame.

Its current analytical scales are approximately:

- range resolution: **0.150 m**;
- positive-IF range support: **56.21 m**;
- radial-velocity resolution: **0.760 m/s**;
- maximum unambiguous radial velocity: **48.67 m/s**.

This is a **composite capability reference**, not a claim that a commercial radar ships with this exact preset. Parameter provenance and claim boundaries are documented in `docs/LITERATURE_GROUNDED_PARAMETERS.md`.

## Correct FMCW signal path

The radar ADC samples the **dechirped IF/beat signal**, not the 77-GHz carrier or the full RF sweep directly. The sensing simulator therefore uses an IF-domain FMCW model with explicit fast-time range and slow-time Doppler structure.

The communication path is a separate one-way vehicular link. The receiver removes the known chirp component and recovers embedded phase-coded data. This prevents the one-way communications link budget from being conflated with the monostatic two-way radar echo.

## Communication validation

The current reference modem uses multi-chip DBPSK after chirp removal. With 32 chips/chirp in the short-range profile, the raw reference rate is approximately **276.3 kb/s**.

The implementation is checked against the analytical noncoherent DBPSK AWGN result. The committed diagnostic Monte-Carlo artifact includes:

| Eb/N0 | simulated BER | analytical BER |
|---:|---:|---:|
| 0 dB | 1.836e-1 | 1.839e-1 |
| 4 dB | 4.106e-2 | 4.056e-2 |
| 8 dB | 9.20e-4 | 9.09e-4 |
| 10 dB | 2.00e-5 | 2.27e-5 |

Residual frequency error is treated explicitly as a high-mobility impairment. At 8 dB Eb/N0, the diagnostic uncompensated BER rises from roughly **9e-4 at 0 Hz residual error** to roughly **3.2e-2 around 5.1 kHz**. These are simulation outputs, not measured RF results.

See `artifacts/stage7/pilot_validation.json`.

## Proposed controller and baselines

- **B0 — Fixed PHY:** one frozen configuration for every operating state.
- **B1 — Communication-only adaptive:** minimizes resource cost subject to communication QoS.
- **B2 — Sensing-only adaptive:** minimizes resource cost subject to sensing QoS.
- **B3 — Deterministic joint ISAC:** satisfies both QoS constraints while treating the estimated state as exact.
- **B4 — Robust joint ISAC (proposed):** physics gate + uncertainty-aware joint reliability constraints.
- **Oracle:** true instantaneous state; non-deployable evaluation bound only.

A representative formulation is

```text
minimize_a     C_resource(a)

subject to     a in A_physics(state)
               P[BER(a,S) <= epsilon_comm] >= 1 - alpha
               P[RMSE_range(a,S) <= delta_r] >= 1 - beta_r
               P[RMSE_velocity(a,S) <= delta_v] >= 1 - beta_v
               P[joint QoS(a,S)] >= 1 - eta
               R_eff(a,S) >= R_min, when required.
```

## Main evaluation outputs

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
docs/                    system model, contribution positioning, provenance and protocol
src/pcfmcw_isac/         waveform, channel, link-budget, sensing and policy code
scripts/                 reproducible validation and experiment entry points
tests/                   physical invariants and regression tests
artifacts/                machine-readable diagnostic and final results
```

## Quick start

```bash
python -m pip install -e .[dev]
pytest -q

python scripts/run_experiment.py \
  --config configs/baseline.json \
  --output artifacts/baseline.json

python scripts/run_stage7_validation.py \
  --output artifacts/stage7/literature_validation.json
```

## Scientific claim boundaries

This repository currently supports a **model-based Monte-Carlo study**, not a new RF hardware measurement campaign.

Every reported quantity should be classified as one of:

1. **source-derived parameter**;
2. **analytically derived quantity**;
3. **controlled simulation variable**;
4. **simulation output**;
5. **external measured value**.

No simulation output is described as a measured automotive-link result. No measurement from another waveform/platform is presented as experimental validation of PC-FMCW.

## Publication gate

The work is paper-ready only after waveform/receiver and physical-feasibility validation, frozen parameter/QoS ranges, common-support B0-B4 evaluation, large independent Monte-Carlo runs, paired confidence intervals/statistical tests, uncertainty/interference/synchronization ablations, feasibility and Pareto maps, runtime measurement and an immutable tagged reproduction bundle.

Until then, committed pilot results remain **diagnostic simulation evidence**, not final paper claims.
