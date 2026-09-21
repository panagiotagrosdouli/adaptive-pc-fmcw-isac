# Paper 1 Claim Audit

## Allowed as manuscript claims

- 77-GHz PC-FMCW can be represented by a common FMCW carrier with phase-coded communication, based on the cited PC-FMCW literature.
- The simulator separates one-way communication propagation from two-way monostatic sensing.
- Sensing is evaluated at dechirped IF rather than by directly sampling the 77-GHz carrier.
- The parking profile has approximately 0.175-m range resolution and approximately 8.41-m/s monostatic unambiguous radial velocity under the declared formulas and source-grounded parameters.
- The composite high-mobility capability profile has approximately 0.150-m range resolution and approximately 48.67-m/s monostatic unambiguous radial velocity under the declared parameters.
- The finite configuration space contains 54 actions from 2 profiles × 3 chip budgets × 3 power backoffs × 3 repetition factors.
- The pilot DBPSK reference follows the analytical AWGN expression closely under the declared assumptions.
- The pilot sensing results show a strong SNR dependence in the declared simulation model.
- On the declared 238-state boundary-aware capability grid, 132 states are physically supportable by at least one action and 106 are outside the support of the complete declared action set.
- The primary gate-ablation comparison conditions on the 132 physically supportable states: the ungated nominal selector chooses a physically invalid action in 114/132 states (86.36%) despite a valid alternative existing in the same 54-action set; only 18/132 supportable states receive a physically valid ungated selection.
- On those same 132 supportable states, the gated selector returns physically valid selections in all 132 states and makes zero physically invalid selections by construction under the implemented physical model.
- Over the full 238-state stress grid, the ungated selector selects in all 238 states and 220 selections (92.44%) violate the selected profile's deterministic FMCW range/velocity support; this is a secondary stress-grid diagnostic, not a field prevalence estimate.

## New gate-ablation wording boundaries

Preferred: “Among the 132 grid states for which the declared action space contains at least one physically valid configuration, the capability-blind nominal selector chooses an unsupported action in 114 cases (86.36%) despite the existence of a valid alternative.”

Allowed secondary statistic: “Over the complete boundary-stressing grid, omitting deterministic physical-feasibility filtering caused 220 of 238 nominal selections to violate the selected profile's FMCW support.”

Forbidden: “92.44% of real vehicular ISAC decisions are physically invalid without our method.”

Allowed: “The physics gate eliminates physically invalid selected actions by construction under the implemented FMCW support model.”

Forbidden: “The physics gate guarantees real-world automotive reliability.”

Allowed: “The contribution is the explicit use of standard waveform capability relations as a hard feasibility layer preceding finite-action PC-FMCW configuration selection, together with a controlled ablation that isolates the resulting selection failure when this layer is omitted.”

Forbidden: “The standard FMCW range or unambiguous-velocity equations are novel.”

Allowed: “The 114/132 result demonstrates a recoverable configuration-selection failure on the declared boundary-aware grid: a valid action exists, but capability-blind ranking selects an unsupported one.”

Forbidden: “All ungated ISAC controllers will select invalid waveforms.”

## Explicitly excluded

- No claim of RF hardware measurement.
- No claim that the composite high-mobility profile is a commercial TI preset.
- No claim of standards compliance.
- No claim of vehicle-level trajectory prediction, planning, packet scheduling, beam management, or illumination control.
- No claim that the pilot run or Paper 1 gate ablation is the frozen large-seed publication benchmark.
- No claim of universal reliability or field deployment.
- No claim that phase coding, DBPSK, FMCW range--Doppler processing, or robust optimization is novel in itself.
- No interpretation of the boundary-aware grid as an empirical driving-state distribution.

## Paper separation rule

Paper 1 establishes the physical configuration problem and deterministic capability gate. The finite-sample Wilson qualification, policy abstention under uncertainty, paired-policy benchmark, and reliability--availability--computation trade-off belong to the separate Paper 2 evidence story.
