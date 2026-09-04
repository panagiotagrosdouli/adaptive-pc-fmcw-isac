# Robust Reliability-Constrained Adaptive PC-FMCW ISAC

Dataset-free, reproducible research framework for **joint sensing-and-communication PHY adaptation** in high-mobility vehicular phase-coded FMCW (PC-FMCW) systems.

## Research question

Can a PC-FMCW transceiver adapt its physical-layer configuration online so that communication reliability and sensing accuracy are jointly satisfied under uncertain SNR, Doppler, interference, synchronization error and phase noise, while minimizing resource cost?

## Scientific contribution

This repository is intentionally focused on the **physical/link layer**. It does not perform trajectory planning, packet/user scheduling, beam management, ADB control, or dataset-driven trajectory forecasting.

The proposed method solves a discrete robust configuration problem over a PC-FMCW configuration set. A configuration may vary transmit power, phase-code length, chirp/repetition budget and coding/repetition level. Selection is based on imperfect state estimates and reliability constraints for both communication and sensing.

Core outputs are:

1. communication reliability: BER, PER, outage and effective rate;
2. sensing quality: range/velocity error proxies and detection quality;
3. resource cost: power/chirp/code/repetition cost;
4. joint feasibility: probability that communication and sensing QoS are simultaneously satisfied;
5. operating-region maps and communication-sensing-resource Pareto frontiers.

## Baselines

- **B0 Fixed PHY** — one conservative configuration for all states.
- **B1 Communication-only adaptive** — minimizes cost subject to communication QoS.
- **B2 Sensing-only adaptive** — minimizes cost subject to sensing QoS.
- **B3 Joint deterministic ISAC** — joint constraints evaluated at the estimated state.
- **B4 Robust joint ISAC (proposed)** — joint chance/reliability constraints under state uncertainty.
- **Oracle** — same joint objective with perfect instantaneous state; evaluation bound only.

## Controlled operating regimes

The project is dataset-free. Experiments are generated from declared simulation distributions and fixed seeds. Planned sweeps cover SNR, relative velocity/Doppler, interference, CFO/synchronization error, phase noise, state-estimation uncertainty and QoS targets.

## Repository layout

```text
configs/                 frozen experiment configurations
docs/                    scientific protocol and paper plan
src/pcfmcw_isac/         waveform/link/sensing models and policies
scripts/                 reproducible experiment entry points
tests/                   scientific invariants and regression tests
artifacts/                generated machine-readable results (not hand edited)
```

## Quick start

```bash
python -m pip install -e .[dev]
pytest -q
python scripts/run_experiment.py --config configs/baseline.json --output artifacts/baseline.json
```

## Claim boundaries

This is a **model-based Monte-Carlo study**, not measured optical/radar hardware validation. Results must be reported as simulated/model-based PC-FMCW ISAC performance. The initial model is deliberately auditable and modular; waveform-level and receiver-level refinements must be validated before stronger physical claims are made.

## Publication gate

A paper result is frozen only after: model validation, baseline parity checks, predeclared sweeps, independent Monte-Carlo seeds, uncertainty calibration checks, paired statistical analysis, sensitivity/ablation studies, feasibility maps, Pareto analysis, runtime reporting and a tagged reproduction bundle.
