# Literature-grounded parameter profile

This stage replaces arbitrary default values with a traceable automotive-radar profile. It is important to distinguish **literature-grounded hardware/profile values** from **controlled simulation variables** and from **measured values produced by this repository**. The repository contains no new RF measurement campaign.

## Grounded hardware and chirp profile

The primary chirp profile follows the Texas Instruments automated-parking 77-GHz reference-design example: 10 MSPS ADC sampling, 858 MHz valid sweep bandwidth, 25.6 us chirp time, 115.8 us chirp repetition time, 256 ADC samples/chirp, 64 chirps/frame and 50 ms frame duration. The carrier is set to 77 GHz within the 76-81 GHz automotive band.

Device-level values are taken from the TI AWR1642 hardware documentation: 12 dBm transmit power, approximately 14 dB receiver noise figure in the 76-77 GHz part of the band, and phase-noise specification around -95 dBc/Hz at 1 MHz offset. These device specifications are recorded for provenance; they are **not** silently converted into an equivalent random-walk phase-noise variance because such a conversion requires an oscillator/noise-shaping model.

PC-FMCW is motivated and architecturally grounded by the experimental and interference literature of Kumbul et al. (EuCAP 2021; IEEE JC&S 2024). The number of communication phase-code chips per chirp remains a design variable in this repository and is not claimed to be a TI modem parameter.

## Why the implementation uses an IF-domain analytical model

A 10 MSPS automotive ADC samples the **dechirped IF/beat signal**, not the original 858-MHz FMCW transmit sweep. Directly generating an 858-MHz complex-baseband chirp at 10 MSPS would violate the sampling model. Stage 7 therefore adds an analytical FMCW IF generator: range and Doppler are inserted through the delay and Doppler equations, and only the dechirped beat signal is sampled at the documented ADC rate.

For a monostatic target,

- tau = 2R/c,
- f_D = 2 v f_c / c,
- f_b = mu tau + f_D,
- mu = B/T_c.

The slow-time Doppler phase advances with the chirp repetition interval T_r, not merely the active chirp duration T_c. This distinction is required for a physically meaningful unambiguous-velocity calculation.

## Derived values for the 858-MHz / 77-GHz profile

The simulator computes, rather than hard-codes, the following quantities:

- range resolution: c/(2B), about 0.175 m,
- positive-IF maximum range at 10 MSPS: c Fs/(4 mu), about 22.4 m,
- Doppler velocity resolution: lambda/(2 N T_r), about 0.263 m/s,
- maximum unambiguous radial velocity: lambda/(4 T_r), about 8.4 m/s.

These limits are properties of the selected short-range parking-style chirp profile. They are not universal limits of 77-GHz automotive radar.

## Controlled variables, not claimed measurements

SNR, residual CFO/frequency error, INR, synchronization error, RCS, antenna gain, blockage loss and stochastic phase-noise strength remain controlled experimental variables unless a later stage supplies a traceable measured or standard-derived model. Plots and tables must label them accordingly.

## Sources

1. Texas Instruments, *Automated Parking System Reference Design Using 77-GHz mmWave Sensor*, TIDUEO9, chirp-profile table.
2. Texas Instruments, *AWR1642 Single-Chip 77 and 79 GHz FMCW Radar Sensor* product/datasheet documentation.
3. U. Kumbul et al., *Experimental Investigation of Phase Coded FMCW for Sensing and Communications*, EuCAP 2021, DOI 10.23919/EuCAP51087.2021.9411464.
4. U. Kumbul et al., *Automotive Radar Interference Mitigation using Phase-Coded FMCW Waveform*, IEEE JC&S 2024, DOI 10.1109/JCS61227.2024.10646233.
