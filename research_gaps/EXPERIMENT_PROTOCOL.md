# Preregistered design for three research gaps (prototype stage)

## Independent units
Sample scenario/trajectory clusters without overlapping random seeds between development, calibration, validation and final test. Declare and store all partition keys before tuning.

## Gap A
Recompute signed beat f_b = 2(B/Tc)R/c + 2vf_c/c and compare to the actual receiver IF band. Check Doppler ambiguity separately. Investigate real vs complex sampling, negative Doppler, and guard bands. Preserve the old 238-state grid as historical comparator. Compare gate-only, independent-bound gate, coupled gate, and a meaningful physics-aware baseline.

## Gap B
Choose scores and a finite threshold grid on development data; fix them before calibration. For each threshold, use independent calibration outcomes and Bonferroni-adjusted one-sided Hoeffding upper bounds. Select the threshold offering maximum coverage with risk upper bound <= epsilon. Test it once on held-out seeds/clusters. Define whether risk control applies globally over selections or per stratum; do not infer conditional guarantees under arbitrary distribution shift.

## Gap C
Use optional-stopping-safe confidence sequences, with alpha spending sum_t alpha/[t(t+1)] <= alpha, for sequential Bernoulli qualification. Compare against fixed 64/128/256/512-draw policies at matched failure risk; report abstention, mean/median/p95 wall time, and draws. Do not treat time-uniform concentration bounds as action-selection multiplicity correction; budget alpha across tested actions when making joint claims.

## Four-axis evaluation
Run A, B, C separately, pairwise, and combined, alongside frozen B3/B4 (unchanged) and explicitly labeled Oracle. Report all negative findings. No unrun experiment may be labeled completed.
