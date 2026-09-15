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
- On the declared 238-state boundary-aware capability grid, the ungated nominal selector selects in all 238 states and 220 selections (92.44%) violate the selected profile's deterministic FMCW range/velocity support; this is a stress-grid result, not a field prevalence estimate.
- On the same grid, the gated selector selects in 132 physically supportable states and makes zero physically invalid selections by construction under the implemented physical model.
- In 114 grid states the ungated selector chooses an invalid action while gating exposes a valid alternative from the same 54-action set.

## New gate-ablation wording boundaries

Allowed: “Under the evaluated configuration space and boundary-aware operating grid, omitting deterministic physical-feasibility filtering caused 220 of 238 nominal selections to violate the selected profile's FMCW support.”

Forbidden: “92.44% of real vehicular ISAC decisions are physically invalid without our method.”

Allowed: “The physics gate eliminates physically invalid selected actions by construction under the implemented FMCW support model.”

Forbidden: “The physics gate guarantees real-world automotive reliability.”

Allowed: “The contribution is the explicit use of standard waveform capability relations as a hard feasibility layer preceding finite-action PC-FMCW configuration selection.”

Forbidden: “The standard FMCW range or unambiguous-velocity equations are novel.”

## Explicitly excluded

- No claim of RF hardware measurement.
- No claim that the composite high-mobility profile is a commercial TI preset.
- No claim of standards compliance.
- No claim of vehicle-level trajectory prediction, planning, packet scheduling, beam management, or illumination control.
- No claim that the pilot run or Paper 1 gate ablation is the frozen large-seed publication benchmark.
- No claim of universal reliability or field deployment.
- No claim that phase coding, DBPSK, FMCW range--Doppler processing, or robust optimization is novel in itself.

## Paper separation rule

Paper 1 establishes the physical configuration problem and deterministic capability gate. The finite-sample Wilson qualification, policy abstention under uncertainty, paired-policy benchmark, and reliability--availability--computation trade-off belong to the separate Paper 2 evidence story.
