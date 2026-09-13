# Excluded or Unverified Claims

The submission branch intentionally excludes the following claims unless new evidence is added and validated:

1. **Universal B4 superiority.** The frozen paired unconditional B4-B3 effect is negative.
2. **RF or automotive hardware validation of the adaptive controller.** Current controller evidence is simulation/analytical.
3. **Embedded real-time operation or ECU certification.** Runtime evidence is host/Python timing.
4. **Global Pareto optimality.** Existing Pareto evidence is empirical over realized evaluated operating points.
5. **Arbitrary model-mismatch or distributional robustness.** Robustness is limited to declared evaluated families/slices.
6. **Independent PER measurement.** A packet-level PER claim requires an explicit packet model not currently part of the primary receiver evidence.
7. **Commercial validity of the composite high-mobility profile.** It is a simulation capability reference, not a claimed commercial preset.
8. **Field prevalence.** Fixed scenario/seed probabilities are protocol-specific and are not estimates of real-world traffic prevalence.
9. **High-draw Monte Carlo as physical truth.** A high-draw reference reduces Monte Carlo decision noise but is still model-based.

Any future inclusion of these statements requires a new evidence class, explicit provenance, and corresponding reproducibility artifacts.
