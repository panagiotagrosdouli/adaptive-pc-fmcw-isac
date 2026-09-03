import importlib.util
from pathlib import Path
import sys

import numpy as np

HERE = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


data = load("data")


def test_normalization_uses_training_only(tmp_path):
    p = tmp_path / "d.npz"
    h = np.zeros((2, 11, 2), np.float32)
    v = np.zeros_like(h)
    h[1] = 100
    v[1] = 100
    np.savez_compressed(p, history_xy=h, history_vxy=v, split=np.array(["training", "development"]))
    n = data.fit_training_normalization(p)
    assert np.allclose(n.mean, 0)


def test_canonical_input_is_four_dimensional():
    x = data.canonical_input(np.zeros((3, 11, 2)), np.ones((3, 11, 2)))
    assert x.shape == (3, 11, 4)
