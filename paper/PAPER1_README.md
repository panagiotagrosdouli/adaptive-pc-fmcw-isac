# Paper 1 — Physics-Aware PC-FMCW Configuration Selection

## Standalone identity

**Title:** Physics-Aware Configuration Selection for Phase-Coded FMCW Integrated Sensing and Communication in High-Mobility Vehicular Links

**Scientific question:** Before robust reliability optimization, can a candidate PC-FMCW PHY configuration physically represent the requested vehicular range and radial velocity?

This paper is intentionally separate from the later finite-sample reliability/abstention paper. It focuses on waveform/profile physics, configuration capability, and the need for deterministic physical gating.

## Evidence boundary

The manuscript uses three evidence classes:

1. **Source-grounded profile parameters** — 77-GHz parking-profile values derived from Texas Instruments reference-design documentation.
2. **Analytical derived quantities** — range resolution, positive-IF range support, velocity resolution, and monostatic unambiguous radial velocity calculated from those parameters.
3. **Pilot simulation evidence** — sensing RMSE and DBPSK BER results from `artifacts/stage7/pilot_validation.json`.

The pilot artifact explicitly states that these are simulation outputs, not RF measurements, and not the frozen large-seed paper run.

## Core numerical anchors

| Quantity | Parking profile | High-mobility capability profile |
|---|---:|---:|
| Carrier | 77 GHz | 77 GHz |
| Bandwidth | 858 MHz | 1 GHz |
| Chirp / repetition | 25.6 / 115.8 us | 20 / 20 us |
| IF sampling | 10 MSPS | 37.5 MSPS |
| Range resolution | 0.1747 m | 0.1499 m |
| Positive-IF range | 22.362 m | 56.211 m |
| Velocity resolution | 0.2627 m/s | 0.7604 m/s |
| Unambiguous velocity | 8.405 m/s | 48.668 m/s |

The high-mobility profile is a composite capability reference and is not presented as a commercial preset.

## Pilot evidence used in Paper 1

- Parking target: `(R,v)=(10 m,3 m/s)`, 50 trials/SNR point.
- At -30 dB IF SNR: range RMSE 7.4197 m; velocity RMSE 5.1280 m/s.
- At -25 dB: range RMSE 0.02142 m; velocity RMSE 0.03511 m/s.
- At -20 dB: range RMSE 0.01151 m; velocity RMSE 0.03011 m/s.
- Communication reference: 32 chips/chirp, 300,000 bits per Eb/N0 point.
- At 0 dB Eb/N0: simulated DBPSK BER 0.183633 vs. 0.183940 theory.
- At 8 dB: 0.000920 vs. 0.000909 theory.

These values are quoted only with their simulation/evidence boundary.

## Reproduction

From the repository root, the Paper 1 source is:

```text
paper/paper1_ieee.tex
paper/paper1_figures.tex
paper/paper1_references.bib
```

The manuscript is designed for IEEEtran and has its own bibliography. The Paper 2 manuscript and v2.1 submission package remain separate.

## External literature used

The paper's literature basis includes the original PC-FMCW experimental work, receiver and waveform studies, vehicular ISAC literature, broad ISAC surveys, robust V2X/ISAC work, and the Texas Instruments 77-GHz reference design. The bibliography is kept local to Paper 1 so its citation set can evolve independently.
