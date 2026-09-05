import importlib.util
from pathlib import Path


def _load_module():
    path = Path(__file__).resolve().parents[1] / "scripts" / "generate_supplemental_v2_1_figures.py"
    spec = importlib.util.spec_from_file_location("supplemental_v2_1_figures", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_uncertainty_story_matches_successful_artifact_snapshot():
    m = _load_module()
    assert m.UNCERTAINTY[1.0]["b3_cond"] == 0.8738738739
    assert m.UNCERTAINTY[1.0]["b4_cond"] == 1.0
    assert m.UNCERTAINTY[3.0]["b4_sel"] == 0.0591666667
    assert m.UNCERTAINTY[3.0]["b4_cond"] == 0.9859154930


def test_ablation_snapshot_retains_negative_results():
    m = _load_module()
    assert m.ABLATIONS["NO_PHYSICS_GATE"][1] == 0.0
    assert m.ABLATIONS["NO_STATE_UNCERTAINTY"][1] < 1.0
    assert m.ABLATIONS["NO_JOINT_CONSTRAINT"][0] > m.ABLATIONS["FULL_B4"][0]


def test_runtime_snapshot_does_not_support_512_draw_real_time_claim():
    m = _load_module()
    b3_ms, b4_ms = m.RUNTIME_MS[512]
    assert b3_ms < 1.0
    assert b4_ms > 200.0


def test_physics_limits_preserve_profile_separation():
    m = _load_module()
    assert m.PARKING_RMAX < m.MOBILE_RMAX
    assert m.PARKING_VMAX < m.MOBILE_VMAX
