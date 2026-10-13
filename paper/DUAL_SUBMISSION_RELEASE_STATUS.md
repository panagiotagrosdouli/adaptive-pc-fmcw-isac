# Dual-paper release readiness — exact-commit evidence (2026-10-12)

**Reviewed commit:** `846948fc20fd7057b3a0d461a3bbe30c16a0f5da`
**Status:** CANDIDATE, NOT APPROVED FOR UPLOAD.

## Checks that have actually passed on the reviewed SHA

| Gate | Status | Workflow |
|---|---|---|
| Repository CI | PASS | https://github.com/panagiotagrosdouli/adaptive-pc-fmcw-isac/actions/runs/38219984747 |
| Repository Autopilot | PASS | https://github.com/panagiotagrosdouli/adaptive-pc-fmcw-isac/actions/runs/38219984707 |
| RadarConf physics-gate IEEE LaTeX / 3–6 page check | PASS | https://github.com/panagiotagrosdouli/adaptive-pc-fmcw-isac/actions/runs/38219984640 |
| Journal manuscript IEEE LaTeX audit | PASS | https://github.com/panagiotagrosdouli/adaptive-pc-fmcw-isac/actions/runs/38219984554 |
| Paper 2 IEEE LaTeX | PASS | https://github.com/panagiotagrosdouli/adaptive-pc-fmcw-isac/actions/runs/38219984624 |
| Supplemental three-seed clustered-bootstrap smoke | PASS (diagnostic only) | https://github.com/panagiotagrosdouli/adaptive-pc-fmcw-isac/actions/runs/38219985243 |

## Required before the author uploads

1. **RadarConf:** replace the literal author-affiliation/contact placeholder in `paper/radarconf2027_physics_gate.tex` with the author's verified affiliation and email; check the final portal requirements. The passing build does not validate this metadata.
2. **Journal:** `paper/manuscript_v2_1.tex` still contains anonymous metadata; apply the journal's anonymity/author policy and verify author declarations.
3. Download the **exact final commit's** PDF artifacts and inspect each page (both versions), including figures/tables, rendered math, font embedding and publisher PDF constraints.
4. Independently audit citation publisher metadata and the policy governing previously presented/related conference material; disclose and cite related work. The conference physics-gate evidence and journal B4 evidence must remain different primary scientific contributions.
5. Run reviewer-grade held-out post-selection reliability and seed-clustered uncertainty experiments if those are needed to substantiate stronger statistical claims. A three-seed smoke test is not such evidence.
6. Create publisher-specific source/PDF bundles from the final accepted commit, record SHA-256 digests, and review their contents. The existing reproducibility archive is not necessarily a publisher upload ZIP.
7. Obtain author/coauthor final consent; do not merge, tag or submit without approval.

The frozen publication-v2.1 experiments and negative B4/B3 result must remain unchanged. Only performed checks are marked PASS.
