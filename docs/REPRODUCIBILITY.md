# Reproducibility

Frozen scientific baseline: `3904c4c2a69c4af96751d64614f7228ddea24b56`.

The submission-readiness work from `paper/submission-ready` was merged into `main` by PR #57. Later audit work must preserve the frozen publication-v2.1 evidence under `artifacts/publication/v2_1/`.

## Principles

- Use repository-native scripts and Make targets.
- Keep smoke/diagnostic outputs distinct from frozen publication results.
- Treat the 4096-draw reference as a Monte Carlo comparator, not physical truth.
- Report host runtime separately from embedded or hardware claims.
- Do not overwrite frozen v2.1 evidence with regenerated experiments.
- Run `scripts/audit_repository.py` (or `make repo-audit`) before submission.

## Frozen protocol

Primary source: `configs/paper_protocol_v2_1.json`.

The protocol fixes QoS thresholds, the B4 confidence rule, paired seed bank, final communication/sensing budgets, and bootstrap procedure. Any change creates a new protocol and must not overwrite v2.1 evidence.

## Environment

```bash
python -m pip install -e .[all]
```

Python 3.10+ is required; CI uses Python 3.11.

## Validation

```bash
make test
make research-smoke
make submission-artifacts
make repo-audit
make paper
make submission-check
```

`make submission-check` runs pytest, regenerates submission provenance, executes the repository-wide audit, and builds the IEEE manuscript. It does not rerun the full expensive frozen Monte Carlo campaign.

## Frozen evidence

```text
configs/paper_protocol_v2_1.json
artifacts/publication/v2_1/FINAL_RESULTS.json
artifacts/publication/v2_1/PROVENANCE.json
artifacts/publication/v2_1/tables/
```

## Submission artifacts

`make submission-artifacts` generates:

```text
artifacts/publication/submission/action_space.csv
artifacts/publication/submission/manifest.json
```

The action-space export must contain exactly 54 actions. The manifest hashes the submission-facing code/config/manuscript/provenance inputs and records the checked-out commit; generation fails if the commit cannot be determined.

## Repository-wide audit

`make repo-audit` checks JSON parseability, frozen protocol/result invariants, profile code/config agreement, action-space uniqueness, manuscript source-manifest integrity, citation keys, stale claim wording, frozen table/result consistency, and required CI/Makefile gates.

## Manuscript

`make paper` builds `paper/manuscript_v2_1.tex` with IEEEtran. The GitHub `Manuscript LaTeX Audit` also fails on missing submission sources, unresolved citations/references, or multiply-defined labels.

## Selection-status semantics

Hard physical infeasibility and policy abstention are different. New v2.1 records expose `any_physics_feasible_action` and `selection_status`; a state with physically admissible actions but no QoS/reliability-qualified action is `ABSTAINED_POLICY`, while states outside all profile capability are `NO_PHYSICS_FEASIBLE_ACTION`. The historical `physics_feasible` field remains for backward compatibility.

## Evidence interpretation

The frozen main benchmark contains 12,000 state/seed units per policy and 72,000 receiver-level records over six policies. B4 has 1468/1468 selected successes in the frozen benchmark; this is conditional simulation evidence, not a field guarantee. Host runtime is not embedded-ECU certification.

## Submission status rule

Do not call the repository submission-ready until pytest/CI, repository audit, publication smoke validation, provenance generation, bibliography/source-manifest checks, IEEE LaTeX build, PDF inspection, and frozen-evidence preservation all pass.
