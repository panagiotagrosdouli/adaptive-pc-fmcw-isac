"""Tiny domain integration test; not a statistical validation."""
from pathlib import Path
from runpy import run_path

run = run_path(str(Path(__file__).resolve().parents[1] / "scripts" /
                   "run_pc_fmcw_research_pilot.py"))["run"]

def test_receiver_level_pilot_has_disjoint_splits_and_consistent_denominators():
    result = run(seed=721, cases_per_split=2, draws=8,
                 comm_bits=256, sensing_trials=1)
    assert result["evidence"] == "PC_FMCW_RECEIVER_PILOT_NOT_FINAL"
    for label in ("B3", "B4", "B3_CAL"):
        r = result["held_out"][label]
        assert r["total_states"] == 2
        assert 0 <= r["selected_successes"] <= r["selected"] <= 2
        assert 0 <= r["coverage"] <= 1
    assert result["calibration"]["n_candidate_states"] <= 2
