"""Small deterministic checks for supplemental clustered-bootstrap semantics."""
import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/seed_clustered_bootstrap.py"
spec = importlib.util.spec_from_file_location("cluster_bootstrap", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def _records():
    records = []
    for seed, diffs in [(10, [1, 1, 1]), (11, [-1, -1, -1]), (12, [1, 1, 1])]:
        for scenario, diff in enumerate(diffs):
            records.append({"state": {"seed": seed}, "scenario_id": scenario,
                            "policy": "A", "joint_qos": int(diff == 1)})
            records.append({"state": {"seed": seed}, "scenario_id": scenario,
                            "policy": "B", "joint_qos": int(diff == -1)})
    return records


def test_clustered_bootstrap_is_paired_and_deterministic():
    kwargs = dict(policy_a="A", policy_b="B", n_resamples=500, seed=42)
    first = module.seed_clustered_paired_bootstrap(_records(), **kwargs)
    second = module.seed_clustered_paired_bootstrap(_records(), **kwargs)
    assert first == second
    assert first["n_clusters"] == 3
    assert first["n_pairs"] == 9
    assert first["mean_paired_difference"] == pytest.approx(1 / 3)
    assert first["ci_low"] <= first["mean_paired_difference"] <= first["ci_high"]


def test_clustered_bootstrap_rejects_incomplete_pairs():
    records = _records()
    records.pop()
    with pytest.raises(ValueError, match="missing policy"):
        module.seed_clustered_paired_bootstrap(records, "A", "B")


def test_clustered_bootstrap_rejects_duplicate_pairs():
    records = _records()
    records.append(records[0].copy())
    with pytest.raises(ValueError, match="duplicate"):
        module.seed_clustered_paired_bootstrap(records, "A", "B")
