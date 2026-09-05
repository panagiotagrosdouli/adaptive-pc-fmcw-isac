import json
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "configs" / "paper_protocol_v2.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_v2_preserves_v1_qos_thresholds():
    cfg = _load()
    assert cfg["qos"] == {
        "ber_max": 0.001,
        "effective_rate_min_bps": 100000,
        "range_rmse_max_m": 1.0,
        "velocity_rmse_max_mps": 1.0,
        "joint_reliability_target": 0.95,
    }


def test_v2_freezes_statistical_and_oracle_semantics():
    cfg = _load()
    semantics = cfg["v2_semantics"]
    assert semantics["b4_internal_draws"] == 512
    assert semantics["b4_reliability_confidence"] == 0.95
    assert semantics["b4_action_local_rng"] is True
    assert semantics["oracle_is_deployable_policy"] is False
    assert cfg["claim_rules"]["oracle_anomaly_blocks_paper_ready_status"] is True


def test_final_design_is_paired_and_predeclared():
    cfg = _load()["paired_benchmark"]
    assert cfg["n_scenarios_per_seed"] == 12
    assert cfg["seed_start"] == 10000
    assert cfg["n_seeds_final"] == 1000
    assert cfg["paired_comparisons"] is True
    assert cfg["bootstrap_resamples"] == 10000
