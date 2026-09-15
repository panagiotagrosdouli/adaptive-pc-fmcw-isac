from __future__ import annotations
import importlib.util
from pathlib import Path
import numpy as np

P = Path(__file__).with_name("audit_corpus.py")
S = importlib.util.spec_from_file_location("stage01_audit", P); assert S and S.loader
M = importlib.util.module_from_spec(S); S.loader.exec_module(M); audit = M.audit

def artifact(path, corrupt=False):
    n = 2
    future = np.ones((n,80,2), np.float32)
    sdc = np.full((n,80,2), .25, np.float32)
    rel = future - sdc
    if corrupt: rel[0,0,0] += 1
    np.savez(path, history_xy=np.zeros((n,11,2),np.float32), history_vxy=np.zeros((n,11,2),np.float32), future_xy=future, future_relative_xy=rel, sdc_future_xy=sdc, history_valid=np.ones((n,11),bool), future_valid=np.ones((n,80),bool), scenario_id=np.array(["s1","s2"]), track_id=np.array([1,2]), sdc_track_id=np.array([9,9]), split=np.array(["official_validation"]*n))

def test_valid_contract(tmp_path):
    p=tmp_path/"x.npz"; artifact(p); r=audit(p,"official_validation"); assert r["passed"] and r["sample_count"]==2

def test_geometry_identity_fails_closed(tmp_path):
    p=tmp_path/"x.npz"; artifact(p,True); r=audit(p,"official_validation"); assert not r["passed"]; assert any("geometry" in e for e in r["errors"])

def test_wrong_split_fails_closed(tmp_path):
    p=tmp_path/"x.npz"; artifact(p); r=audit(p,"training"); assert not r["passed"]
