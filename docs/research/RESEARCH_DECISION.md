# Research Decision — Evidence-Led Paper Direction

Date: 2026-09-12

## Decision

The primary paper claim is **not** that robust B4 universally outperforms deterministic B3. The frozen v2.1 evidence falsifies that stronger hypothesis for unconditional joint QoS: B4−B3 = -0.03942 with 95% paired-bootstrap CI [-0.04292, -0.03600].

The primary research question is therefore:

> Under uncertain high-mobility PC-FMCW operation, how does physics-gated reliability-constrained adaptation reshape the **reliability–availability–resource** operating region relative to deterministic and single-objective adaptation, and which PC-FMCW physical limits determine where reliable operation is possible at all?

## Primary hypothesis

H1: Robust PC-FMCW adaptation can identify a conservative subset of physically supported operating states with confidence-qualified high conditional joint communication+sensing reliability, but this reliability is purchased through abstention/availability loss. The scientifically relevant result is the shape and physical cause of that trade-off, not unconditional policy dominance.

## Secondary hypothesis

H2: State uncertainty contracts the reliable selectable region; this contraction is strongest near PC-FMCW feasibility/QoS boundaries. Individual impairment variables should only be claimed as decision-relevant where ablation or boundary studies show that they move the selection/reliability boundary.

## Evidence motivating the decision

Frozen v2.1: B4 selects 12.23% of states and achieves 100% empirical conditional joint QoS over 1,468 selected states; the one-sided 95% Wilson lower bound is 0.99816. B3 selects 19.07% and has conditional joint QoS 0.84834. Thus B4 is substantially more conservative and more reliable conditional on accepting a state, but has lower unconditional success.

The E11 frozen ablation shows that removing state uncertainty expands selection from 12.5% to 16.67%, while removing CFO or interference does not change aggregate selection in that particular slice. Therefore CFO/interference sensitivity may be physically real without being a demonstrated driver of the robust decision boundary in that experiment.

## Literature boundary

Robust ISAC waveform design, outage/chance constraints, adaptive waveform selection, Doppler-aware ISAC, and PC-FMCW joint radar/communication are established research areas. The defensible gap is narrower: PC-FMCW-specific physical capability screening followed by finite-action probabilistic joint-QoS selection under high-mobility uncertainty, with explicit characterization of abstention/infeasibility and resource cost.

Recent literature makes categorical priority claims unsafe. In particular, robust ISAC under channel uncertainty and outage constraints is established, while recent PC-FMCW work includes experimental joint radar/communication and synchronization studies. The paper should use 'comparatively underexplored intersection' language unless a systematic final database search supports stronger wording.

## Rejected primary claims

1. **B4 universally improves joint QoS over B3.** Rejected by frozen paired evidence.
2. **Chance-constrained/robust ISAC is novel.** Rejected by prior literature.
3. **Adaptive ISAC waveform selection is novel.** Rejected by prior/recent literature.
4. **Doppler/CFO-aware PC-FMCW is novel.** Rejected as a broad claim; synchronization and Doppler compensation have prior PC-FMCW work.
5. **CFO and interference are proven key adaptation mechanisms.** Not established by frozen E11 aggregate ablation.

## Falsification criteria

H1 is weakened if confidence-qualified conditional reliability is not materially higher than deterministic B3 at comparable availability/resource support, or if the apparent gain disappears under modest model mismatch.

H2 is weakened if uncertainty sweeps do not systematically contract the selectable region or if contraction is unrelated to identifiable physical/QoS boundaries.

## Minimum publishable evidence

- validated PC-FMCW physical model and receiver paths;
- explicit one-way communication vs two-way sensing separation;
- strong B0–B4/Oracle common-support evaluation;
- confidence-qualified conditional reliability and availability reporting;
- physical/QoS infeasibility maps;
- state-uncertainty and physics-gate ablations;
- model-mismatch sensitivity;
- resource-cost interpretation;
- negative B4-vs-B3 unconditional result retained prominently;
- claim audit and reproducible artifacts.

## Claim language

Preferred:

> Physics-gated reliability-constrained PC-FMCW adaptation exposes and controls a reliability–availability–resource trade-off under uncertain high-mobility operation, selecting a conservative operating subset with high conditional joint QoS while explicitly abstaining where the declared reliability target cannot be supported.

Avoid:

> The robust policy universally outperforms deterministic adaptation.
