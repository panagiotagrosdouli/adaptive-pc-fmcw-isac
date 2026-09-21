# System Model

We study a phase-coded FMCW integrated sensing-and-communication transmitter in a high-mobility vehicular setting. The **same transmitted PC-FMCW waveform** supports two physically distinct receive paths:

1. a **monostatic sensing echo**, with two-way delay and two-way Doppler; and
2. a **one-way communication link** to a remote vehicle, with one-way propagation/Doppler and a receiver that removes the known FMCW chirp before decoding the phase code.

This separation avoids treating a radar echo and a V2V communication link as if they were the same channel.

For chirp index m and fast time t, the idealized transmitted waveform is

s_m(t) = sqrt(P_m) exp(j[pi mu t^2 + phi_m(t)]),

where mu=B/Tc is the FMCW slope and phi_m(t) is the phase-coded communication sequence. Multiple phase-code chips may be transmitted during one chirp.

## Sensing path

For a target at range R and radial velocity v,

- tau_r = 2R/c,
- f_D,r = 2 v f_c/c.

The practical automotive ADC samples the dechirped IF signal, not the RF sweep. For this reason the publication-validation path uses an analytical IF model sampled at the documented ADC rate. With the sign convention used in `if_model.py`,

f_b = mu tau_r + f_D,r.

Slow-time Doppler phase advances according to the chirp repetition interval T_r. The range estimate removes the estimated Doppler contribution from the fast-time beat frequency before converting to delay.

## Communication path

The remote receiver observes a one-way link with

- tau_c = R/c,
- f_D,c = v f_c/c.

A synchronized communication receiver removes the known FMCW chirp, leaving the phase-code sequence at baseband. Stage 7 uses a transparent multi-chip DBPSK reference modem. Its AWGN BER is validated against the standard DBPSK expression P_b = 0.5 exp(-Eb/N0). Residual frequency error after synchronization is treated explicitly in robustness sweeps.

The communication modem is a reference implementation, not a measured automotive communications standard.

## Literature-grounded profile

The primary validation profile is based on a published TI 77-GHz automated-parking chirp example: 858 MHz valid sweep bandwidth, 25.6 us chirp time, 115.8 us chirp repetition, 10 MSPS ADC rate, 256 samples/chirp and 64 chirps/frame. Device values such as 12 dBm TX power, receiver noise figure and phase-noise specification are retained as provenance metadata rather than silently converted into unsupported stochastic models.

## Adaptive PHY problem

The adaptation layer observes imperfect estimates of communication/sensing state and chooses a finite PHY action. The proposed policy minimizes resource cost subject to a target probability that communication reliability and sensing accuracy constraints are met. Controlled uncertainty, residual synchronization error and mutual interference are evaluated separately from literature-grounded hardware constants.

## Scope boundary

This repository studies waveform/PHY/link adaptation. It does not perform trajectory forecasting, packet/user scheduling, beam selection, ADB control or ego-motion planning.
