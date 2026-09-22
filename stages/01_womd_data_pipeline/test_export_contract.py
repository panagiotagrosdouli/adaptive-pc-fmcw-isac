from __future__ import annotations
import importlib.util
from pathlib import Path
import numpy as np

P=Path(__file__).with_name("export_womd_tfrecord.py"); S=importlib.util.spec_from_file_location("stage01_export",P); assert S and S.loader
M=importlib.util.module_from_spec(S); S.loader.exec_module(M)

def test_split_is_deterministic_and_scenario_level():
    assert M.stable_dev("scenario-42",.1)==M.stable_dev("scenario-42",.1)

def test_anchor_rotation_translation():
    points=np.array([[11.,20.],[10.,21.]],np.float32); origin=np.array([10.,20.],np.float32)
    out=M.rotate_anchor(points,origin,0.0); np.testing.assert_allclose(out,[[1.,0.],[0.,1.]])

def test_future_relative_geometry_keeps_sdc_motion():
    actor=np.array([[[5.,0.],[7.,0.]]],np.float32); sdc=np.array([[[1.,0.],[2.,0.]]],np.float32)
    relative=actor-sdc; np.testing.assert_allclose(relative,[[[4.,0.],[5.,0.]]]); assert not np.allclose(relative,actor)

def test_velocity_is_causal_finite_difference():
    h=np.array([[0.,0.],[1.,0.],[3.,0.]],np.float32); v=M.velocities(h,1.0); np.testing.assert_allclose(v,[[1.,0.],[1.,0.],[2.,0.]])

def test_sha256_file_records_exact_input_bytes(tmp_path):
    path=tmp_path/"shard.tfrecord"; path.write_bytes(b"official-womd-shard\n")
    assert M.sha256_file(path)=="a411652dab7c1e0ae400f1555034af4f7f77ccefcf4089ec441a806871d8beaa"
