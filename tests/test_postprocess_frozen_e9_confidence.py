import importlib.util
from pathlib import Path


def _load_module():
    path = Path(__file__).resolve().parents[1] / "scripts" / "postprocess_frozen_e9_confidence.py"
    spec = importlib.util.spec_from_file_location("postprocess_frozen_e9_confidence", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


post = _load_module()


def _payload(probability=1.0, selection=1.0, raw=True):
    return {
        "evidence_class": post.EXPECTED_EVIDENCE_CLASS,
        "protocol_id": post.EXPECTED_PROTOCOL,
        "e9": {
            "slice": {
                "axis_x": "x",
                "axis_y": "y",
                "policy": "B4_ROBUST_JOINT",
                "cells": [{
                    "x": 1.0,
                    "y": 2.0,
                    "joint_qos_probability": probability,
                    "selection_rate": selection,
                    "empirically_meets_declared_target": raw,
                }],
            }
        },
    }


def test_twenty_of_twenty_cannot_confidence_qualify_point95_target():
    out = post.qualify_e9(_payload(), trials_per_cell=20, target=0.95, confidence=0.95)
    assert out["raw_empirical_target_cells"] == 1
    assert out["confidence_qualified_target_cells"] == 0
    assert not out["target_statistically_attainable_at_trials_per_cell"]
    cell = out["slices"]["slice"]["cells"][0]
    assert cell["joint_qos_successes_reconstructed"] == 20
    assert cell["selections_reconstructed"] == 20
    assert cell["wilson_lower"] < 0.95


def test_probability_must_match_integer_count_for_declared_trials():
    try:
        post.qualify_e9(_payload(probability=0.333), trials_per_cell=20)
    except ValueError as exc:
        assert "incompatible with integer count" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_larger_sample_can_confidence_qualify_all_successes():
    out = post.qualify_e9(_payload(), trials_per_cell=100, target=0.95, confidence=0.95)
    assert out["target_statistically_attainable_at_trials_per_cell"]
    assert out["confidence_qualified_target_cells"] == 1
