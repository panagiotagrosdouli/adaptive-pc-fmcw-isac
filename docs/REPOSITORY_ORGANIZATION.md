# Repository Organization

This file defines the non-destructive repository layout for the predictive-connectivity paper.

The organization is intentionally stage-oriented: each scientific block has one clearly named home, while legacy beam/ADB research remains available for reference and is not renamed or rewritten as part of this reorganization.

## Top-level layout

```text
.
├── README.md
├── Makefile
├── pyproject.toml
├── docs/
│   └── REPOSITORY_ORGANIZATION.md
├── stages/
│   ├── 00_freeze_and_provenance/
│   ├── 01_womd_data_pipeline/
│   ├── 02_pc_fmcw_dpsk_link/
│   ├── 03_classical_baselines/
│   ├── 04_communication_aware_gru/
│   ├── 05_official_predictor_evaluation/
│   ├── 06_packet_scheduling/
│   ├── 07_statistics_and_figures/
│   └── 08_final_paper/
├── artifacts/
│   └── paper_final/
└── iscai_stage*/
    └── legacy/reference implementation from the earlier beam/ADB research line
```

## Organization rules

1. `README.md` explains the active scientific question, causal pipeline, stage map, boundaries, evaluation protocol and submission gate.
2. `stages/` is the active paper workflow. New predictive-connectivity implementation belongs here.
3. Every stage keeps its own `stage.json`, README/instructions, executable scripts and tests where appropriate.
4. Cross-stage publication outputs are written under `artifacts/paper_final/` rather than scattered across source directories.
5. Raw WOMD files and large checkpoints are not committed. Their paths, hashes and manifests are committed or archived as publication evidence.
6. `iscai_stage0`–`iscai_stage7` remain legacy/reference code. They are not silently deleted, renamed or presented as the main contribution of the new paper.
7. Part-A receiver-derived communication evidence is treated as a frozen dependency. New geometry/link assumptions are explicitly identified as model extensions.
8. Stage status describes evidence, not file existence: `DONE`, `PARTIAL`, `BLOCKED`, `NOT_STARTED`.

## Scientific ownership by stage

| Stage | Scientific ownership |
|---|---|
| 00 | experiment freeze, code/data/config provenance, overlap audit |
| 01 | canonical WOMD corpus and true future actor–SDC geometry |
| 02 | Part-A DBPSK receiver calibration and geometry-to-link model |
| 03 | causal classical predictors and non-learned scheduler baselines |
| 04 | shared GRU architecture, communication-aware objectives, lambda selection, learned calibration |
| 05 | untouched official-WOMD predictor and link-fidelity evaluation |
| 06 | packet traffic, queues, deadlines and paired scheduler experiments |
| 07 | scenario-clustered inference, joined analyses, figures and tables |
| 08 | manuscript, supplement, claims audit and final reproduction bundle |

## Artifact ownership

```text
artifacts/paper_final/
├── manifests/
├── data_audit/
├── ber/
├── lambda_sweep/
├── checkpoints/
├── predictor_eval/
├── scheduler_eval/
├── statistics/
├── joined_analysis/
├── figures/
├── tables/
├── complexity/
└── reproduction/
```

Source code should never depend on a manuscript figure or manually edited aggregate. Figures and tables are downstream products of frozen machine-readable artifacts.

## Naming convention

Use descriptive scientific names rather than temporary experiment names. Examples:

- `womd_v131_training_development.npz`
- `womd_v131_official_validation.npz`
- `dbpsk_ber_lut.csv`
- `link_model_config.json`
- `lambda_selection.json`
- `trajectory_plus_link_seed_11.pt`
- `official_validation_scenario_metrics.csv`
- `scheduler_raw_scenario_seed_policy.csv`

Do not use filenames that imply a result is final before the corresponding evidence gate has passed.

## Legacy boundary

The existing `iscai_stage*` directories are kept so previous experiments remain reproducible. New paper code should not be duplicated into those directories merely for visual consistency. If a legacy component is scientifically reused, the new stage should import/migrate the needed implementation explicitly and document the provenance.
