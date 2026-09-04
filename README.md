# Robust Reliability-Constrained Adaptive PC-FMCW ISAC

Dataset-free, reproducible research framework for **joint sensing-and-communication PHY adaptation** in high-mobility vehicular phase-coded FMCW (PC-FMCW) systems.

## Research question

Can a PC-FMCW transceiver adapt its physical-layer configuration online so that communication reliability and sensing accuracy are jointly satisfied under uncertain SNR, Doppler, interference, synchronization error and phase noise, while minimizing resource cost?

## Scientific contribution

This repository is intentionally focused on the **physical/link layer**. It does not perform trajectory planning, packet/user scheduling, beam management, ADB control, or dataset-driven trajectory forecasting.

The proposed method solves a discrete robust configuration problem over a PC-FMCW configuration set. A configuration may vary transmit power, phase-code length, chirp/repetition budget and coding/repetition level. Selection is based on imperfect state estimates and reliability constraints for both communication and sensing.

Core outputs are:

1. communication reliability: BER, PER, outage and effective rate;
2. sensing quality: range/velocity accuracy and detection quality;
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

## Literature-grounded validation profiles

Stage 7 introduces traceable automotive-radar values instead of relying only on generic defaults.

- **Short-range parking profile:** 77 GHz carrier, 858 MHz valid sweep, 25.6 us active chirp, 115.8 us chirp repetition, 10 MSPS IF ADC, 256 samples/chirp and 64 chirps/frame, based on the TI automated-parking 77-GHz reference-design example.
- **High-mobility capability profile:** 77 GHz, 1 GHz / 20 us sweep target with 37.5 MSPS ADC capability, constructed from TI high-mobility chirp guidance and AWR2944 hardware capability. It is explicitly a composite capability reference rather than a claimed commercial preset.
- **77-GHz JCRS cross-check:** a published vehicular example at 20.28 m, 5.1 kHz one-way Doppler and 15 dBsm vehicle RCS is retained as an external channel-scale benchmark. Its source waveform is PMCW-CDMA, so it is used only for channel-value cross-checking, not waveform validation.

A practical FMCW ADC samples the **dechirped IF/beat signal**. The literature-grounded sensing path therefore uses an analytical sampled-IF model rather than incorrectly sampling an 858-MHz transmit sweep at 10 MSPS.

The communication path is physically separated from the monostatic sensing echo. A remote receiver removes the known chirp and decodes a multi-chip DBPSK phase code; the AWGN BER implementation is regression-tested against the analytical DBPSK reference.

See `docs/LITERATURE_GROUNDED_PARAMETERS.md` and `artifacts/stage7/pilot_validation.json`.

## Controlled operating regimes

The project is dataset-free. Experiments are generated from declared simulation distributions and fixed seeds. Sweeps cover SNR/EbN0, relative velocity/Doppler, interference, residual CFO/synchronization error, phase noise, state-estimation uncertainty and QoS targets. Quantities without a traceable hardware/channel model remain labelled controlled simulation variables.

## Repository layout

```text
configs/                 frozen and literature-grounded experiment configurations
docs/                    scientific protocol, physical model and paper plan
src/pcfmcw_isac/         waveform/link/sensing models and policies
scripts/                 reproducible experiment entry points
tests/                   scientific invariants and regression tests
artifacts/                generated machine-readable results
```

## Quick start

```bash
python -m pip install -e .[dev]
pytest -q
python scripts/run_experiment.py --config configs/baseline.json --output artifacts/baseline.json
python scripts/run_stage7_validation.py --output artifacts/stage7/literature_validation.json
```

## Claim boundaries

This is a **model-based Monte-Carlo study**, not a new measured RF/optical hardware campaign. Literature-grounded constants are distinguished from controlled simulation variables and from measured quantities in cited external work. Pilot artifacts are not automatically publication results. Stronger claims require the frozen large-seed protocol, uncertainty/mismatch experiments and full statistical analysis.

## Publication gate

A paper result is frozen only after: model validation, baseline parity checks, predeclared sweeps, independent Monte-Carlo seeds, uncertainty calibration checks, paired statistical analysis, sensitivity/ablation studies, feasibility maps, Pareto analysis, runtime reporting and a tagged reproduction bundle.
