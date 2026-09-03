# Stage 7 — Statistics, Joined Analysis, Figures and Tables

**Canonical implementation:** `stages/07_statistics_and_figures/`

## Scope
Convert frozen scenario-level Stage-05 and Stage-06 results into inferential evidence, joined predictor-to-network analyses, and publication-ready figures/tables.

## Inputs
- Stage-05 raw per-scenario predictor/link-fidelity results;
- Stage-06 raw scenario × seed × scheduler × operating-condition results;
- frozen confirmatory comparison families and reporting rules.

Aggregate-only summaries are insufficient input for this stage because the WOMD scenario is the statistical cluster.

## Statistical protocol
Core publication inference uses:

- 10,000-replicate scenario-cluster bootstrap confidence intervals;
- paired Wilcoxon signed-rank tests for predeclared paired comparisons;
- paired t-test sensitivity analysis;
- effect-size estimates;
- paired win fractions;
- raw and Holm-adjusted p-values for declared multiple-comparison families.

Inference must preserve the paired scenario/seed structure. Individual trajectory samples or horizon steps must not be treated as independent experimental replicates.

## Joined analysis
Join, by frozen scenario identity and experimental condition:

```text
trajectory error (ADE/FDE)
        ↓
future geometry / link fidelity
        ↓
realized scheduler outcome
```

This analysis tests whether displacement accuracy is actually predictive of communication fidelity and whether communication fidelity translates into Goodput/PDR/outage/deadline/latency gains.

## Publication outputs
Required evidence includes raw/adjusted p-values, confidence intervals, effect sizes, win fractions, joined-analysis tables and publication figures. Planned core visualizations include system architecture, Part-A BER calibration, trajectory-to-link examples, ADE-versus-communication fidelity, learned-objective ablation, scheduler forest plots, horizon sweeps, vehicle-count/load operating-region heatmaps, scenario slices, calibration/NLL and complexity/performance trade-offs.

Figures must be generated from frozen artifacts and exported in vector form (`PDF`/`SVG`) plus publication-preview `PNG`; numerical tables must have machine-readable CSV and manuscript-ready LaTeX forms.

Publication artifacts belong under `artifacts/paper_final/statistics/`, `joined_analysis/`, `figures/` and `tables/`.

## Acceptance gate
Stage 7 is complete only when confirmatory families are declared, inference is clustered at scenario level, paired comparisons use matched evidence, Holm-adjusted results are archived, figures/tables are reproducibly generated from frozen inputs, and both favorable and unfavorable operating regimes are retained.

## Current status
`NOT_STARTED` for final publication inference. Existing statistical utilities are implementation assets, not evidence until they are run on the frozen Stage-05/06 scenario-level outputs.

## Scientific role
This stage determines the strength and limits of the paper's claims. A scientifically valid conclusion may be conditional: communication-aware prediction can improve link-state fidelity while its network-level value depends on scheduling flexibility and operating regime.

## Commands
Statistical runners, joined-analysis scripts, figure/table generation and artifact checks belong in `stages/07_statistics_and_figures/`.
