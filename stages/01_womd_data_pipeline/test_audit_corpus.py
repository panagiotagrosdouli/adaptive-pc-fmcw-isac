import importlib.util
from pathlib import Path
import numpy as np
MODULE=Path(__file__).with_name("audit_corpus.py"); spec=importlib.util.spec_from_file_location("stage01_audit",MODULE); audit_module=importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(audit_module)
def corpus(path,split="official_validation",bad=False,bad_geometry=False):
 n=3; history=np.zeros((n,11,2),np.float32); future=np.ones((n,80,2),np.float32); sdc=np.full((n,80,2),.25,np.float32); rel=future-sdc
 if bad: history[0,0,0]=np.nan
 if bad_geometry: rel[0,0,0]+=1
 np.savez_compressed(path,history_xy=history,history_vxy=np.zeros((n,11,2),np.float32),future_xy=future,future_relative_xy=rel,sdc_future_xy=sdc,history_valid=np.ones((n,11),bool),future_valid=np.ones((n,80),bool),scenario_id=np.array(["a","a","b"]),track_id=np.array([1,2,3]),sdc_track_id=np.array([9,9,10]),split=np.array([split]*n))
def test_valid_official_corpus_passes(tmp_path):
 p=tmp_path/"official.npz"; corpus(p); r=audit_module.audit(p,"official_validation"); assert r["passed"] and r["true_sdc_future_geometry"] and r["sample_count"]==3 and r["scenario_count"]==2
def test_internal_development_cannot_pose_as_official(tmp_path):
 p=tmp_path/"dev.npz"; corpus(p,"development"); assert not audit_module.audit(p,"official_validation")["passed"]
def test_nonfinite_trajectory_fails(tmp_path):
 p=tmp_path/"bad.npz"; corpus(p,bad=True); r=audit_module.audit(p); assert not r["passed"] and not r["finite_numeric_arrays"]
def test_inconsistent_future_sdc_geometry_fails(tmp_path):
 p=tmp_path/"geometry.npz"; corpus(p,bad_geometry=True); r=audit_module.audit(p); assert not r["passed"] and not r["true_sdc_future_geometry"]
