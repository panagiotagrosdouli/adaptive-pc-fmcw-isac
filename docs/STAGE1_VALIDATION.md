# Stage 1 — Waveform and Receiver Validation

## Purpose

Stage 1 replaces paper-facing reliance on the initial surrogate PHY with a reproducible waveform-level validation layer. No Stage-1 result is a measured-hardware claim.

## System boundary

The validation chain is

`bits -> differential phase symbols -> phase-coded FMCW chirps -> controlled channel/impairments -> dechirp/decoding -> communication + sensing metrics`.

This stage does not contain WOMD, trajectory forecasting, packet scheduling, beam selection, ADB, or ego-motion planning.

## Frozen validation questions

1. Does the noiseless communication chain recover the transmitted information exactly?
2. Does BER decrease monotonically with Eb/N0 in the AWGN reference experiment and approach the selected analytical differential-detection reference under matched assumptions?
3. Does a single ideal target produce the expected beat-frequency/range peak within FFT resolution?
4. Does coherent slow-time processing recover signed Doppler within the unambiguous region?
5. Are delay and Doppler errors separated from CFO and phase-noise impairments in the API and experiments?
6. Do phase-code length, code rate/repetition, chirp budget and transmit resource have explicit accounting rather than hidden gains?

## Stage-1 model

For chirp index m and fast-time t, the complex-baseband transmit signal is represented as

`s_m(t) = sqrt(P_m) exp(j[2 pi (f0 t + 0.5 mu t^2) + phi_m])`,

where `mu = B/Tc` and `phi_m` carries the phase-coded communication symbol. The first implementation uses a normalized complex-baseband representation; carrier-frequency-dependent Doppler is applied explicitly in the channel rather than numerically sampling the RF carrier.

A single-target reference channel applies delay `tau = 2R/c`, Doppler `fd`, complex gain, AWGN, and optional CFO/phase perturbations. Multi-target and mutual-interference extensions are later stages and must not be silently mixed into the Stage-1 reference curves.

## Communication reference

The first communication reference uses binary differential phase coding across chirps. The receiver forms differential products between adjacent decoded chirp phases. AWGN-only BER curves are compared against an analytical reference only when normalization, differential detector, and Eb/N0 definition match. A mismatch is reported rather than tuned away.

## Sensing reference

Range is estimated from dechirped fast-time beat frequency. Doppler is estimated from coherent slow-time phase evolution after range-bin selection. Report bin resolution, unambiguous interval, absolute error, and RMSE. Do not claim super-resolution from FFT-bin estimates.

## Required tests before Stage 1 closes

- waveform dimensions and unit-energy/resource accounting;
- deterministic seed reproducibility;
- noiseless differential communication recovery;
- AWGN BER ordering across at least three Eb/N0 values;
- zero-delay/zero-Doppler sanity case;
- known-delay range-bin recovery;
- positive and negative Doppler recovery;
- CFO changes communication/sensing outputs when enabled;
- phase noise changes outputs when enabled;
- invalid configurations fail loudly;
- no test depends on an external dataset.

## Closure gate

Stage 1 can be marked `VALIDATED_SIMULATION` only after all required tests pass and archived validation tables contain configuration, random seeds, assumptions and software commit. This label means validated simulation under declared assumptions, not experimental hardware validation.
