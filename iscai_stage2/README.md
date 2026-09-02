# ISCAI Stage 2

Stage 2 owns the PC-FMCW-like observation and measurement-uncertainty
pipeline.

## Upstream dependency

Stage 1 is frozen and remains the source of:

- causal WOMD actor histories,
- ego/headlamp frames,
- receiver/actor geometry,
- Stage-1 contracts.

Stage 2 imports those through:

- iscai_stage1.actors
- iscai_stage1.geometry
- iscai_stage1.contracts

Stage 2 owns:

- iscai_stage2.observations
- iscai_stage2.pc_fmcw

Stage 2 must not modify Stage-1 causal semantics.

## Observation semantics

WOMD/WOMD-LiDAR is not measured FMCW.

The Stage-2 main mode is:

real causal traffic
-> geometry-derived ideal observables
-> synthetic PC-FMCW-like measurement model
-> SNR/CRLB covariance
-> noise / missed detections / false alarms

Measurement covariance is distinct from predictive uncertainty.

## Clean-versus-degraded experimental protocol

- Use identical scenario/actor/time splits for both conditions.
- The clean condition keeps the ideal causal measurement mean and its declared
  covariance, without sampled sensor noise, misses, or false alarms.
- The degraded condition is derived from that exact clean record with fixed,
  reported seeds; truth association is stored only in evaluator sidecars.
- Range noise uses an explicitly lower-truncated Gaussian at the physical
  zero-range boundary. Boundary-affected samples must be reported separately.
- Fixed-SNR, detection, false-alarm, and angular-error parameters are declared
  experimental assumptions, not measurements from WOMD or results from Part A.
- CRLB values are lower bounds used to parameterize a synthetic observation
  model; they are not claimed as achieved estimator errors.

The optional full waveform/RDM/CFAR path is not required for the
core Stage-2 pipeline.
