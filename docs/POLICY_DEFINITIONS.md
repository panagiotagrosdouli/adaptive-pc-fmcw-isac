# Policy Definitions

Frozen baseline: `3904c4c2a69c4af96751d64614f7228ddea24b56`.

## B0_FIXED
Uses one frozen PHY configuration across operating states. It serves as a non-adaptive deployable baseline. Selection can fail when the fixed action is not admissible under the relevant gate/receiver evaluation.

## B1_COMM_ONLY
Adaptive communication-only selector. It minimizes declared resource cost subject to communication-side requirements. It does not enforce the full joint sensing/communication QoS objective.

## B2_SENSING_ONLY
Adaptive sensing-only selector. It minimizes declared resource cost subject to sensing-side requirements. It does not enforce the full joint communication requirement.

## B3_DETERMINISTIC_JOINT
Joint communication+sensing selector evaluated at the estimated state as if that estimate were exact. It enforces joint deterministic QoS but does not perform B4's uncertainty-draw confidence qualification.

## B4_ROBUST_JOINT
Proposed physics-gated robust selector. Candidate actions must first pass deterministic physical feasibility. For each surviving action, uncertainty realizations are evaluated against the joint QoS event. The action is admissible only when its one-sided Wilson lower confidence bound meets the frozen reliability target; among admissible candidates, the declared minimum-resource action is selected. If no candidate qualifies, B4 abstains.

## ORACLE
Non-deployable hindsight reference using true receiver-level state/information to identify the minimum declared resource-cost successful action. It is an evaluation bound/reference and must not be described as a deployable policy.

## Reporting rule

For every policy report selection/abstention separately from conditional and unconditional joint QoS. Conditional reliability describes selected decisions; unconditional joint QoS additionally penalizes abstention and therefore reflects service availability under the frozen scenario bank.
