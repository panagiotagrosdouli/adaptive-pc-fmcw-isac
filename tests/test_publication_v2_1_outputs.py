import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "artifacts" / "publication" / "v2_1"


def test_policy_summary_matches_frozen_json():
    final = json.loads((EVIDENCE / "FINAL_RESULTS.json").read_text())
    rows = list(csv.DictReader((EVIDENCE / "tables" / "policy_summary.csv").open()))
    assert len(rows) == len(final["aggregate"]) == 6
    by_policy = {r["policy"]: r for r in rows}
    for policy, metrics in final["aggregate"].items():
        row = by_policy[policy]
        assert float(row["selection_rate"]) == metrics["selection_rate"]
        assert float(row["joint_qos_unconditional"]) == metrics["joint_qos_probability_unconditional"]
        assert float(row["joint_qos_conditional"]) == metrics["joint_qos_probability_conditional_on_selection"]


def test_paired_table_retains_negative_result():
    final = json.loads((EVIDENCE / "FINAL_RESULTS.json").read_text())
    b4_b3 = final["paired_B4_minus_B3_joint_qos"]
    assert b4_b3["mean_paired_difference"] < 0
    assert b4_b3["ci_high"] < 0
    assert final["sanity_gate"]["b4_superiority_over_b3_supported"] is False


def test_e11_snapshot_matches_frozen_summary():
    source = json.loads((EVIDENCE / "E9_E11_RESULTS.json").read_text())["e11"]
    rows = list(csv.DictReader((EVIDENCE / "tables" / "e11_ablation.csv").open()))
    by_name = {r["ablation"]: r for r in rows}
    for name in ["FULL_B4", "NO_STATE_UNCERTAINTY", "NO_CFO", "NO_INTERFERENCE"]:
        assert float(by_name[name]["selection_rate"]) == source[name]["selection_rate"]
        assert float(by_name[name]["joint_qos_rate_unconditional"]) == source[name]["joint_qos_rate_unconditional"]
