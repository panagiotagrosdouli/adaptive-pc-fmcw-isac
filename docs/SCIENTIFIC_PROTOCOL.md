# Scientific Protocol

## Scope

The study evaluates robust adaptive PC-FMCW ISAC at PHY/link level under controlled vehicular conditions. No external dataset is required.

## Primary hypothesis

A robust joint policy can reduce unnecessary PHY resource use relative to a conservative fixed configuration while maintaining a predeclared joint communication-and-sensing reliability target under imperfect state knowledge.

## Secondary questions

1. When does communication-only adaptation damage sensing QoS?
2. When does sensing-only adaptation waste communication resources?
3. How large is the robustness cost of imperfect SNR/Doppler/interference/CFO knowledge?
4. Which impairment dominates loss of joint feasibility in each operating regime?
5. How close can the deployable robust policy approach a perfect-state oracle?
6. Where is the joint QoS problem infeasible for the available PC-FMCW configuration set?

## Policies

B0 Fixed PHY; B1 communication-only; B2 sensing-only; B3 joint deterministic; B4 robust joint; Oracle perfect-state bound.

## Predeclared experiment blocks

E1 clean AWGN/SNR sanity sweep.
E2 SNR x Doppler feasibility map.
E3 interference robustness sweep.
E4 CFO/synchronization sweep.
E5 phase-noise sweep.
E6 state-estimation uncertainty sweep.
E7 communication reliability target sweep.
E8 sensing accuracy target sweep.
E9 joint communication-sensing-resource Pareto frontier.
E10 configuration-variable ablation.
E11 oracle-gap analysis.
E12 computational complexity/runtime analysis.

## Statistical protocol

Use common random numbers for paired policy comparisons. Report means plus 95% bootstrap confidence intervals, paired effect estimates, failure probabilities and per-regime results. The Monte-Carlo seed list and configuration hash must be archived. No threshold may be changed after inspecting the frozen formal results.

## Claim boundaries

The initial repository provides an auditable analytical/surrogate PC-FMCW model for software and protocol development. Before publication-level physical claims, each communication and sensing equation must be traced to theory, Part-A evidence, or a validated waveform/receiver simulation. Unsupported model assumptions must be labelled as assumptions. No simulated quantity may be called a measurement.
