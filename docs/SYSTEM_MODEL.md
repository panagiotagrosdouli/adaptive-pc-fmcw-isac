# System Model

We study a phase-coded FMCW integrated sensing-and-communication transmitter/receiver in a high-mobility vehicular setting. The simulator operates at complex baseband. Carrier-dependent Doppler is injected analytically; RF/optical carrier sampling is not attempted.

For chirp index m and fast time t, the normalized transmitted signal is

s_m(t) = sqrt(P_m) exp(j[pi mu t^2 + phi_m]),

where mu=B/Tc is the FMCW slope and phi_m is the phase-coded communication symbol. Differential BPSK is initially used because it provides a transparent reference chain. Extensions must preserve a documented receiver and validation reference.

The received waveform includes delay, Doppler, residual CFO, phase noise, additive noise and optional mutual interference. The same received signal is consumed by a communication receiver and a dechirp/range-Doppler sensing receiver.

The estimated state is imperfect. Adaptation observes estimated SNR/Doppler/CFO/interference descriptors and chooses a finite PHY action. The proposed policy solves a reliability-constrained finite-action problem: minimize resource cost subject to a minimum probability that BER, effective rate, range error and velocity error satisfy their targets.

The main scientific separation is deliberate: this repository studies PHY/link adaptation only. It does not perform trajectory forecasting, packet/user scheduling, beam selection, ADB control or ego-motion planning.
