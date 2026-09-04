import importlib.util
import sys
from pathlib import Path

import numpy as np

P = Path(__file__).with_name("link_model.py")
spec = importlib.util.spec_from_file_location("link_model", P)
m = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = m
spec.loader.exec_module(m)


def lut():
    return m.BerLut(np.array([-20., -10., 0., 10., 20.]), np.array([.5, .2, .02, 1e-4, 1e-6]))


def test_snr_decreases_with_range():
    cfg = m.LinkConfig()
    snr, _ = m.snr_from_geometry(np.array([20., 40., 80.]), 0., cfg)
    assert np.all(np.diff(snr) < 0)


def test_pointing_error_reduces_snr_and_fov_is_hard_gate():
    cfg = m.LinkConfig()
    snr, fov = m.snr_from_geometry(20., np.array([0., 4., 13.]), cfg)
    assert snr[0] > snr[1]
    assert fov.tolist() == [True, True, False]
    assert np.isneginf(snr[2])


def test_link_state_bounds_and_outage():
    state = m.link_state(np.array([20., 20.]), np.array([0., 20.]), lut(), m.LinkConfig())
    assert np.all((state["ber"] >= 0) & (state["ber"] <= 1))
    assert np.all((state["per"] >= 0) & (state["per"] <= 1))
    assert np.all((state["goodput_bps"] >= 0) & (state["goodput_bps"] <= 1e9))
    assert bool(state["outage"][1])


def test_link_lifetime_is_first_outage():
    assert m.usable_link_lifetime_s([False, False, True, True], 0.1) == 0.2
    assert m.usable_link_lifetime_s([False] * 5, 0.1) == 0.5
