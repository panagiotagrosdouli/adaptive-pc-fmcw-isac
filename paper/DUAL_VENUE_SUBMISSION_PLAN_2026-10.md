# Two-track IEEE submission plan — 12 October 2026

## Verified venue requirements
- **IEEE RadarConf 2027:** original conference manuscript, IEEE two-column A4, **3–6 pages including references**, title/author affiliation/contact on first page, no page numbers. Abstract entered in the submission portal must not exceed 100 words. IEEE AESS posts the **31 October 2026** deadline. Verify the author portal and final policy immediately before uploading.
  Official sources: https://radarconf2027.org/paper-submission/ and https://ieee-aess.org/event/conference/2027-ieee-radar-conference
- **IEEE Transactions on Aerospace and Electronic Systems (TAES):** separate original contribution within scope, journal author instructions and disclosures. Regular papers may incur overlength charges beyond ten printed pages; the official TAES template is authoritative. See https://ieee-aess.org/publications/transactions-aes/author-information.

## Separate scientific claims and evidence
### Conference — physics-gate ablation (Paper 1)
**Working file:** `paper/radarconf2027_physics_gate.tex`, derived from `paper/paper1_ieee.tex`, not the old mixed-claims `paper/radarconf2027.tex`.
Scope: explicit deterministic capability gate for a finite 54-action PC-FMCW PHY; 238-state boundary-aware stress grid; 132 supportable operating states; 114/132 ungated invalid actions despite a valid alternative; gated selection physical validity on 132/132 supportable states.
No claims of B4 reliability certification, Wilson confidence rule, B3/B4 comparison, or universal field robustness.

### Journal — robust reliability-qualified operation (Paper 2 / v2.1)
**Working file:** `paper/manuscript_v2_1.tex`.
Scope: physics gate as necessary background, B0–B4+Oracle, finite-draw uncertainty qualification, the frozen 12,000 paired state/seed units per policy, B4 selected-case evidence and availability cost, statistically cautious interpretation of the one-sided Wilson bound.
Conference physics-gate experimental findings cannot be republished as new journal results. A journal article submitted after a conference publication must properly cite and disclose the conference article and provide substantively additional analysis and results; confirm the particular venue's overlap policies. **Do not simultaneously submit materially duplicative papers**, and never claim two independent studies simply because the titles differ.

## Release gates
- [ ] RadarConf physics-gate candidate builds successfully and meets six pages and all required metadata/format.
- [ ] Physically inspect all conference pages, all bibliographic metadata, and contrast against the existing mixed `radarconf2027.tex`.
- [ ] Confirm author affiliation, email, approvals and submission portal details.
- [ ] Journal manuscript passes exact-commit LaTeX/CI and detailed claim audit.
- [ ] Perform explicit source/figure/text overlap and copyright disclosure audit.
- [ ] Decide which venue receives which work and record all overlapping sources in cover letter where required.
- [ ] Prepare separate conference and journal source-only ZIP files and PDF checksums.
- [ ] Upload only when approved by the author and compliant with the publisher policies.

These are **candidate** manuscripts; neither is certified ready until its gates are satisfied.
