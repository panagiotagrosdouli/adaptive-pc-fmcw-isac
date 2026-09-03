import importlib.util
from pathlib import Path

import numpy as np

MODULE = Path(__file__).with_name("export_womd_tfrecord.py")
spec = importlib.util.spec_from_file_location("stage01_export", MODULE)
m = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(m)


def test_scenario_split_is_deterministic():
    assert m.stable_dev("scenario-123", 0.1) == m.stable_dev("scenario-123", 0.1)
    assert not m.stable_dev("scenario-123", 0.0)


def test_world_to_sdc_anchor_frame():
    pts = np.array([[11.0, 20.0], [10.0, 21.0]], dtype=np.float32)
    origin = np.array([10.0, 20.0], dtype=np.float32)
    out = m.rotate(pts, origin, 0.0)
    np.testing.assert_allclose(out, [[1.0, 0.0], [0.0, 1.0]])


def test_velocity_uses_only_history():
    h = np.stack([np.array([0.1 * i, 0.0]) for i in range(11)]).astype(np.float32)
    v = m.velocities(h)
    np.testing.assert_allclose(v[:, 0], 1.0, atol=1e-6)
    np.testing.assert_allclose(v[:, 1], 0.0, atol=1e-6)
