# Supplemental statistical sensitivity checks (post-freeze)

These checks are additional research diagnostics; **they do not revise** the
publication-v2.1 frozen results, confidence intervals, or manuscript benchmark.

## Seed-clustered sensitivity

The frozen paired bootstrap samples individual (seed, scenario) units. The
predeclared design contains 12 scenarios per seed; hence seed-level dependence
could matter. The supplementary `scripts/seed_clustered_bootstrap.py` resamples
whole seeds, retaining all their scenario observations and preserving B3/B4
pairing. Both an observation-level interval and a clustered interval should be
reported before population-level interpretations are made.

A suitable source is the **actual receiver-level** records JSON, not the
aggregate `FINAL_RESULTS.json`:

```bash
python scripts/run_e6_e12_benchmark.py --n-seeds 10 --comm-bits 20000 --sensing-trials 3 --output artifacts/supplemental_cluster_input.json
python scripts/seed_clustered_bootstrap.py --input artifacts/supplemental_cluster_input.json --output artifacts/supplemental_clustered_ci.json
pytest -q tests/test_seed_clustered_bootstrap.py
```

**IMPORTANT:** The first command runs the older E6-E12 benchmarking entrypoint;
it is a pipeline demonstration and **not** automatically the frozen v2.1 final
protocol. For reviewer-grade results, use the frozen v2.1 driver/receiver records,
match exact protocol/seed/configuration metadata, and label the supplemental
output appropriately. The frozen summary JSON lacks scenario-level paired
records and cannot support clustered intervals by itself.

## Adaptive action-selection multiplicity

The nominal one-sided Wilson lower bound for each individual candidate action
does not alone provide familywise coverage across the entire candidate set
when the best qualifying action is selected using the same uncertainty draws.
An independent held-out verification or simultaneous/multiplicity-adjusted
bounds are appropriate sensitivity analyses. They should track selected
action, per-action draws, selection-rule outcome, and independent validation
outcomes, without treating a large-draw simulator as physical ground truth.

No new reliability certification or generalized improvement should be claimed
until such a study is actually executed and its assumptions audited.

## Acceptance criteria

- Report number of independent seeds, scenarios per seed, and sampling unit.
- Verify matching paired keys and reject missing or duplicate evaluations.
- Record RNG seed, confidence level, resample count, scripts and commit SHA.
- Never silently promote smoke outputs or supplemental numbers to frozen results.
