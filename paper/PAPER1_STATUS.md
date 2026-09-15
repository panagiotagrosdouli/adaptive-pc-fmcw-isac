# Paper 1 Status

Baseline Paper 1 branch `paper1-ieee-submission` was merged into `main` as commit `7177acbee8c46417eedd655a08ea4a5ef5febf2b`; the standalone IEEE manuscript, independent bibliography, claim audit, evidence manifest, vector figures, and dedicated LaTeX CI were already established there.

Current post-baseline work: branch `paper1-physics-gate-ablation`, PR #66. This extension adds a Paper-1-specific deterministic gated-versus-ungated configuration-selection ablation, boundary-aware range--velocity evidence, generated table/figure inputs, reproducibility target, and tests. It is explicitly post-freeze Paper 1 evidence and does not alter `artifacts/publication/v2_1/`.

The ablation remains scientifically separate from Paper 2/v2.1 reliability evidence: no B4 Monte Carlo qualification, Wilson confidence rule, paired-policy reliability benchmark, or reliability--availability--computation claim is imported into Paper 1.

Submission status for this extension is conditional on PR #66 CI/LaTeX checks completing successfully and final visual inspection of the resulting PDF.
