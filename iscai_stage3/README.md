# Stage 3 — truth-free causal association and tracklets

The canonical Stage-3 boundary consumes only Stage-2
`UnlabeledDetectionFrame` objects. Oracle WOMD IDs, actor classes, and truth
sidecars are evaluator-only and are not accepted by the tracking API.

All measurements are transformed from the time-varying headlamp frame `Ht` to
the common anchor frame `H0` before temporal differences or association are
computed. Spherical measurement covariance is propagated with the full
range/azimuth/elevation Jacobian and rotated into `H0`.

`tracking.gnn` provides a deterministic covariance-aware GNN baseline with a
three-dimensional chi-square gate. It is deliberately not labelled as a
multi-hypothesis method. A
future Multi-Hypothesis Tracking implementation must consume the same
truth-free Cartesian contract
and be evaluated against this baseline with identical frames and splits.

In this repository `MDHT` means Multidimensional Hough Transform. It will be
used for anonymous tracklet initialization before association. The abbreviation
`MHT` is not used for Multi-Hypothesis Tracking, preventing acronym ambiguity.
