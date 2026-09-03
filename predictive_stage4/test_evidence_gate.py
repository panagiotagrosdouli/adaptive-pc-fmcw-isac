import importlib.util
from pathlib import Path
import sys

import numpy as np

HERE = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(f"test_stage4_{name}", HERE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


data = load("data")
surrogates = load("surrogates")
evaluator = load("evaluate_checkpoint")


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


def test_surrogates_load_frozen_stage2_config():
    cfg = surrogates.load_surrogate_config(HERE.parent / "predictive_stage2" / "link_model_config.json")
    assert cfg["reference_range_m"] == 20.0
    assert cfg["fov_half_angle_deg"] == 12.0


def test_binary_outage_f1_is_pooled_over_steps():
    truth = np.array([0, 1, 1, 0], dtype=bool)
    pred = np.array([0, 1, 0, 1], dtype=bool)
    assert evaluator.binary_f1(truth, pred) == 0.5


def test_binary_auroc_handles_ties_exactly():
    truth = np.array([0, 1, 0, 1], dtype=bool)
    score = np.array([0.1, 0.8, 0.8, 0.9])
    assert np.isclose(evaluator.binary_auroc(truth, score), 0.875)


def test_binary_auroc_returns_none_for_one_class():
    assert evaluator.binary_auroc(np.ones(4, dtype=bool), np.arange(4.0)) is None
