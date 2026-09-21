# Final Submission Checklist

This checklist is the human-facing companion to the executable repository gates.

## Manuscript

- [x] IEEE journal class and two-column layout.
- [x] Abstract reports real frozen benchmark numbers and negative results.
- [x] PC-FMCW one-way communication and two-way sensing semantics are separated.
- [x] Dechirped IF sensing model is stated correctly.
- [x] Physical feasibility equations and action-space definition agree with code.
- [x] B0-B4 and Oracle roles are defined without deployability overclaiming.
- [x] One-sided Wilson qualification is explicitly derived and interpreted.
- [x] Reliability, availability, and unconditional service probability are distinguished.
- [x] Frozen primary benchmark and supplemental experiments are clearly separated.
- [x] Runtime is labeled host/Python timing, not ECU certification.
- [x] Hardware-measurement claims are excluded.
- [x] Literature positioning and bibliography are verified against publication sources.
- [x] Source-to-claim and figure-provenance records are included.

## Evidence

- [x] Frozen publication-v2.1 evidence is preserved unchanged.
- [x] 12,000 paired units per policy / 72,000 receiver-level primary evaluations are documented.
- [x] B4 1468/1468 selected successes and the one-sided 95% Wilson lower bound are preserved.
- [x] Negative paired B4-B3 unconditional result is preserved.
- [x] Finite-draw calibration includes the 32-draw non-certifiability result.
- [x] Uncertainty, ablation, distribution-shift, mismatch, action-space, and runtime evidence are retained with claim boundaries.

## Reproducibility

- [x] `make test` exists.
- [x] `make repo-audit` exists.
- [x] `make paper` exists.
- [x] `make submission-artifacts` exists.
- [x] `make submission-check` exists.
- [ ] `make submission-bundle` passes on the release candidate commit.
- [ ] Final GitHub CI passes on the release candidate commit.
- [ ] Final Manuscript LaTeX Audit passes on the release candidate commit.
- [ ] Final compiled PDF is visually inspected after the release candidate build.
- [ ] Release bundle artifact is downloaded and opened successfully.

The unchecked release-candidate items must be completed by CI/build validation on the exact final commit before a tag/release is created.
