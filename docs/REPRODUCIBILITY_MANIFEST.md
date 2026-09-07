# Reproducibility Manifest

## Scientific identity

- Method: Physics-Gated Reliability-Constrained Adaptive PC-FMCW ISAC.
- Domain: model-based 77-GHz RF/mmWave vehicular PC-FMCW integrated sensing and communication.
- Evidence boundary: analytical and controlled simulation evidence; no new RF measurement campaign.
- Part A relationship: PHY-level RF/mmWave extension of the PC-FMCW ISAC concept, not an experimental improvement measured on the optical laser-headlamp hardware.

## Frozen primary study

- Protocol: `configs/paper_protocol_v2_1.json`.
- Primary evidence commit: `1b2100c11b6d4a7b6213777fd2da85e22601154b`.
- Primary workflow run: `33967030983`.
- Policies: B0 Fixed, B1 Communication-only, B2 Sensing-only, B3 Deterministic Joint, B4 Robust Joint, Hindsight Oracle.
- Final seed bank: 1000 seeds beginning at 10000, 12 scenarios per seed.
- States per policy: 12,000.
- Receiver-level policy evaluations: 72,000.
- Communication bits per selected evaluation: 20,000.
- Sensing trials per selected evaluation: 3.
- B4 internal uncertainty draws: 512.
- Reliability confidence: 95% one-sided Wilson lower bound.
- Joint reliability target: 0.95.
- Paired bootstrap resamples: 10,000.
- Main summary: `artifacts/publication/v2_1/FINAL_RESULTS.json`.
- E9/E11 summary: `artifacts/publication/v2_1/E9_E11_RESULTS.json`.
- Main artifact SHA-256: `31daf1b571c84e4c38380cc8e7d03715eb06d03d7d9ff3e151c49184b5ebdd79`.
- E9/E11 artifact SHA-256: `1aeabd05526bfda796cdebb0df45214c2a7c0f665044faa01dfbd7d8244bb722`.

## Supplemental reviewer study

- Supplemental source commit: `ef0e135b88c7c9647d72195f80884e380bc33cf6`.
- Workflow run: `33975266575`.
- Experiments: uncertainty sweep, impairment stress, physics-only maps, physical-resource Pareto, extended ablations, model mismatch, runtime.
- Provenance: `artifacts/publication/v2_1/supplemental/PROVENANCE.json`.
- Frozen primary thresholds, policy logic, and primary simulations were not changed by the supplemental study.

## Validation and tests

The repository includes tests for waveform/receiver sanity, analytical models, link budget, physics profiles, policy semantics, publication protocol, statistics, publication outputs, and supplemental evidence generation. CI also includes manuscript LaTeX auditing.

## Principal reproduction entry points

```bash
python -m pip install -e .[dev]
pytest -q

python scripts/run_e1_e5_validation.py
python scripts/run_e6_e12_benchmark.py

python scripts/run_supplemental_v2_1.py --experiment uncertainty --output <path>
python scripts/run_supplemental_v2_1.py --experiment stress --output <path>
python scripts/run_supplemental_v2_1.py --experiment physics --output <path>
python scripts/run_supplemental_v2_1.py --experiment pareto --output <path>
python scripts/run_supplemental_v2_1.py --experiment ablations --output <path>
python scripts/run_supplemental_v2_1.py --experiment mismatch --output <path>
python scripts/run_supplemental_v2_1.py --experiment runtime --output <path>
```

For the immutable primary publication result, use the repository's v2.1 GitHub Actions workflow and frozen protocol rather than changing thresholds or action definitions locally.

## Evidence classes

Every reported numerical item should be tagged as one of:

1. source-derived parameter;
2. analytically derived quantity;
3. controlled simulation variable;
4. simulation output;
5. external measured value.

Simulation outputs must never be relabeled as measurements.

## Known reproducibility limitations

- Full raw primary and supplemental bundles are preserved as GitHub Actions artifacts rather than all being committed to Git because of size.
- Runtime values depend on Python implementation and CI hardware and are not embedded-target latency measurements.
- The high-mobility profile is a composite capability reference.
- Phase-noise sensitivity is not calibrated to a specific oscillator phase-noise mask.
- Primary E9 target flags are empirical-mean based; confidence-qualified region labeling requires post-processing from success/trial counts.
