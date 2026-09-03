import importlib.util
from pathlib import Path
import numpy as np
P=Path(__file__).with_name("calibration.py"); s=importlib.util.spec_from_file_location("cal",P); cal=importlib.util.module_from_spec(s); assert s.loader; s.loader.exec_module(cal)
def test_variance_mle_per_horizon():
 r=np.ones((4,80,2),float)*2; v=cal.fit_isotropic_variance(r); assert v.shape==(80,); assert np.allclose(v,4.)
def test_nll_finite_and_coverage_bounded():
 rng=np.random.default_rng(7); r=rng.normal(size=(1000,80,2)); v=cal.fit_isotropic_variance(r); assert np.isfinite(cal.gaussian_nll(r,v)); c=cal.coverage(r,v); assert set(c)=={"50","90","95"}; assert all(0<=x<=1 for x in c.values())
def test_chi2_df2_quantile_is_monotone(): assert cal.chi2_df2_quantile(.5)<cal.chi2_df2_quantile(.9)<cal.chi2_df2_quantile(.95)
