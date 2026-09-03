import numpy as np
from evaluate_predictors import trajectory_metrics, range_bearing, angular_error


def test_zero_trajectory_error():
    y=np.arange(20,dtype=float).reshape(10,2)
    assert trajectory_metrics(y,y)==(0.0,0.0)


def test_constant_offset_metrics():
    y=np.zeros((5,2)); yh=y+np.array([3.,4.])
    ade,fde=trajectory_metrics(yh,y)
    assert ade==5.0 and fde==5.0


def test_range_bearing():
    r,b=range_bearing(np.array([[3.,4.],[1.,0.]]))
    np.testing.assert_allclose(r,[5.,1.]); np.testing.assert_allclose(b,[np.arctan2(4,3),0])


def test_wrapped_angular_error():
    a=np.deg2rad(np.array([179.])); b=np.deg2rad(np.array([-179.]))
    np.testing.assert_allclose(np.rad2deg(angular_error(a,b)),[2.],atol=1e-10)
