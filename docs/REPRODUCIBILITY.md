# Reproducibility

Frozen scientific baseline: `3904c4c2a69c4af96751d64614f7228ddea24b56`.
Submission branch: `paper/submission-ready`.

## Principles

- Preserve frozen primary evidence under `artifacts/publication/v2_1/`.
- Use repository-native scripts and Make targets rather than ad-hoc calculations.
- Keep diagnostic/smoke outputs distinct from final publication results.
- Treat the high-draw reference as a Monte Carlo comparator, not physical truth.
- Report host runtime separately from deployment or ECU claims.
- A regenerated experiment must never silently overwrite the frozen v2.1 artifact family.

## Frozen protocol

Primary source: `configs/paper_protocol_v2_1.json`.

The protocol fixes QoS thresholds, B4 confidence qualification, paired seed bank, final communication/sensing evaluation budgets and bootstrap procedure. Any change to these settings creates a new protocol and must not overwrite v2.1 evidence.

## Environment

```bash
python -m pip install -e .[all]
```

The package requires Python 3.10 or newer; CI currently exercises Python 3.11.

## Fast scientific validation

```bash
make test
make research-smoke
```

CI additionally executes Stage-7, E1--E5, E6--E12, and full supplemental smoke runs.

## Frozen evidence inspection

Primary frozen files include:

```text
configs/paper_protocol_v2_1.json
artifacts/publication/v2_1/FINAL_RESULTS.json
artifacts/publication/v2_1/PROVENANCE.json
artifacts/publication/v2_1/tables/
```

These files define the historical paper-v2.1 evidence and are not rewritten by the submission branch.

## Reviewer-grade supplemental reproduction

The repository exposes native targets such as:

```bash
make research-calibration
make research-action-space
make research-distribution-shift
make research-qos-sensitivity
make experiments
make gate
make verdict
make figures
make tables
```

`make paper-results` chains the full supplemental experiment, gate, verdict, figure, and table path for the selected `ARTIFACT_DIR`. Because this is substantially more expensive than smoke validation, do not run it unintentionally on every commit.

## Submission-facing artifacts

```bash
make submission-artifacts
```

This generates:

```text
artifacts/publication/submission/action_space.csv
artifacts/publication/submission/manifest.json
```

The action-space exporter is derived directly from the frozen action enumerator and fails if the action count is no longer 54. The manifest records SHA-256 hashes and sizes for submission-facing scientific/manuscript files.

## IEEE manuscript

With `latexmk` and the IEEE/TeX packages installed:

```bash
make paper
```

The GitHub `Manuscript LaTeX Audit` workflow additionally validates `paper/SUBMISSION_SOURCE_MANIFEST.txt`, builds `paper/manuscript_v2_1.tex`, and fails on unresolved citations/references or multiply-defined labels.

## Local submission gate

```bash
make submission-check
```

This runs the Python test suite, regenerates submission-facing provenance artifacts, and builds the IEEE manuscript. It does not rerun the entire expensive primary/supplemental Monte-Carlo publication campaign; those evidence families remain versioned separately.

## Evidence interpretation

The main paired benchmark contains 12,000 state/seed units per policy and 72,000 receiver-level evaluations over six policies. B4's 1468/1468 selected successes and corresponding Wilson bound are conditional frozen simulation results. The 4096-draw calibration reference reduces Monte-Carlo decision noise but is not physical ground truth. Host runtime is not embedded-ECU certification.

## Submission status rule

Do not label a branch `SUBMISSION READY` until:

- full pytest/CI is green;
- publication smoke validation is green;
- action-space and manifest generation pass;
- bibliography and source manifest are consistent;
- IEEE LaTeX build is green with no unresolved citations/references;
- final PDF has been visually inspected;
- frozen evidence remains unchanged;
- claim/reviewer audits are complete.
