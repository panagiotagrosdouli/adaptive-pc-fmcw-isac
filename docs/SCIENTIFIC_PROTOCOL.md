# Scientific Protocol

## Scope

The study evaluates robust adaptive PC-FMCW ISAC at PHY/link level under controlled vehicular conditions. No external driving dataset is required.

The same transmitted PC-FMCW waveform supports two physically different paths: a one-way V2V communications link and a monostatic two-way sensing echo. Their delay, Doppler and link budgets are never conflated.

## Evidence hierarchy

Every numerical quantity must be labelled as one of:

1. **source-derived hardware/profile constant** — traceable to a cited external source;
2. **analytically derived quantity** — computed from source-derived constants and an explicit equation;
3. **controlled simulation variable** — intentionally swept, not claimed as measured;
4. **simulation result** — produced by the reproducible code and seed set;
5. **external measured value** — quoted from a cited experiment and never presented as a measurement by this repository.

No result may move upward in this hierarchy by wording alone.

## Primary hypothesis

A robust joint policy can reduce unnecessary PHY resource use relative to a conservative fixed configuration while maintaining a predeclared joint communication-and-sensing reliability target under imperfect state knowledge.

## Secondary questions

1. When does communication-only adaptation damage sensing QoS?
2. When does sensing-only adaptation waste communication resources?
3. How large is the robustness cost of imperfect SNR/Doppler/interference/synchronization knowledge?
4. Which impairment dominates loss of joint feasibility in each operating regime?
5. How close can the deployable robust policy approach a perfect-state oracle?
6. Where is the joint QoS problem infeasible for the available PC-FMCW configuration set?
7. When is a short-range parking-style chirp profile physically incompatible with high vehicular radial velocity?
8. Can profile selection recover feasibility without excessive communication or sensing resource cost?

## Grounded profiles

The formal evaluation uses at least two declared operating profiles.

- **P-SR:** literature-grounded 77-GHz short-range parking profile using the TI automated-parking chirp example.
- **P-HM:** literature-grounded high-mobility capability profile built from TI high-speed chirp guidance and current 77-GHz hardware ADC/RF capability. It is a composite capability reference, not a claimed commercial preset.

A published 77-GHz JCRS example at 20.28 m and 5.1 kHz one-way Doppler is used only as an external scale cross-check because its waveform is PMCW-CDMA rather than PC-FMCW.

## Physical validation gates

Before adaptation claims:

- the sensing model must use dechirped IF sampling at the hardware ADC rate;
- range resolution, unambiguous range, velocity resolution and unambiguous velocity must match analytical expressions;
- the communication DBPSK chain must match the analytical AWGN BER reference when residual frequency error is zero;
- one-way communication Doppler and two-way monostatic Doppler must be tested independently;
- profile-specific failure outside the unambiguous region must be treated as a physical limitation, not an algorithm failure.

## Policies

B0 Fixed PHY; B1 communication-only; B2 sensing-only; B3 joint deterministic; B4 robust joint; Oracle perfect-state bound.

The action codebook and resource-cost definition are frozen before the formal policy run.

## Predeclared experiment blocks

E0 provenance/capability sanity.
E1 waveform and IF sanity.
E2 communication AWGN/theory validation.
E3 sensing range-Doppler validation.
E4 mobility and residual synchronization stress.
E5 phase-noise/synchronization model sensitivity.
E6 mutual interference.
E7 fixed and nominal adaptation baselines.
E8 proposed robust chance-constrained adaptation.
E9 joint reliability/feasibility maps.
E10 communication-sensing-resource Pareto analysis.
E11 ablations and model mismatch.
E12 statistics, runtime and reproduction bundle.

## Statistical protocol

Use common random numbers for paired policy comparisons whenever policies operate on the same state draw. Report means, medians where informative, 95% bootstrap confidence intervals, paired effect estimates, joint-constraint violation probability and per-regime results. The seed list, configuration hash, source commit and software environment must be archived. No threshold or codebook may be changed after inspecting frozen formal results.

Pilot experiments may be used to debug the implementation and identify numerically useful plotting ranges, but their values must not be copied into the formal frozen results unless the protocol explicitly predeclared them.

## Claim boundaries

This repository is a model-based reproducible research study, not a new RF measurement campaign. Source-derived hardware constants are real external specifications; simulation outputs remain simulations. External measurements are cited as external validation/context only. Unsupported phase-noise, blockage, RCS, antenna-gain or interference distributions must be labelled assumptions or controlled sensitivity variables until traceable models are added.
