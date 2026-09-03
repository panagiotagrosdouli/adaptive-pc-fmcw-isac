# Optional Predictive RL Extension

This extension is intentionally **not** part of the core submission gate.

Only begin after the Stage 06 heuristic scheduler matrix and Stage 07 core statistics are frozen.

## Scientific question

Does predicted future link state improve a learned scheduler when compared with an otherwise identical current-state RL policy?

## Minimum design

- DQN-current vs DQN-predictive;
- PPO-current vs PPO-predictive;
- fixed-dimensional masked multi-user state;
- discrete receiver-selection action;
- timely-delivery/deadline-aware reward;
- training/development scenes only for RL fitting and tuning;
- one frozen official-validation evaluation;
- same traffic/link realization for paired current-vs-predictive comparisons.

## Acceptance gate

RL is worth including only if it adds interpretable evidence beyond the strong heuristic baseline. A null or negative result is still useful if it supports the conclusion that the value lies in predictive information rather than policy complexity.
