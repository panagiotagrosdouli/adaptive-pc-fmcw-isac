# Final manuscript preflight — release candidate (2026-10-12)

**Target:** `paper/manuscript_v2_1.tex` (IEEEtran journal-format scientific manuscript).  
**Candidate base:** `2c7b2fc2ea425b2c13630d148e26de3e97e2809d` (`main` as inspected 2026-10-12).  
**Status: NOT YET SUBMISSION READY.** This record is a preflight plan, not a pass certificate.

## Protected research record

Keep `artifacts/publication/v2_1/`, the frozen baseline `3904c4c2a69c4af96751d64614f7228ddea24b56`, the declared 54-action set, the evaluated simulation protocol, and all primary results unchanged. Do not reinterpret host timing as embedded real-time evidence or Monte-Carlo outputs as RF field measurements. Preserve the B4-versus-B3 negative unconditional comparison.

## Required execution on the exact proposed release commit

Run after checking out the final release candidate, not only on an earlier green commit:

```bash
python -m pip install -e '.[all]'
pytest -q
make submission-artifacts
make repo-audit
make submission-check
make submission-bundle
```

Inspect the `CI`, `Manuscript LaTeX Audit`, and applicable publication smoke workflows for the **same exact SHA**. The LaTeX audit must produce a successfully compiled PDF, resolve references/citations, check duplicate labels, and validate the ZIP members. Record workflow run URLs, commit SHA, and artifact SHA-256 values in the release notes.

## Manual PDF acceptance gate

Download `manuscript-v2-1-submission` for the exact release SHA. Open the PDF and inspect *every page* for cropped equations, illegible tables/figures, awkward floats, broken symbols, bibliography truncation, page limits, and readable labels. Validate fonts and PDF constraints with the chosen publisher's checker. Mark this gate passed only after actual inspection, with reviewer/date.

## Editorial and scientific acceptance gate

- Choose the journal/conference **before** certifying a submission. `manuscript_v2_1.tex` currently uses `\\documentclass[journal]{IEEEtran}` and `Anonymous Author(s)`; author metadata and blind-review rules are venue-dependent.
- Independently verify bibliography DOIs, publication metadata and references against final publisher information.
- Verify abstract, tables, figures and discussion against `artifacts/publication/v2_1/FINAL_RESULTS.json` and `paper/SOURCE_TO_CLAIM_TRACEABILITY.md`; report uncertainty and conditional denominators accurately.
- Check similarity, permissions for reused material, conflict-of-interest, funding, data/code availability and author approvals according to venue policy.
- Create the venue-specific source package using only required LaTeX sources and figures. The broad reproducibility ZIP is **not** automatically the publisher upload ZIP.

## Sign-off (do not tick without evidence)

- [ ] Final release SHA recorded:
- [ ] Full tests and scientific audit pass on that SHA:
- [ ] Publication smoke and manuscript build pass on that SHA:
- [ ] Deterministic release bundle downloaded and ZIP integrity verified:
- [ ] Compiled PDF manually inspected on every page:
- [ ] Target venue, page limit and blind-review metadata verified:
- [ ] Bibliography and author declarations verified:
- [ ] Publisher-compliant PDF and source ZIP prepared:
- [ ] Submission owner authorizes final release/tag:

This gate does not imply paper acceptance, field validation, or hardware-readiness.
