# Paper 1 Status

The standalone IEEE Paper 1 baseline and the subsequent deterministic physics-gate ablation/reviewer-hardening work have been merged into `main`. The latest merged head is `05de967f1cece4ab102d1aee4fd46c8816dda5fc`.

Current Paper 1 scope: a PHY-level, simulation/model-based study of finite 54-action PC-FMCW configuration selection with a state-dependent deterministic range/velocity admissibility layer. The primary gate-ablation result conditions on 132 supportable states within a 238-state boundary-aware stress grid: the ungated nominal selector chooses an unsupported action in 114/132 states (86.36%) despite a valid alternative, while the gated selector returns physically valid selections in all 132. The full-grid 220/238 (92.44%) value remains a secondary stress-grid diagnostic.

The paper explicitly separates recoverable configuration-selection failures from globally unsupported states, and it does not interpret the stress grid as a real-driving distribution.

The literature/novelty pass has been strengthened to acknowledge established PC-FMCW, adaptive/cognitive radar, and recent adaptive FMCW/ISAC reconfiguration work. The paper does not claim novelty for FMCW equations, PC-FMCW itself, adaptive waveform selection in general, or physical limits individually. The scoped contribution is the explicit state-dependent physical-admissibility layer preceding finite-action PC-FMCW ranking, together with the controlled gate-removal evidence.

Paper 1 remains scientifically separate from Paper 2/v2.1 reliability evidence: no B4 Monte Carlo qualification, Wilson confidence rule, paired-policy reliability benchmark, or reliability--availability--computation claim is used as Paper 1 evidence.

CI, Paper 1 IEEE LaTeX, Manuscript LaTeX Audit, and Repository Autopilot checks for the merged reviewer-hardening work completed successfully. Final submission remains subject to the normal human editorial decision and any venue-specific submission requirements.
