import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("stage05_aggregate", HERE / "aggregate_official_evaluation.py")
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MOD)


def row(scenario="s1", predictor="CV", **extra):
    value = {"scenario_id": scenario, "predictor": predictor, "split": "official_validation", "actor_samples": "2"}
    value.update({metric: "1.0" for metric in MOD.METRICS})
    value.update(extra)
    return value


def test_validation_rejects_split_leakage():
    errors = MOD.validate([row(split="development")], [11], False)
    assert any("official_validation" in error for error in errors)


def test_validation_rejects_nonfinite_metric():
    errors = MOD.validate([row(ade_m="nan")], [11], False)
    assert any("non-finite" in error for error in errors)


def test_undefined_metric_needs_support():
    candidate = row(ade_m="", actor_samples="")
    errors = MOD.validate([candidate], [11], False)
    assert any("explicit support" in error for error in errors)


def test_archive_matrix_is_checked():
    rows = [row(predictor="GRU-Traj", objective="trajectory", seed="11")]
    errors = MOD.validate(rows, [11], True)
    assert any("trajectory_plus_link" in error for error in errors)


def test_scenario_level_aggregation_and_ranking():
    rows = [row("s1", "A", ade_m="2"), row("s2", "A", ade_m="4"), row("s1", "B", ade_m="1")]
    summary, rankings = MOD.aggregate(rows)
    a = next(x for x in summary if x["predictor"] == "A")
    assert a["ade_m"] == 3.0
    assert a["unique_scenarios"] == 2
    ade = [x for x in rankings if x["metric"] == "ade_m"]
    assert ade[0]["predictor"] == "B"


def test_csv_writer_accepts_heterogeneous_metric_columns(tmp_path):
    target = tmp_path / "rows.csv"
    MOD.write_csv(target, [{"scenario_id": "a", "ade_m": 1}, {"scenario_id": "b", "nll": 2}])
    assert target.read_text().splitlines()[0] == "ade_m,nll,scenario_id"
