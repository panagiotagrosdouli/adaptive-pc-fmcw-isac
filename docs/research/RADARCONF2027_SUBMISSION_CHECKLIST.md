# RadarConf 2027 Submission Candidate Checklist

Date: 2026-09-30

## Candidate source

- Manuscript: `paper/radarconf2027.tex`
- Compact figures/tables: `paper/radarconf2027_figures.tex`
- Bibliography: `paper/references_v2_1.bib`, `paper/references_submission.bib`
- Source manifest: `paper/RADARCONF2027_SOURCE_MANIFEST.txt`
- Candidate manuscript commit: `9544c83b9c1145f1c9e7e126ac0d7777618ad2a0`
- Frozen branch: `radarconf2027-submission-candidate` (points to the candidate manuscript commit)
- Dedicated CI: `.github/workflows/radarconf2027_latex.yml`

## Scientific claim to preserve

> The contribution is an admissibility-first PC-FMCW controller: hard range, IF-sampling, and unambiguous-velocity limits are enforced before finite-action uncertainty-aware joint sensing/communication reliability qualification. The controller abstains when no physically admissible action has sufficient finite-sample evidence to meet the declared reliability target.

Do **not** broaden this into a claim that adaptive PC-FMCW, robust ISAC, synchronization, or waveform selection is new in isolation.

## Core evidence included

- Finite 54-action PC-FMCW PHY action space.
- 12,000 paired operating-state/seed units per policy.
- 72,000 final receiver-level evaluations across six policies.
- B3 selection: 19.07%; conditional joint QoS: 84.83%.
- B4 selection: 12.23%; 1,468/1,468 selected successes.
- B4 one-sided 95% Wilson lower bound: 99.816%.
- B4--B3 unconditional joint-QoS difference: -0.03942, 95% paired-bootstrap interval [-0.04292,-0.03600].
- No-physics-gate ablation: 31.67% selection and 0% joint QoS in the frozen supplemental design.
- 512-draw feasibility disagreement vs. 4096-draw comparator: 0%; selected-action disagreement: 0.833%.
- 512-draw B4 host median latency: 251.04 ms; p95: 504.11 ms.

## Claim boundaries

The manuscript must continue to state that:

- B4 is not universally or unconditionally superior to B3.
- Observed 100% selected-case success is not a universal 100% reliability guarantee.
- The 4096-draw comparator is not physical ground truth.
- The high-mobility profile is a composite capability reference, not a commercial preset.
- Runtime is from an unoptimized Python/Linux host, not an embedded ECU.
- The results are simulation/analytical/statistical/host-runtime evidence, not RF hardware validation.

## Literature threats explicitly covered

- Uysal automotive PC-FMCW.
- Lampel PC-FMCW RadCom synchronization.
- Kumbul PC-FMCW sensing/communication line.
- Alami El Dine PC-FMCW synchronization and Doppler compensation.
- Temiz et al. 2026 reconfigurable FMCW ISAC and TCOM hardware study.
- Wang et al. 2024 robust ISAC waveform design.
- Tholeti cognitive waveform selection.
- Yazar et al. 2026 adaptive ISAC waveform selection.

See `docs/research/DEEP_LITERATURE_AUDIT_2026-09-30.md`.

## Venue constraints

IEEE Radar Conference 2027 currently requires:

- IEEE standard two-column conference format.
- A4 paper size.
- 3--6 pages, including figures, tables, and references.
- Submission-system abstract no longer than 100 words.
- Author names, affiliations, and contact information on the first page.
- Current full-paper deadline: 31 October 2026.
- The conference currently states that papers cannot be updated after submission because review begins immediately; upload only the frozen, coauthor-approved PDF.

The dedicated CI automatically fails if the PDF exceeds six pages or contains unresolved citations/references.

## Automated validation

The table-enhanced candidate immediately preceding the final provenance-citation edit compiled successfully at **4 pages** with:

- source-manifest validation: PASS;
- LaTeX build: PASS;
- unresolved citations/references: PASS;
- six-page limit: PASS;
- artifact upload: PASS;
- no overfull-box warning reported;
- only non-fatal underfull-box warnings.

A final rebuild is required for candidate commit `9544c83b9c1145f1c9e7e126ac0d7777618ad2a0` because it adds the missing provenance citation for the source-grounded short-range profile.

## Human-only items before upload

- [ ] Insert actual author names.
- [ ] Insert affiliations.
- [ ] Insert corresponding-author email/contact details.
- [ ] Confirm author order with all coauthors.
- [ ] Confirm all coauthors approve the final manuscript.
- [ ] Confirm submission-system topic/track selection.
- [ ] Run the venue-prescribed final IEEE PDF compliance check.
- [ ] Re-check title and 90-word submission abstract in the portal.
- [ ] Upload the PDF only after the final dedicated CI run is green.

## Current status

**SUBMISSION CANDIDATE — technically mature, awaiting the final CI rebuild and human author metadata.**
