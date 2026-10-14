# Three-gap research workbench: evidence status (14 October 2026)

Base: main commit a80ddb1a312e6f26c946a08b6c5acaf81b2c71a4.
Frozen publication-v2.1 evidence remains unchanged.

## A — Joint range/Doppler/IF
Known issue: independent range and Doppler inequalities omit the combined signed beat condition. Previous PR #80 was closed; examine its historical diagnostic and verify the receiver passband convention before choosing the corrected physical model. No replacement Paper 1 results are asserted.

## B — Selective reliability
New module: src/pcfmcw_isac/research_gap_methods.py, function calibrate_fixed_thresholds.
This is a conservative confirmatory calibration **building block**, not an integrated PC-FMCW policy. Requires a fixed scoring rule, predeclared thresholds, independent calibration units, and separate final held-out testing. Beware effective sample size and dependence of scenario/seed clusters.

## C — Adaptive computation
New module: anytime_bernoulli_decision, with time-uniform Hoeffding bounds using a summable alpha allocation. This is a safe but intentionally conservative *prototype*, not demonstrated speedup for B4; its stringent target may never accept at 512 draws. Compare matched risk and actual runtime before claiming benefit.

## Outstanding deliverables
Integrate A/B/C into copied, versioned controller pathways (not frozen policies), create independent development/calibration/validation/test banks, run A1-A10, B-E1-B-E12, C-E1-C-E10 and combined factorial ablations. Generate new machine-readable figures and provenance; independent literature/DOI audit and full exact-SHA LaTeX/PDF checks remain outstanding.

Status: RESEARCH IN PROGRESS. Neither IEEE manuscript is newly certified submission-ready.
