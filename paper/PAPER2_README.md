# Paper 2 — standalone IEEE submission

## Identity

**Working title:** Physics-Gated Reliability-Constrained Adaptive Phase-Coded FMCW ISAC for High-Mobility Vehicular Links

**Paper role:** Paper 2 is the reliability-focused manuscript. It uses the frozen publication-v2.1 benchmark and the reviewer-grade supplemental evidence already preserved in the repository.

## Scientific question

Given an imperfect estimate of the vehicular PHY state, which physically admissible PC-FMCW action can be offered with a declared confidence-qualified joint sensing--communication reliability, and what availability and computational cost does that reliability require?

## Evidence boundary

The manuscript distinguishes:

1. frozen 1000-seed paired simulation evidence;
2. supplemental uncertainty, ablation, mismatch, finite-draw, Pareto, distribution-shift, and runtime evidence;
3. analytical references and literature-grounded hardware/profile parameters.

No numerical result is presented as an adaptive-controller hardware measurement. The 4096-draw reference is a low-Monte-Carlo-noise comparator, not physical ground truth. Runtime is host-Python/Linux evidence, not embedded real-time certification.

## Core frozen result

The frozen benchmark contains 72,000 receiver-level evaluations across six policies. B4 selects 12.23% of the 12,000 common state/seed units, succeeds in all 1,468 selected cases, and has a one-sided 95% Wilson lower bound of 99.816% conditional reliability. Its unconditional joint-QoS probability is 12.23%, below B3's 16.18%; the paired B4-minus-B3 effect is -0.03942 with 95% bootstrap interval [-0.04292, -0.03600].

The central claim is therefore a reliability--availability--computation trade-off, not unconditional policy superiority.

## Reproduction surface

Primary manuscript sources:

- `manuscript_v2_1.tex`
- `final_abstract_conclusion_abstract_only.tex`
- `final_abstract_conclusion_conclusion_only.tex`
- `final_results_discussion.tex`
- `figures_submission.tex`
- `literature_positioning.tex`
- `results_v2_1_tables.tex`
- `supplemental_v2_1_tables.tex`
- `references_v2_1.bib`
- `references_submission.bib`

Primary machine-readable evidence is under `artifacts/publication/v2_1/`.

## Paper separation

Paper 1 addresses physics-aware configuration selection and deterministic capability boundaries. Paper 2 addresses confidence-qualified reliability, abstention, uncertainty robustness, finite-sample calibration, and the reliability--availability--computation trade-off. The two manuscripts must remain independently citable and independently auditable.
