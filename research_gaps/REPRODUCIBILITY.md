# Reproducible research runbook — 2026-10-14

## Status
All changes belong to PR #81. The frozen publication-v2.1 results and IEEE manuscripts are not changed. The new workflow is **manual** to prevent unintentionally launching expensive full-scale simulations. Passing pytest is software verification, not proof of novelty or reliability.

## Trigger
Open GitHub Actions > **Research Gap Pilot (manual)** > Run workflow, choose `research/three-gap-prototypes-20261014`, then choose the scenario-bank size and robust-draw budget. Run on the exact source SHA that will be reported.

## Outputs
The workflow checks the available research tests, evaluates the historical vs coupled IF conventions, generates a source-derived SVG figure, executes a receiver-level PC-FMCW held-out pilot, records `git rev-parse HEAD`, Python version, dependencies, and SHA256 hashes, and uploads one GitHub Actions artifact.

```
python scripts/run_coupled_if_research.py --convention complex
python scripts/run_coupled_if_research.py --convention positive
python scripts/plot_coupled_if_research.py
python scripts/run_pc_fmcw_research_pilot.py --cases-per-split 8 --draws 32
```

## Methodological limits
- This is a small exploratory pilot (defaults: eight independent scenario seeds per split and 32 draws), not the frozen 512-draw benchmark.
- The policy-level calibration is conditional on the score and B3 selection. The calibration result may abstain on all held-out states; this is a valid negative/inconclusive outcome.
- Held-out receiver results are simulated, not RF measurements.
- The IF convention is provisional until receiver and hardware assumptions are independently validated.
- The finite-sample claims rely on independent units; repeated correlated trajectory states need cluster-aware methods.
- New manuscript figures or claims must not cite exploratory pilot metrics as publication-grade results.
- Check run logs and downloaded artifacts before changing the published manuscripts.

## Research steps still required
A: receiver-validated joint passband, full fair ablation, physically aware comparator, changed-state cause analysis.
B: predeclared hypothesis, independent calibration bank at meaningful sample size, held-out failure risk with confidence intervals, calibration and model-shift study.
C: fully integrated anytime-valid action screening, matched 512-draw B4 comparison, confidence-budget multiplicity across actions, profiling and p95 timings.
A+B+C: factorial combination, evaluation against frozen B3/B4, figures, literature and originality review.
