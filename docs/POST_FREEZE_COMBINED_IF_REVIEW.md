# Post-freeze combined IF feasibility finding (2026-10-14)

**Status: Open scientific issue — no frozen results changed.**

The canonical `physics_feasibility` in `src/pcfmcw_isac/publication_protocol.py` checks range against the zero-Doppler positive-IF bound and radial velocity against the slow-time ambiguity limit **independently**.

However `target_frequencies` in `src/pcfmcw_isac/if_model.py` defines the signed beat as

```
fb = (B/Tc) * (2R/c) + (2 v fc/c)
```

At a positive range boundary and positive radial velocity, the canonical gate can accept a target with beat frequency above `Fs/2`, even under the repository's nominal IF convention. This is an analytical consequence; the added regression test records an example.

## Research impact

* The frozen publication-v2.1 baseline and Paper 1 ablation **must not be silently rewritten**.
* Before either paper is submitted, determine whether the receiver IF convention, positive beat passband, Doppler sign, and ADC Nyquist definition support a stricter joint gate. A complex sampled IF convention can differ from a real positive-IF passband; clarify hardware assumptions before choosing the final gate.
* Run a **separately versioned** ablation with the joint bound, recalculate the 238-state support counts and gated-vs-ungated comparisons, and update all manuscripts and evidence manifests if scientific claims change.
* Check mirrored sign/negative-frequency and radar processing behavior. Validate at boundaries and for combinations of R/v, not only at separate maxima.
* Do not claim the 132/238 and 114/132 figures remain valid for the stricter joint gate until recomputed.

Added standalone diagnostic: `src/pcfmcw_isac/if_feasibility_diagnostic.py`.
Regression tests: `tests/test_combined_if_feasibility_diagnostic.py`.

The diagnostic does not establish RF measurement performance or global feasibility, and it does not modify the production selector.
