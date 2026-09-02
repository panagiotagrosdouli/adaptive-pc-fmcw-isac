# Stage 0 - Dataset and reproducibility audit

Stage 0 inventories the locally licensed WOMD/WOMD-LiDAR data and records the
runtime environment without embedding a researcher-specific filesystem path.
It does not train models and does not make performance claims.

## Dataset location

Provide the dataset root explicitly:

```bash
export WOMD_ROOT=/path/to/waymo
```

or pass `--dataset-root`. Command-line configuration takes priority over the
environment, which takes priority over a non-null config value.

## Canonical commands

```bash
python iscai_stage0/scripts/audit_environment.py
python iscai_stage0/scripts/audit_dataset_layout.py
```

The output reports distinguish filename-based split heuristics from fields
verified by parsing WOMD records. Raw data are never copied into the repository.

## Scientific scope

- WOMD/WOMD-LiDAR version: configured and recorded in the Stage-0 config.
- Part A: not applicable to the primary trajectory-to-control methodology.
- A successful Stage 0 establishes data accessibility and provenance only.
- Dataset/model validity is evaluated by later stages.
