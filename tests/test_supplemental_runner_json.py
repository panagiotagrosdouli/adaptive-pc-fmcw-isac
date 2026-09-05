import importlib.util
import json
from pathlib import Path


def _load_runner_module():
    path = Path(__file__).resolve().parents[1] / "scripts" / "run_supplemental_v2_1.py"
    spec = importlib.util.spec_from_file_location("run_supplemental_v2_1", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_json_safe_converts_nested_nonfinite_values_to_null():
    runner = _load_runner_module()
    payload = {
        "finite": 1.25,
        "nested": [float("inf"), {"negative": float("-inf"), "nan": float("nan")}],
    }
    safe = runner._json_safe(payload)
    assert safe == {
        "finite": 1.25,
        "nested": [None, {"negative": None, "nan": None}],
    }
    encoded = json.dumps(safe, allow_nan=False)
    assert "Infinity" not in encoded
    assert "NaN" not in encoded
    assert "null" in encoded
