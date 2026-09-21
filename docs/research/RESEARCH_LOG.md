# Research Log

## 2026-09-12 — Research branch and evidence audit

**Question.** Does the current frozen evidence support the planned headline claim that robust B4 is superior to deterministic B3?

**Action.** Created `research/paper-strengthening` from `main`. Inspected the repository tree, contribution positioning, related-work map, frozen v2.1 main results and E9/E11 results. Performed an additional current web literature check for robust ISAC and PC-FMCW work.

**Result.** No. Frozen B4 has higher conditional reliability on selected states but lower availability and lower unconditional joint QoS than B3. B4−B3 unconditional joint QoS is -0.03942 with 95% paired-bootstrap CI [-0.04292,-0.03600]. B4 selects 12.23% of states and succeeds in all 1468 selected cases; its one-sided 95% Wilson lower conditional reliability bound is 0.99816.

**Interpretation.** The strongest defensible story is a reliability–availability–resource operating-region result. Robustness should be framed as selective risk control/abstention, not universal performance superiority.

**Literature criticism.** Robust waveform design under channel uncertainty, outage-constrained ISAC, PC-FMCW joint sensing/communication, automotive PC-FMCW synchronization, and recent PC-FMCW experimental work already exist. Novelty language must focus on the narrower ordered combination of PC-FMCW physical feasibility screening and probabilistic finite-action selection under high-mobility uncertainty.

**Decision.** Freeze the revised research direction in `docs/research/RESEARCH_DECISION.md`; add claim-by-claim restrictions in `docs/research/CLAIM_AUDIT.md`. Preserve the negative B4-vs-B3 result.

**Next scientific priorities.** (1) confidence-qualified E9 post-processing without altering frozen simulations; (2) boundary-focused uncertainty/gate ablations; (3) model-mismatch study; (4) runtime evidence; (5) final systematic bibliography check, especially 2026 PC-FMCW and adaptive ISAC work.
