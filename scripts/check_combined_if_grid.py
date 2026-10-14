"""Post-freeze independent boundary-grid census.

This supplementary diagnostic does not replace the historical Paper 1 or
publication-v2.1 experiment and must not be silently treated as its result.
Run with: python scripts/check_combined_if_grid.py
"""
from pcfmcw_isac.paper1_physics_gate_ablation import RANGE_GRID_M, VELOCITY_GRID_MPS
from pcfmcw_isac.if_feasibility_diagnostic import diagnose_if
from pcfmcw_isac.policy_evaluation import profile_registry

def main():
    profiles = profile_registry()
    baseline = joint = divergence = 0
    rows = []
    for r in RANGE_GRID_M:
        for v in VELOCITY_GRID_MPS:
            tests = {name: diagnose_if(profile, r, v) for name, profile in profiles.items()}
            old_ok = any(x.canonical_gate_supported for x in tests.values())
            new_ok = any(x.canonical_gate_supported and x.sampled_if_supported for x in tests.values())
            baseline += old_ok
            joint += new_ok
            if old_ok != new_ok:
                divergence += 1
                rows.append((r, v))
    print("Historical independent-bound census:",baseline)
    print("Coupled-beat supplementary census:",joint)
    print("Previously supported states removed by joint criterion:",divergence)
    print("Changed grid states:",rows)
    assert baseline == 132, "Existing historical grid is no longer reproducible"
    assert joint == 127, "Investigate revised IF convention or profile model"
    assert divergence == 5

if __name__ == "__main__":
    main()
