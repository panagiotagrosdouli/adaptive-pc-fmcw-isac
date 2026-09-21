# Stage 07 — Scenario-clustered inference

This implementation provides the confirmatory statistical core. Repeated rows
(including seeds and operating-condition replicates) are averaged within WOMD
scenario before inference. Comparisons fail closed when scenario pairing is
incomplete.

For every predeclared comparison, the runner exports the oriented mean paired
difference (positive means improvement), a 10,000-resample scenario-cluster
bootstrap 95% interval, two-sided paired Wilcoxon p-value, paired t-test
sensitivity p-value, Cohen's dz, win fraction, and family-wise Holm-adjusted
Wilcoxon p-value.

Comparisons are supplied as a frozen JSON list with `comparison_id`, `family`,
`group_column`, `metric`, `treatment`, `control`, `higher_is_better`, and
optional exact-match `filters`. Run tests with `make stage07-test`.

Stage 07 remains `PARTIAL` until frozen Stage-05/06 evidence is analyzed and the
joined tables and publication figures are generated from those artifacts.
